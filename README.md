# TCG LOG — セットアップガイド

## ファイル構成

```
tcglog/
├── index.html              # トップページ（記事一覧）
├── privacy.html            # プライバシーポリシー
├── disclaimer.html         # 免責事項
├── sitemap.xml             # SEO用サイトマップ
├── CNAME                   # GitHub Pages 独自ドメイン設定
├── css/
│   └── style.css           # 共通スタイル
└── articles/
    ├── summary-YYYYMMDD-HHMM.html  # 定時まとめ記事
    └── [genre]-YYYYMMDD.html       # ジャンル別記事
```

---

## GitHub Pages 公開手順

### 1. GitHub にリポジトリを作成

1. https://github.com にログイン
2. 右上「+」→「New repository」
3. Repository name: `tcglog`（何でもOK）
4. Public を選択
5. 「Create repository」をクリック

### 2. ファイルをアップロード

**方法A: ブラウザからアップロード（簡単）**
1. 作成したリポジトリページで「uploading an existing file」をクリック
2. このフォルダの中身を全部ドラッグ＆ドロップ
3. 「Commit changes」をクリック

**方法B: Git コマンド（慣れてきたら）**
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/ユーザー名/tcglog.git
git push -u origin main
```

### 3. GitHub Pages を有効化

1. リポジトリ → 「Settings」タブ
2. 左メニュー「Pages」
3. Source: 「Deploy from a branch」
4. Branch: `main` / `/ (root)`
5. 「Save」

→ しばらくすると `https://ユーザー名.github.io/tcglog/` でアクセス可能に

### 4. 独自ドメイン（tcglog.jp）を設定

**DNSレコード設定（ドメイン管理画面で行う）**

Aレコード × 4を追加：
```
@ → 185.199.108.153
@ → 185.199.109.153
@ → 185.199.110.153
@ → 185.199.111.153
```

CNAMEレコードを追加：
```
www → ユーザー名.github.io
```

**GitHub側の設定**
1. Settings → Pages → Custom domain
2. `tcglog.jp` を入力して Save
3. 「Enforce HTTPS」にチェックを入れる

→ DNS反映に最大48時間かかる

---

## 新しい記事を追加する方法

### 定時まとめ記事
`articles/summary-20240413-2100.html` をコピーして、
- ファイル名の日付・時刻を変更
- `<title>` タグを更新
- `<meta name="description">` を更新
- `<link rel="canonical">` のURLを更新
- 記事本文を書き換える

### ジャンル別記事
`articles/pokeka-20240413.html` をコピーして同様に更新。

### sitemap.xml の更新
新しい記事を追加したら `sitemap.xml` に `<url>` ブロックを追加する。

---

## Google Search Console への登録

1. https://search.google.com/search-console にアクセス
2. 「URLプレフィックス」で `https://tcglog.jp/` を入力
3. HTMLファイルをダウンロードしてリポジトリのルートに配置
4. プッシュ後「確認」ボタンを押す
5. 確認完了後、サイトマップを送信：`https://tcglog.jp/sitemap.xml`

---

## Google Analytics の設定

1. https://analytics.google.com でプロパティを作成
2. 「ウェブストリーム」でサイトURLを入力
3. 測定IDをコピー（`G-XXXXXXXXXX` の形式）
4. 全HTMLファイルの `</head>` 直前に以下を追加：

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

---

## AdSense 申請チェックリスト

申請前に以下を確認：
- [ ] プライバシーポリシーページがある
- [ ] 免責事項ページがある
- [ ] 記事が10本以上ある
- [ ] 各記事が1,000字以上ある
- [ ] HTTPS が有効になっている
- [ ] サイトが正常に表示される
- [ ] お問い合わせ方法が明記されている
