# 各種操作をまとめたコントローラ

from japanpost_backend.file_fetcher import download_zip
from japanpost_backend.bulk_register import bulk_register
from japanpost_backend.diff_applier import (
    apply_add_zip, apply_del_zip,
)
from japanpost_backend.reapply_patch import reapply_log_entry
from japanpost_backend.db_manager import (
    get_all, clear_all, count_records,
    update_custom, get_by_zipcode,
)
from japanpost_backend.search_manager import search_with_filters, search_multiple
from japanpost_backend.log_manager import get_logs, delete_log
from japanpost_backend.reverse_patch import reverse_log_entry


class Controller:
    """GUI とバックエンドを仲介する役割"""
    def bulk_register(self, url: str):
        """ZIP をダウンロードして全件登録"""
        try:
            path = download_zip(url)
            bulk_register(path, url)
            return f"[OK] 一括登録成功: {url}"
        except Exception as e:
            return f"[ERROR] 一括登録失敗: {e}"

        """追加差分を適用"""
    def apply_add(self, url: str):
        try:
            path = download_zip(url)
            apply_add_zip(path, url)
            return f"[OK] 差分追加成功: {url}"
        except Exception as e:
            return f"[ERROR] 差分追加失敗: {e}"
        """削除差分を適用"""

    def apply_del(self, url: str):
        try:
            path = download_zip(url)
            apply_del_zip(path, url)
            return f"[OK] 差分削除成功: {url}"
        except Exception as e:
            return f"[ERROR] 差分削除失敗: {e}"

    def get_all_addresses(self):
        """全住所の一覧を返す"""
        records = get_all()
        return [(r["zipcode"], r["pref"], r["city"], r["town"]) for r in records]

    def search_addresses(self, zipcode: str = "", pref: str = "", city: str = "",
                         town: str = "", page: int = 1, per_page: int = 30,
                         filters=None):
        """条件で検索しページネーション結果を返す"""
        if filters is not None:
            results, total = search_multiple(filters, page, per_page)
        else:
            results, total = search_with_filters(zipcode, pref, city, town,
                                                page, per_page)
        data = [(r["zipcode"], r["pref"], r["city"], r["town"]) for r in results]
        return data, total

    def clear_database(self):
        """住所データを全件削除"""
        try:
            clear_all()
            return "[OK] 全データを削除しました"
        except Exception as e:
            return f"[ERROR] 全データ削除失敗: {e}"

    def get_record_count(self) -> int:
        """登録件数を取得"""
        return count_records()

    def get_record(self, zipcode: str):
        """指定の郵便番号のレコードを返す"""
        return get_by_zipcode(zipcode)

    # --- log handling ---
    def fetch_logs(self, page: int = 1, per_page: int = 30):
        """取込履歴をページ取得"""
        return get_logs(page, per_page)

    def reverse_logs(self, indices):
        """選択された履歴を取り消す"""
        msgs = []
        for idx in sorted(indices):
            msgs.append(reverse_log_entry(idx))
        return "\n".join(msgs)

    def delete_logs(self, indices):
        """選択された履歴を削除"""
        for idx in sorted(indices, reverse=True):
            delete_log(idx)
        return "[OK] 履歴を削除しました"

    def reapply_logs(self, indices):
        """選択された履歴を再実行"""
        msgs = []
        for idx in sorted(indices):
            msgs.append(reapply_log_entry(idx))
        return "\n".join(msgs)

    # --- custom field handling ---
    def update_custom_fields(self, zipcodes, custom):
        """複数レコードに同じカスタム値を設定"""
        for zc in zipcodes:
            update_custom(zc, custom)
        return f"[OK] カスタム項目を更新しました ({len(zipcodes)} 件)"

    def update_custom_map(self, mapping):
        """レコードごとに異なるカスタム値を設定"""
        for zc, custom in mapping.items():
            update_custom(zc, custom)
        return f"[OK] カスタム項目を更新しました ({len(mapping)} 件)"

