from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
ARTICLES_DIR = ROOT / 'articles'
QUEUE_FILE = DATA_DIR / 'content_queue.json'
INDEX_FILE = ROOT / 'index.html'
SITEMAP_FILE = ROOT / 'sitemap.xml'
TZ = ZoneInfo('Asia/Tokyo')
GENRE_CLASS = {
    'pokeka': 'genre-pokeka',
    'yugioh': 'genre-yugioh',
    'onepiece': 'genre-onepiece',
    'duema': 'genre-duema',
    'mtg': 'genre-mtg',
    'summary': 'genre-summary',
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
    source_label: str
    tags: list[str]
    highlights: list[str]
    sections: list[dict[str, Any]]

    @property
    def href(self) -> str:
        return f'articles/{self.slug}.html'

    @property
    def canonical(self) -> str:
        return f'https://tcglog.jp/{self.href}'

    @property
    def display_date(self) -> str:
        return self.published_at.astimezone(TZ).strftime('%Y/%m/%d %H:%M')


def load_queue() -> tuple[dict[str, Any], list[Entry]]:
    raw = json.loads(QUEUE_FILE.read_text(encoding='utf-8'))
    site = raw['site']
    entries: list[Entry] = []
    for item in raw['entries']:
        entries.append(
            Entry(
                type=item['type'], slug=item['slug'], title=item['title'], description=item['description'],
                category=item['category'], genre=item['genre'], published_at=datetime.fromisoformat(item['publishedAt']),
                hero_label=item.get('heroLabel', item['category']), source_label=item.get('sourceLabel', '公式更新'),
                tags=item.get('tags', []), highlights=item.get('highlights', []), sections=item.get('sections', [])
            )
        )
    entries.sort(key=lambda e: e.published_at, reverse=True)
    return site, entries


def genre_class(genre: str) -> str:
    return GENRE_CLASS.get(genre, 'genre-summary')


def render_article(entry: Entry, site_name: str) -> str:
    section_html = []
    for sec in entry.sections:
        paras = ''.join(f'<p>{escape(p)}</p>' for p in sec.get('paragraphs', []))
        section_html.append(f"<section class='article-section'><h2>{escape(sec.get('heading', '概要'))}</h2>{paras}</section>")
    highlights = ''.join(f'<li>{escape(x)}</li>' for x in entry.highlights)
    tags = ''.join(f'<span class="tag">{escape(t)}</span>' for t in entry.tags)
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(entry.title)} | {escape(site_name)}</title>
<meta name="description" content="{escape(entry.description)}">
<link rel="canonical" href="{escape(entry.canonical)}">
<link rel="stylesheet" href="../css/style.css">
</head>
<body>
<header class="site-header"><div class="container header-inner"><a class="logo" href="/">TCG <span>LOG</span></a><nav class="header-nav"><a href="/">トップ</a></nav></div></header>
<main class="container article-shell">
  <div class="article-hero">
    <div class="meta-row"><span class="card-genre {genre_class(entry.genre)}">{escape(entry.category)}</span><span class="article-date">{escape(entry.display_date)}</span></div>
    <h1>{escape(entry.title)}</h1>
    <p class="article-lead">{escape(entry.description)}</p>
    <div class="tag-row">{tags}</div>
  </div>
  <div class="article-panel">
    <p class="source-line">情報源: {escape(entry.source_label)}</p>
    <ul class="highlight-list">{highlights}</ul>
    {''.join(section_html)}
  </div>
</main>
<footer class="site-footer"><div class="container footer-inner"><div class="footer-copy">&copy; 2026 {escape(site_name)}</div></div></footer>
</body>
</html>'''


def render_index(site: dict[str, Any], entries: list[Entry]) -> str:
    latest = entries[0] if entries else None
    latest_html = ''
    if latest:
        latest_html = f'''<a class="hero-card" href="{escape(latest.href)}">
  <div class="meta-row"><span class="card-genre {genre_class(latest.genre)}">{escape(latest.category)}</span><span class="article-date">{escape(latest.display_date)}</span></div>
  <h2>{escape(latest.title)}</h2>
  <p>{escape(latest.description)}</p>
