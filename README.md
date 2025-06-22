# 🇯🇵 日本郵便住所データ管理システム（TinyDB版）

## 概要
日本郵便が公開している住所CSVデータ（`utf_ken_all.zip`、`utf_add_YYMM.zip`、`utf_del_YYMM.zip`）を取り込み、ローカルの JSON データベース（TinyDB）で管理するためのデスクトップアプリです。GUI 上から住所データの一括登録や更新データの追加登録・削除、検索が行えます。

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
Excel 連携機能を利用するため `openpyxl` も依存関係に含まれています。

### 3. 初期データの配置
以下の ZIP ファイルを日本郵便公式サイトからダウンロードし、`resources/` フォルダーに配置してください。
- 全国版: <https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/utf_ken_all.zip>
- 追加データ: <https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/utf_add_YYMM.zip>
- 削除データ: <https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/utf_del_YYMM.zip>

### ダウンロードデータのフォーマット
日本郵便が配布する CSV ファイルは次の順で項目が並んでいます。

1. 全国地方公共団体コード（JIS X0401、X0402） - 半角数字
2. （旧）郵便番号（5桁） - 半角数字
3. 郵便番号（7桁） - 半角数字
4. 都道府県名（カナ） - 全角カタカナ
5. 市区町村名（カナ） - 全角カタカナ
6. 町域名（カナ） - 全角カタカナ
7. 都道府県名（漢字）
8. 市区町村名（漢字）
9. 町域名（漢字）
10. 一町域が二以上の郵便番号で表される場合の表示（1 = 該当、0 = 該当せず）
11. 小字毎に番地が起番されている町域の表示（1 = 該当、0 = 該当せず）
12. 丁目を有する町域の場合の表示（1 = 該当、0 = 該当せず）
13. 一つの郵便番号で二以上の町域を表す場合の表示（1 = 該当、0 = 該当せず）
14. 更新の表示（0 = 変更なし、1 = 変更あり、2 = 廃止）
15. 変更理由（0 = 変更なし、1 = 市政・区政・町政・分区・政令指定都市施行、2 = 住居表示の実施、3 = 区画整理、4 = 郵便区調整等、5 = 訂正、6 = 廃止）

## 🚀 実行方法
仮想環境を有効化した状態で次を実行します。
```bash
python main.py
```
初回起動時に `data/address.json` と `data/import_log.json` が自動生成されます。

## 🖥️ 主な機能
| 機能 | 説明 |
| --- | --- |
| 全住所データの初期登録 | `utf_ken_all.zip` を読み込み全件登録 |
| 更新データの追加登録（新住所） | `utf_add_YYMM.zip` の内容を追加登録 |
| 更新データによる削除（削除済住所） | `utf_del_YYMM.zip` の内容を論理削除 |
| 全削除 | 登録済みの住所データをすべて削除 |
| 検索 | 郵便番号・都道府県・市区町村・町域でリアルタイム検索 |
| 詳細検索API | バックエンドで郵便番号・都道府県・市区町村・町域を条件指定して検索 |
| ページ付検索UI | 4 項目入力で条件指定し、30 件ずつページ送り |
| ログ表示 | 各操作の結果を画面下部に表示 |
| サイドバー開閉 | 左メニューを隠してメイン画面を拡大 |
| ログ欄開閉 | 出力ログを折りたたみ縦領域を拡大 |
| 取込履歴表示 | 差分取込の履歴を一覧・復元・削除 |
| 配送設定一括反映 | Excel から営業所コードやコースコードなどを読み込み配送設定を統合 |


### 配送設定 Excel のフォーマット
配送設定を取り込む Excel ファイルには次の 3 つのシートを用意します。

1. **entries**: `zipcode`, `office_code`, `destination_name`, `shiwake_code`
2. **course_codes**: `zipcode`, `course_code`
3. **pickup_variants**: `zipcode`, `pickup_location`, `delivery_type`, `destination_name`, `shiwake_code`

それぞれのシートに郵便番号を 7 桁で記載し、必要な配送情報を入力してください。

## 🎨 UI について
- PySide6 ベースのシンプルな GUI
- 左メニューで画面切り替え（`QListWidget` + `QStackedWidget`）
- メニューと出力ログはボタンで折りたたみ可能
- 検索ページは郵便番号・都道府県・市区町村・町域を指定し、30 件ずつページ送り可能
- パステル調のカスタム QSS でシンプルな外観を実現

## 📘 今後の拡張予定
- カスタム項目（メモ、タグ）編集
- CSV への部分エクスポート
- PyInstaller による配布

## よくある問題
- **モジュールが見つからない**: `python -m main` で実行するか、`__init__.py` を確認してください。
- **`data/address.json` が作成されない**: 権限の問題などで失敗した場合は `data/` フォルダーを手動で作成してください。
