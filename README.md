# 🇯🇵 日本郵便住所データ管理システム（TinyDB版）

## 📦 概要

このアプリは、日本郵便が提供する住所CSVデータ（`utf_ken_all.zip`、`utf_add_YYMM.zip`、`utf_del_YYMM.zip`）をGUIから取り込み・管理できるデスクトップアプリです。

- Python + PySide6 + TinyDB 製
- 住所データをローカルJSONデータベース（TinyDB）に保存
- 差分追加／削除に対応（履歴ログあり）
- GUI操作で一括登録・検索が可能
- 今後の拡張：履歴復元・カスタム編集・非同期対応 etc...

---

## 🛠 セットアップ

### 1. 仮想環境作成（任意）

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

2. 必要ライブラリのインストール
bash
コピーする
編集する
pip install -r requirements.txt
requirements.txt がない場合はこちら：

bash
コピーする
編集する
pip install pyside6 tinydb qt-material requests
3. 初期データ準備
resources/utf_ken_all.zip に、日本郵便公式から取得したZIPを配置してください。

全国版：https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/utf_ken_all.zip

差分追加：https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/utf_add_YYMM.zip

差分削除：https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/utf_del_YYMM.zip

🚀 起動方法
bash
コピーする
編集する
python main.py
初回起動時に data/address.json と data/import_log.json が自動作成されます。

🖥️ 機能一覧
機能	説明
一括登録	utf_ken_all.zip を使って住所を全件登録します
差分追加	utf_add_YYMM.zip を使って新住所を追加します
差分削除	utf_del_YYMM.zip を使って住所を論理削除します
検索	郵便番号・都道府県・市区町村・町域でリアルタイム検索可能です
ログ表示	各操作結果が下部のログ領域に出力されます
⚠ 履歴復元	未実装（reverse_patch.py は土台あり）
⚠ 履歴一覧UI	未実装（import_log.json の内容表示）
⚠ カスタム項目編集	未実装（models.py にカスタム項目定義あり）

🎨 UIについて
PySide6ベース

左メニューによる画面切替（QListWidget + QStackedWidget）

検索ページは QTableView + QSortFilterProxyModel による高速フィルタ

テーマ：qt-material を使用（dark_teal.xml）

📘 補足機能（今後）
✅ 差分の再適用・取り消し（ログ管理）

✅ UIからの履歴一覧／復元

✅ カスタム項目（メモ、タグ）編集画面

✅ データの部分エクスポート（CSV）

✅ PyInstaller による exe 配布（予定）

✅ よくある問題
モジュールエラーで動かない
→ python -m main のようにモジュール実行するか、__init__.py を確認してください。

data/address.json がない
→ 自動で作成されるはずですが、権限などで失敗した場合は data/ を手動で作ってください。

