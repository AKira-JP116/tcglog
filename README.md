# TCG LOG - Official Only

現状サイトをいったん白紙にして、**公式更新検知 → 自動で記事化** だけに絞った最小構成です。

## 残すもの
- `scripts/detect_official_updates.py`
- `scripts/generate_site.py`
- `.github/workflows/official-detect-and-publish.yml`
- `data/source_registry.json`
- `data/content_queue.json`
- `data/official_state.json`
- `articles/`
- `index.html`
- `sitemap.xml`

## 使わないもの
- 相場まとめ
- トレンド欄
- 編集用フォーム
- 総合ニュース風のトップ導線

## サイト方針
- 公式更新のみ監視
- 差分が出たときだけ公開
- 各記事に元ソースを明記
- まずは公式ソース3〜5本から開始
