from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from html import escape
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ARTICLES_DIR = ROOT / "articles"
QUEUE_FILE = DATA_DIR / "content_queue.json"
SITE_STATUS_FILE = DATA_DIR / "site-status.json"
LATEST_FILE = DATA_DIR / "latest.json"
INDEX_FILE = ROOT / "index.html"
SITEMAP_FILE = ROOT / "sitemap.xml"
TZ = ZoneInfo("Asia/Tokyo")

GENRE_CLASS = {
    "summary": "genre-summary",
    "pokeka": "genre-pokeka",
    "yugioh": "genre-yugioh",
    "onepiece": "genre-onepiece",
    "mtg": "genre-mtg",
    "duema": "genre-duema",
}

@dataclass
class Entry:
    type: str
    slug: str
    title: str
    description: str
    category: str
    genre: str
    published_at: datetime
    hero_label: str
    eyecatch: str
    source_label: str
    tags: list[str]
    highlights: list[str]
    sections: list[dict[str, Any]]

    @property
    def href(self) -> str:
        return f"articles/{self.slug}.html"

    @property
    def canonical(self) -> str:
        return f"https://tcglog.jp/{self.href}"

    @property
    def display_date(self) -> str:
        return self.published_at.astimezone(TZ).strftime("%Y/%m/%d %H:%M")

    @property
    def article_heading(self) -> str:
        return self.published_at.astimezone(TZ).strftime("%Y年%m月%d日 %H:%M 更新")


def load_queue() -> tuple[dict[str, Any], list[Entry]]:
    raw = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    site = raw["site"]
    entries: list[Entry] = []
    for item in raw["entries"]:
        entries.append(
            Entry(
                type=item["type"],
                slug=item["slug"],
                title=item["title"],
                description=item["description"],
                category=item["category"],
                genre=item["genre"],
                published_at=datetime.fromisoformat(item["publishedAt"]),
                hero_label=item.get("heroLabel", item["category"]),
                eyecatch=item.get("eyecatch", "FEATURE"),
                source_label=item.get("sourceLabel", "編集部整理"),
                tags=item.get("tags", []),
                highlights=item.get("highlights", []),
                sections=item.get("sections", []),
            )
        )
    entries.sort(key=lambda e: e.published_at, reverse=True)
    return site, entries


def genre_class(genre: str) -> str:
    return GENRE_CLASS.get(genre, "genre-summary")


def tag_html(tags: list[str]) -> str:
    return "\n          ".join(f'<span class="tag">{escape(tag)}</span>' for tag in tags)


def render_article(entry: Entry, site_name: str) -> str:
    highlights = "\n            ".join(f"<li>{escape(item)}</li>" for item in entry.highlights)
    sections_html: list[str] = []
    for section in entry.sections:
        paras = "\n          ".join(f"<p>{escape(p)}</p>" for p in section.get("paragraphs", []))
        sections_html.append(f"<h2>{escape(section.get('heading', '本文'))}</h2>\n          {paras}")
    body_html = "\n\n          ".join(sections_html)
    return f"""<!DOCTYPE html>
<html lang=\"ja\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{escape(entry.title)} | {escape(site_name)}</title>
  <meta name=\"description\" content=\"{escape(entry.description)}\">
  <meta property=\"og:title\" content=\"{escape(entry.title)} | {escape(site_name)}\">
  <meta property=\"og:description\" content=\"{escape(entry.description)}\">
  <meta property=\"og:type\" content=\"article\">
  <meta property=\"og:url\" content=\"{escape(entry.canonical)}\">
  <meta property=\"og:image\" content=\"https://tcglog.jp/assets/ogp.png\">
  <meta property=\"og:site_name\" content=\"{escape(site_name)}\">
  <meta name=\"twitter:card\" content=\"summary_large_image\">
  <link rel=\"canonical\" href=\"{escape(entry.canonical)}\">
  <link rel=\"stylesheet\" href=\"../css/style.css\">
</head>
<body>
<header class=\"site-header\">
  <div class=\"container\">
    <div class=\"header-inner\">
      <a href=\"/\" class=\"logo\">
        <span class=\"logo-mark\">TCG <span>LOG</span></span>
        <span class=\"logo-sub\">トレカ情報まとめ</span>
      </a>
      <nav class=\"header-nav\">
        <a href=\"/\">トップ</a>
        <a href=\"/#latest\">最新まとめ</a>
        <a href=\"/#genres\">ジャンル別</a>
      </nav>
    </div>
  </div>
</header>

<main>
  <div class=\"container main-shell\">
    <article>
      <div class=\"section-head compact\">
        <div>
          <p class=\"section-kicker\">{escape(entry.eyecatch)}</p>
          <h1 class=\"article-title\">{escape(entry.title)}</h1>
        </div>
      </div>

      <div class=\"featured-card\" style=\"padding:24px;margin-bottom:24px;\">
        <div class=\"featured-badge-row\">
          <span class=\"card-genre {genre_class(entry.genre)}\">{escape(entry.hero_label)}</span>
          <span class=\"featured-time\">{escape(entry.display_date)}</span>
        </div>
        <p class=\"featured-text\">{escape(entry.description)}</p>
        <div class=\"featured-points\">
          {tag_html(entry.tags)}
        </div>
      </div>

      <div class=\"about-panel\" style=\"grid-template-columns:1fr; margin-top:0;\">
        <div>
          <p class=\"section-kicker\">SOURCE</p>
          <h2 style=\"font-size:20px; margin-top:6px;\">{escape(entry.source_label)}</h2>
          <p style=\"margin-top:10px;\">{escape(entry.article_heading)}</p>
          <ul style=\"margin:14px 0 0 18px; color:var(--muted);\">
            {highlights}
          </ul>
        </div>
      </div>

      <div class=\"about-panel\" style=\"grid-template-columns:1fr; margin-top:18px;\">
        <div>
          {body_html}
        </div>
      </div>
    </article>
  </div>
</main>

<footer class=\"site-footer\">
  <div class=\"container\">
    <div class=\"footer-inner\">
      <div>
        <div class=\"logo-mark\" style=\"margin-bottom:4px\">TCG <span style=\"color:var(--accent)\">LOG</span></div>
        <div class=\"footer-copy\">© 2026 {escape(site_name)}. All rights reserved.</div>
      </div>
      <div class=\"footer-links\">
        <a href=\"/privacy.html\">プライバシーポリシー</a>
        <a href=\"/disclaimer.html\">免責事項</a>
      </div>
    </div>
  </div>
</footer>
</body>
</html>
"""


