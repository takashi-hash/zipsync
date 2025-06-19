# 🇯🇵 日本郵便住所データ管理システム（TinyDB版）

## 📦 概要
日本郵便が公開している住所CSVデータ（`utf_ken_all.zip`、`utf_add_YYMM.zip`、`utf_del_YYMM.zip`）を取り込み、ローカルの JSON データベース（TinyDB）で管理するためのデスクトップアプリです。GUI 上から一括登録や差分追加・削除、検索が行えます。

## 🛠 セットアップ
### 1. 仮想環境の作成と有効化
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 依存パッケージのインストール
`requirements.txt` を使用してインストールします。
```bash
pip install -r requirements.txt
```

### 3. 初期データの配置
以下の ZIP ファイルを日本郵便公式サイトからダウンロードし、`resources/` フォルダーに配置してください。
- 全国版: <https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/utf_ken_all.zip>
- 差分追加: <https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/utf_add_YYMM.zip>
- 差分削除: <https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/utf_del_YYMM.zip>

## 🚀 実行方法
仮想環境を有効化した状態で次を実行します。
```bash
python main.py
```
初回起動時に `data/address.json` と `data/import_log.json` が自動生成されます。

## 🖥️ 主な機能
| 機能 | 説明 |
| --- | --- |
| 一括登録 | `utf_ken_all.zip` を読み込み全件登録 |
| 差分追加 | `utf_add_YYMM.zip` の内容を追加登録 |
| 差分削除 | `utf_del_YYMM.zip` の内容を論理削除 |
| 全削除 | 登録済みの住所データをすべて削除 |
| 検索 | 郵便番号・都道府県・市区町村・町域でリアルタイム検索 |
| 詳細検索API | バックエンドで郵便番号・都道府県・市町村を条件指定して検索 |
| ページ付検索UI | 3 項目入力で条件指定し、30 件ずつページ送り |
| ログ表示 | 各操作の結果を画面下部に表示 |

## 🎨 UI について
- PySide6 ベースのシンプルな GUI
- 左メニューで画面切り替え（`QListWidget` + `QStackedWidget`）
- 検索ページは郵便番号・都道府県・市区町村を指定し、30 件ずつページ送り可能
- テーマには `qt-material` の `dark_teal.xml` を使用

## 📘 今後の拡張予定
- 履歴の再適用・取り消し
- 履歴一覧／復元の UI
- カスタム項目（メモ、タグ）編集
- CSV への部分エクスポート
- PyInstaller による配布

## よくある問題
- **モジュールが見つからない**: `python -m main` で実行するか、`__init__.py` を確認してください。
- **`data/address.json` が作成されない**: 権限の問題などで失敗した場合は `data/` フォルダーを手動で作成してください。
