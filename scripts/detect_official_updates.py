from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REGISTRY_FILE = DATA / "source_registry.json"
STATE_FILE = DATA / "official_state.json"
QUEUE_FILE = DATA / "content_queue.json"
LATEST_FILE = DATA / "latest.json"
TZ = ZoneInfo("Asia/Tokyo")
NOW = datetime.now(TZ)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TCGLOGBot/1.0; +https://tcglog.jp)"
}


@dataclass
class Source:
    id: str
    name: str
    category: str
    official_home: str
    list_url: str
    item_selector: str
    title_selector: str | None
    url_attr: str
    summary_selector: str | None
    limit: int = 5


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text)).strip()


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "update"


def fetch_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    return response.text


def parse_updates(source: Source) -> list[dict[str, str]]:
    if not source.list_url.startswith("http"):
        return []
    html = fetch_html(source.list_url)
    soup = BeautifulSoup(html, "html.parser")
    nodes = soup.select(source.item_selector)
    updates: list[dict[str, str]] = []
    for node in nodes[: source.limit]:
        title_node = node.select_one(source.title_selector) if source.title_selector else node
        title = clean_text(title_node.get_text(" ", strip=True)) if title_node else ""
        if not title:
            continue
        href = node.get(source.url_attr) or (title_node.get(source.url_attr) if title_node else None)
        if not href:
            continue
        url = urljoin(source.list_url, href)
        summary = ""
        if source.summary_selector:
            summary_node = node.select_one(source.summary_selector)
            if summary_node:
                summary = clean_text(summary_node.get_text(" ", strip=True))
        updates.append({"title": title, "url": url, "summary": summary})
    return updates


def build_entry(source: Source, item: dict[str, str]) -> dict[str, Any]:
    timestamp = NOW.strftime("%Y-%m-%dT%H:%M:%S%z")
    compact_time = NOW.strftime("%Y%m%d-%H%M")
    title = f"【公式更新】{source.name} 最新情報を確認 | {NOW.strftime('%-m/%-d %H:%M')}"
    description = item["summary"] or f"{source.name} の公式更新を検知しました。最新タイトルは「{item['title']}」です。"
    return {
        "type": "genre",
        "slug": f"{source.id}-{compact_time}-{slugify(item['title'])[:40]}",
        "title": title,
        "description": description[:140],
        "category": source.category,
        "genre": source.id,
        "publishedAt": timestamp,
        "heroLabel": "公式更新",
        "eyecatch": "OFFICIAL UPDATE",
        "sourceLabel": f"{source.name} 公式サイト",
        "tags": ["公式", "更新検知", source.category],
        "highlights": [
            f"検知対象: {source.name}",
            f"最新タイトル: {item['title']}",
            f"参照URL: {item['url']}"
        ],
        "sections": [
            {
                "heading": "今回の更新",
                "paragraphs": [
                    f"{source.name} の公式ページで新しい更新を検知しました。",
                    f"確認できた最新タイトルは「{item['title']}」です。",
                    item["summary"] or "要約文は未取得のため、元ページを直接確認してください。"
                ]
            },
            {
                "heading": "参照元",
                "paragraphs": [
                    f"公式一覧ページ: {source.list_url}",
                    f"更新記事URL: {item['url']}"
                ]
            }
        ],
        "sourceUrl": item["url"]
    }


def build_summary_entry(entries: list[dict[str, Any]]) -> dict[str, Any]:
    timestamp = NOW.strftime("%Y-%m-%dT%H:%M:%S%z")
    compact_time = NOW.strftime("%Y%m%d-%H%M")
    highlights = [f"{e['category']}: {e['highlights'][1].replace('最新タイトル: ', '')}" for e in entries[:5]]
    return {
        "type": "summary",
        "slug": f"summary-{compact_time}",
        "title": f"【{NOW.strftime('%H:%M')}まとめ】公式更新を自動検知したTCG最新情報",
        "description": "公式サイトの更新差分を検知して、自動でまとめた定時記事です。",
        "category": "定時まとめ",
        "genre": "summary",
        "publishedAt": timestamp,
        "heroLabel": "定時まとめ",
        "eyecatch": "AUTO SUMMARY",
        "sourceLabel": "各TCG公式サイト",
        "tags": ["公式", "自動更新", "差分検知"],
        "highlights": highlights,
        "sections": [
            {
                "heading": "検知サマリー",
                "paragraphs": [
                    f"今回の実行では {len(entries)} 件の公式更新を新規検知しました。",
                    "以下のジャンルで差分が確認できたため、個別記事も自動生成しています。"
                ]
            }
        ] + [
            {
                "heading": e["category"],
                "paragraphs": [
                    e["highlights"][1],
                    e["description"],
                    e["sourceUrl"]
                ]
            }
            for e in entries[:10]
        ]
    }


def main() -> int:
    registry = load_json(REGISTRY_FILE)
    state = load_json(STATE_FILE)
    queue = load_json(QUEUE_FILE)
    latest = load_json(LATEST_FILE)
    existing_slugs = {entry["slug"] for entry in queue.get("entries", [])}

    sources = [Source(**item) for item in registry["sources"]]
    new_entries: list[dict[str, Any]] = []
    next_state = {"lastCheckedAt": NOW.isoformat(), "sources": state.get("sources", {})}

    for source in sources:
        items = parse_updates(source)
        newest = items[0] if items else None
        prev = state.get("sources", {}).get(source.id, {})
        prev_url = prev.get("latestUrl")
        prev_title = prev.get("latestTitle")
        if newest:
            latest[source.id] = {
                "name": source.name,
                "category": source.category,
                "title": newest["title"],
                "url": newest["url"],
                "checkedAt": NOW.isoformat()
            }
            next_state["sources"][source.id] = {
                "latestTitle": newest["title"],
                "latestUrl": newest["url"],
                "checkedAt": NOW.isoformat()
            }
            if newest["url"] != prev_url or newest["title"] != prev_title:
                entry = build_entry(source, newest)
                if entry["slug"] not in existing_slugs:
                    new_entries.append(entry)

    if new_entries:
        queue.setdefault("entries", []).extend(new_entries)
        summary_entry = build_summary_entry(new_entries)
        if summary_entry["slug"] not in existing_slugs:
            queue["entries"].append(summary_entry)

    save_json(STATE_FILE, next_state)
    save_json(QUEUE_FILE, queue)
    save_json(LATEST_FILE, latest)
    print(json.dumps({"detected": len(new_entries), "checkedAt": NOW.isoformat()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
