# TCG LOG 改修版

## 今回の変更点
- 更新頻度を **9:00 / 15:00 / 21:00** に整理
- トップページを **最新まとめが主役** の構成に変更
- 「更新済みっぽく見せるだけ」の表示をやめ、`data/site-status.json` の実データを表示
- GitHub Actions で **指定時刻に自動更新処理** を実行

## 追加ファイル
- `index.html`
- `css/style.css`
- `data/site-status.json`
- `data/latest.json`
- `scripts/render_status.py`
- `.github/workflows/tcglog-scheduled-update.yml`

## 自動更新の意味
この実装で自動化されるのは、まず **サイトの更新ステータス反映** です。

- 毎日 JST 9:00 / 15:00 / 21:00 に GitHub Actions が起動
- `scripts/render_status.py` が `data/site-status.json` を更新
- トップページがその時刻を読み込んで「最終反映時刻」「次回自動更新予定」を表示

## 記事そのものも自動生成したい場合
次のどちらかを追加してください。

1. 外部APIやスクレイピングで記事データを集める
2. `scripts/` に記事生成スクリプトを追加し、HTMLとsitemapを更新する

今の構成は、そのための土台です。

## GitHub へ反映する手順
1. 既存の `index.html` を今回の `index.html` で置き換え
2. 既存の `css/style.css` を今回の `css/style.css` で置き換え
3. `data/` `scripts/` `.github/workflows/` を追加
4. push 後、GitHub の Actions タブで workflow が有効か確認

## 注意
GitHub Actions の `schedule` は UTC 基準です。
このファイルでは JST に合わせて以下に設定済みです。
- `0 0 * * *` → 9:00 JST
- `0 6 * * *` → 15:00 JST
- `0 12 * * *` → 21:00 JST