def render_index(site: dict[str, Any], entries: list[Entry], latest_summary: Entry | None) -> str:
    headline_title = latest_summary.title if latest_summary else "最新まとめは準備中です"
    headline_href = latest_summary.href if latest_summary else "#"
    featured_html = ""
    if latest_summary:
        featured_html = f"""
      <a href=\"{escape(latest_summary.href)}\" class=\"featured-card\">
        <div class=\"featured-badge-row\">
          <span class=\"card-genre {genre_class(latest_summary.genre)}\">{escape(latest_summary.hero_label)}</span>
          <span class=\"featured-time\">{escape(latest_summary.display_date)}</span>
        </div>
        <h3 class=\"featured-title\">{escape(latest_summary.title)}</h3>
        <p class=\"featured-text\">{escape(latest_summary.description)}</p>
        <div class=\"featured-points\">
          {tag_html(latest_summary.tags)}
        </div>
      </a>
        """
    pickup_candidates = [e for e in entries if e.type != "summary"][:4]
    pickup_html = "\n".join(
        f"""        <a href=\"{escape(e.href)}\" class=\"pickup-card\">
          <span class=\"card-genre {genre_class(e.genre)}\">{escape(e.category)}</span>
          <h3>{escape(e.title)}</h3>
          <p>{escape(e.description)}</p>
        </a>"""
        for e in pickup_candidates
    )
    feed_html = "\n".join(
        f"""        <a href=\"{escape(e.href)}\" class=\"article-card{' pinned' if e.type == 'summary' else ''}\" data-genre=\"{escape(e.genre)}\">
          <div class=\"card-inner\">
            <div class=\"card-meta\">
              <span class=\"card-genre {genre_class(e.genre)}\">{escape(e.category)}</span>
              <span class=\"card-date\">{escape(e.display_date)}</span>
            </div>
            <div class=\"card-title\">{escape(e.title)}</div>
            <div class=\"card-excerpt\">{escape(e.description)}</div>
          </div>
        </a>"""
        for e in entries[:12]
    )
    schedule_text = " / ".join(site.get("schedule", []))
    return f"""<!DOCTYPE html>
<html lang=\"ja\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{escape(site['name'])} — トレカ情報まとめサイト</title>
  <meta name=\"description\" content=\"{escape(site['description'])}\">
  <meta property=\"og:title\" content=\"{escape(site['name'])} — トレカ情報まとめサイト\">
  <meta property=\"og:description\" content=\"{escape(site['description'])}\">
  <meta property=\"og:type\" content=\"website\">
  <meta property=\"og:url\" content=\"{escape(site['url'])}/\">
  <meta property=\"og:image\" content=\"https://tcglog.jp/assets/ogp.png\">
  <meta property=\"og:site_name\" content=\"{escape(site['name'])}\">
  <meta name=\"twitter:card\" content=\"summary_large_image\">
  <link rel=\"canonical\" href=\"{escape(site['url'])}/\">
  <link rel=\"stylesheet\" href=\"css/style.css\">
</head>
<body>
<header class=\"site-header\">
  <div class=\"container\">
    <div class=\"header-inner\">
      <a href=\"/\" class=\"logo\">
        <span class=\"logo-mark\">TCG <span>LOG</span></span>
        <span class=\"logo-sub\">トレカ情報まとめ</span>
      </a>
      <nav class=\"header-nav\">
        <a href=\"/\">トップ</a>
        <a href=\"#latest\">最新まとめ</a>
        <a href=\"#genres\">ジャンル別</a>
        <a href=\"#about\">このサイトについて</a>
      </nav>
    </div>
  </div>
</header>

<div class=\"headline-bar\">
  <div class=\"container headline-inner\">
    <span class=\"headline-chip\">LATEST</span>
    <a class=\"headline-link\" href=\"{escape(headline_href)}\">{escape(headline_title)}</a>
  </div>
</div>

<main>
  <div class=\"container main-shell\">
    <section class=\"hero-block\">
      <div class=\"hero-copy\">
        <p class=\"eyebrow\">TCG NEWS CURATED</p>
        <h1 class=\"hero-title\">今日のトレカ情報を、<br>ひと目で追える形に。</h1>
        <p class=\"hero-desc\">ポケカ・遊戯王・MTG・ワンピースカード・デュエマの動きを、朝・昼・夜の3回に整理して掲載します。更新予定時刻は <strong>{escape(schedule_text)}</strong> です。</p>
        <div class=\"hero-actions\">
          <a class=\"btn btn-primary\" href=\"#latest\">最新まとめを見る</a>
          <a class=\"btn btn-secondary\" href=\"#genres\">ジャンル別に見る</a>
        </div>
      </div>
      <div class=\"status-panel\">
        <div class=\"status-card\">
          <div class=\"status-label\">更新ステータス</div>
          <div id=\"update-status-text\" class=\"status-main\">本日の更新判定を読み込み中…</div>
          <div id=\"update-status-sub\" class=\"status-sub\">自動更新スケジュール: {escape(schedule_text)}</div>
        </div>
        <div class=\"status-card muted\">
          <div class=\"status-label\">この表示について</div>
          <div class=\"status-list\">
            <div>・表示だけで「更新済み」を偽装しません</div>
            <div>・最終反映時刻はデータファイルから表示</div>
            <div>・記事HTMLと sitemap も同時に更新します</div>
          </div>
        </div>
      </div>
    </section>

    <section id=\"latest\" class=\"featured-section\">
      <div class=\"section-head\">
        <div>
          <p class=\"section-kicker\">MAIN FEATURE</p>
          <h2>まずはこれを読めばOK</h2>
        </div>
        <a href=\"{escape(headline_href)}\" class=\"section-link\">最新まとめへ →</a>
      </div>
{featured_html}
    </section>

    <section id=\"genres\" class=\"pickup-section\">
      <div class=\"section-head compact\">
        <div>
          <p class=\"section-kicker\">PICKUPS</p>
          <h2>ジャンル別の注目記事</h2>
        </div>
      </div>
      <div class=\"pickup-grid\">
{pickup_html}
      </div>
    </section>

    <section class=\"feed-section\">
      <div class=\"section-head compact\">
        <div>
          <p class=\"section-kicker\">LATEST FEED</p>
          <h2>新着記事一覧</h2>
        </div>
      </div>
      <div class=\"filter-bar\">
        <button class=\"filter-btn active\" data-genre=\"all\">すべて</button>
        <button class=\"filter-btn\" data-genre=\"summary\">まとめ</button>
        <button class=\"filter-btn\" data-genre=\"pokeka\">ポケカ</button>
        <button class=\"filter-btn\" data-genre=\"yugioh\">遊戯王</button>
        <button class=\"filter-btn\" data-genre=\"onepiece\">ワンピース</button>
        <button class=\"filter-btn\" data-genre=\"mtg\">MTG</button>
        <button class=\"filter-btn\" data-genre=\"duema\">デュエマ</button>
      </div>
      <div class=\"articles-grid\" id=\"articles-grid\">
{feed_html}
      </div>
    </section>

    <section id=\"about\" class=\"about-panel\">
      <div>
        <p class=\"section-kicker\">ABOUT</p>
        <h2>{escape(site['name'])}について</h2>
        <p>TCG LOGは、トレカの情報を朝・昼・夜に整理して届けるためのまとめサイトです。速報を追いかけるだけでなく、あとから見返しやすい並びを重視しています。</p>
      </div>
      <div class=\"about-note\">
        <strong>この構成の特徴</strong>
        <ul>
          <li>最新まとめをトップの主役に固定</li>
          <li>記事HTML・トップ・サイトマップを一括生成</li>
          <li>更新時刻は実データと連動して表示</li>
        </ul>
      </div>
    </section>
  </div>
</main>

<footer class=\"site-footer\">
  <div class=\"container\">
    <div class=\"footer-inner\">
      <div>
        <div class=\"logo-mark\" style=\"margin-bottom:4px\">TCG <span style=\"color:var(--accent)\">LOG</span></div>
        <div class=\"footer-copy\">© 2026 {escape(site['name'])}. All rights reserved.</div>
      </div>
      <div class=\"footer-links\">
        <a href=\"/privacy.html\">プライバシーポリシー</a>
        <a href=\"/disclaimer.html\">免責事項</a>
        <a href=\"#about\">このサイトについて</a>
      </div>
    </div>
  </div>
</footer>

<script>
  const filterBtns = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.article-card');
  filterBtns.forEach(btn => {{
    btn.addEventListener('click', () => {{
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const genre = btn.dataset.genre;
      cards.forEach(card => {{
        card.style.display = (genre === 'all' || card.dataset.genre === genre) ? 'block' : 'none';
      }});
    }});
  }});

  async function loadSiteStatus() {{
    try {{
      const res = await fetch('data/site-status.json', {{ cache: 'no-store' }});
      const data = await res.json();
      const last = new Date(data.lastPublishedAt);
      const fmt = new Intl.DateTimeFormat('ja-JP', {{
        timeZone: data.timezone || 'Asia/Tokyo',
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
      }});
      document.getElementById('update-status-text').textContent = `最終反映: ${{fmt.format(last)}}`;
      document.getElementById('update-status-sub').textContent = `次回自動更新: ${{data.nextScheduledAtLabel || '未設定'}}`;
    }} catch (err) {{
      document.getElementById('update-status-text').textContent = '更新情報を読み込めませんでした';
      document.getElementById('update-status-sub').textContent = 'data/site-status.json を確認してください';
    }}
  }}
  loadSiteStatus();
</script>
</body>
</html>
"""


