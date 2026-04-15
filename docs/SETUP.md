# 公式更新検知 → 自動で記事化 セットアップ

## 1. source_registry.json を埋める
`data/source_registry.json` の `official_home` と `list_url` を各TCGの公式URLに置き換えてください。

- `list_url`: ニュース一覧 / お知らせ一覧 / 更新情報一覧ページ
- `item_selector`: 一覧の各記事リンクに当たる CSS セレクタ
- `title_selector`: リンクの中にタイトル要素がある場合のみ指定
- `summary_selector`: 一覧上に説明文がある場合のみ指定

まずは1タイトルだけ設定して手動実行し、抽出できることを確認してから対象を増やす運用が安全です。

## 2. GitHub Actions を有効化
workflow ファイルは `.github/workflows/official-detect-and-publish.yml` です。

- 定時実行: 日本時間 09:00 / 15:00 / 21:00
- 手動実行: Actions → Official detect and publish → Run workflow

## 3. 動作の流れ
1. 公式一覧ページを取得
2. 先頭記事を抽出
3. 前回保存した URL / タイトルと比較
4. 差分があれば `content_queue.json` に個別記事を追加
5. 同じ実行で「定時まとめ」も追加
6. `generate_site.py` が HTML と `sitemap.xml` を再生成

## 4. 状態ファイル
- `data/official_state.json`: 前回見た最新URLとタイトル
- `data/latest.json`: 各TCGの最新表示用データ
- `data/content_queue.json`: 記事化待ちを兼ねる元データ

## 5. 最初に見るべきポイント
- 一覧ページの構造はサイトごとに違います
- CSS セレクタがずれると検知できません
- 初回は `workflow_dispatch` で手動テスト推奨

## 6. おすすめの運用
- ポケカ / 遊戯王 / ワンピの3本から開始
- 安定後に他TCGへ拡張
- 公式更新の本文まで要約したい場合は、次段で記事URL本文抽出を追加
