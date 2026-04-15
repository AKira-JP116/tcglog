# TCG LOG 自動生成版

## できること
- 毎日 **9:00 / 15:00 / 21:00** に GitHub Actions が起動
- `data/content_queue.json` を読んで **記事HTMLを自動生成**
- 同時に **トップページ `index.html`** を再生成
- 同時に **`sitemap.xml`** を再生成
- `data/site-status.json` と `data/latest.json` も更新

## 更新の流れ
1. `data/content_queue.json` に記事データを入れる
2. Actions が `scripts/generate_site.py` を実行
3. 以下が自動更新される
   - `articles/*.html`
   - `index.html`
   - `sitemap.xml`
   - `data/site-status.json`
   - `data/latest.json`

## 重要ポイント
この版は **記事ページ生成とサイトマップ更新まで自動化** しています。
ただし、記事内容の元データは `content_queue.json` に入る前提です。

つまり、完全自動にするには次のどちらかを後で追加します。
- APIやスクレイピングで `content_queue.json` を自動生成
- ChatGPTや別スクリプトで `content_queue.json` を更新

## content_queue.json の役割
ここが編集部の原稿置き場です。1件ごとに次の情報を持ちます。
- slug
- title
- description
- category
- genre
- publishedAt
- tags
- sections

## 導入手順
1. 既存リポジトリに以下を追加
   - `css/style.css`
   - `scripts/generate_site.py`
   - `data/content_queue.json`
   - `.github/workflows/tcglog-auto-generate.yml`
2. 一度ローカルまたは Actions で `python scripts/generate_site.py` を実行
3. 生成された `index.html` `articles/*.html` `sitemap.xml` を確認
4. GitHub Pages に反映

## 補足
- GitHub Actions の cron は UTC 基準です
- この workflow は JST 9:00 / 15:00 / 21:00 に合わせて設定済みです
- 以前の `render_status.py` 単体更新 workflow は不要なら外してOKです