def render_sitemap(site_url: str, entries: list[Entry]) -> str:
    blocks = [
        f"""  <url>
    <loc>{site_url}/</loc>
    <lastmod>{datetime.now(TZ).date().isoformat()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""
    ]
    for entry in entries:
        changefreq = "daily" if entry.type == "summary" else "weekly"
        priority = "0.8" if entry.type == "summary" else "0.7"
        blocks.append(
            f"""  <url>
    <loc>{entry.canonical}</loc>
    <lastmod>{entry.published_at.astimezone(TZ).date().isoformat()}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        )
    return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n\n" + "\n\n".join(blocks) + "\n\n</urlset>\n"


def next_schedule_label(schedule: list[str], now: datetime) -> str:
    today = now.astimezone(TZ).date()
    for item in schedule:
        hour, minute = map(int, item.split(":"))
        slot = datetime(today.year, today.month, today.day, hour, minute, tzinfo=TZ)
        if slot > now.astimezone(TZ):
            return slot.strftime("%Y/%m/%d %H:%M JST")
    tomorrow = today + timedelta(days=1)
    hour, minute = map(int, schedule[0].split(":"))
    return datetime(tomorrow.year, tomorrow.month, tomorrow.day, hour, minute, tzinfo=TZ).strftime("%Y/%m/%d %H:%M JST")