</a>'''
    feed_html = '\n'.join(
        f'''<a class="feed-card" href="{escape(e.href)}"><div class="meta-row"><span class="card-genre {genre_class(e.genre)}">{escape(e.category)}</span><span class="article-date">{escape(e.display_date)}</span></div><h3>{escape(e.title)}</h3><p>{escape(e.description)}</p></a>'''
        for e in entries[:20]
    )
    monitored = ''.join(f'<li>{escape(x)}</li>' for x in site.get('monitoredGenres', []))
    schedule = ' / '.join(site.get('schedule', ['09:00', '15:00', '21:00']))
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(site['name'])} | 公式更新速報</title>
<meta name="description" content="{escape(site['description'])}">
<link rel="canonical" href="{escape(site['url'])}/">
<link rel="stylesheet" href="css/style.css">
</head>
<body>
<header class="site-header"><div class="container header-inner"><a class="logo" href="/">TCG <span>LOG</span></a><nav class="header-nav"><a href="#latest">最新</a><a href="#feed">更新一覧</a></nav></div></header>
<main class="container main-shell">
  <section class="plain-hero">
    <p class="eyebrow">OFFICIAL UPDATE WATCH</p>
    <h1>公式更新だけを追う<br>TCG速報板</h1>
    <p class="hero-desc">各TCGの公式サイト更新を定期検知し、差分があったときだけ自動で記事化します。まとめ記事、相場雑記、トレンド装飾はいったん外し、速報性を最優先にした最小構成です。</p>
    <div class="status-inline"><span>更新時刻: {escape(schedule)}</span><span>監視対象: {len(site.get('monitoredGenres', []))}タイトル</span></div>
  </section>
  <section id="latest" class="section-block">
    <div class="section-head"><div><p class="section-kicker">LATEST</p><h2>最新の公式更新</h2></div></div>
    {latest_html or '<div class="empty-card">まだ記事がありません。</div>'}
  </section>
  <section class="section-block info-grid">
    <div class="info-card"><p class="section-kicker">POLICY</p><h3>このサイトでやること</h3><ul><li>公式更新のみ監視</li><li>差分がある時だけ記事化</li><li>各記事に元ソースを明記</li></ul></div>
    <div class="info-card"><p class="section-kicker">TARGETS</p><h3>監視対象</h3><ul>{monitored}</ul></div>
  </section>
  <section id="feed" class="section-block">
    <div class="section-head"><div><p class="section-kicker">FEED</p><h2>公式更新記事一覧</h2></div></div>
    <div class="feed-grid">{feed_html}</div>
  </section>
</main>
<footer class="site-footer"><div class="container footer-inner"><div class="footer-copy">&copy; 2026 {escape(site['name'])}</div></div></footer>
</body>
</html>'''


def render_sitemap(site: dict[str, Any], entries: list[Entry]) -> str:
    urls = [f"  <url><loc>{site['url']}/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>"]
    for e in entries:
        urls.append(f"  <url><loc>{site['url']}/{e.href}</loc><lastmod>{e.published_at.date().isoformat()}</lastmod><changefreq>never</changefreq><priority>0.8</priority></url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n'


def main() -> None:
    site, entries = load_queue()
    ARTICLES_DIR.mkdir(exist_ok=True)
    for e in entries:
        (ARTICLES_DIR / f'{e.slug}.html').write_text(render_article(e, site['name']), encoding='utf-8')
    INDEX_FILE.write_text(render_index(site, entries), encoding='utf-8')
    SITEMAP_FILE.write_text(render_sitemap(site, entries), encoding='utf-8')

if __name__ == '__main__':
    main()