def write_status(site: dict[str, Any], latest_entry: Entry | None) -> None:
    now = datetime.now(TZ)
    payload = {
        "lastPublishedAt": (latest_entry.published_at if latest_entry else now).isoformat(),
        "generatedAt": now.isoformat(),
        "schedule": site.get("schedule", []),
        "timezone": site.get("timezone", "Asia/Tokyo"),
        "nextScheduledAtLabel": next_schedule_label(site.get("schedule", ["09:00", "15:00", "21:00"]), now),
    }
    SITE_STATUS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_latest(entry: Entry | None) -> None:
    payload: dict[str, Any] = {}
    if entry:
        payload = {
            "title": entry.title,
            "href": entry.href,
            "publishedAt": entry.published_at.isoformat(),
            "genre": entry.genre,
            "description": entry.description,
        }
    LATEST_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    site, entries = load_queue()
    latest_summary = next((e for e in entries if e.type == "summary"), None)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        (ARTICLES_DIR / f"{entry.slug}.html").write_text(render_article(entry, site["name"]), encoding="utf-8")
    INDEX_FILE.write_text(render_index(site, entries, latest_summary), encoding="utf-8")
    SITEMAP_FILE.write_text(render_sitemap(site["url"], entries), encoding="utf-8")
    write_status(site, latest_summary or (entries[0] if entries else None))
    write_latest(latest_summary or (entries[0] if entries else None))
    print(f"Generated {len(entries)} article(s), index.html, sitemap.xml, and status files.")


if __name__ == "__main__":
    main()
