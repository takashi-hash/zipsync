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
from japanpost_backend.search_manager import search_with_filters
from japanpost_backend.log_manager import get_logs, delete_log
from japanpost_backend.reverse_patch import reverse_log_entry


class Controller:
    def bulk_register(self, url: str):
        try:
            path = download_zip(url)
            bulk_register(path, url)
            return f"[OK] 一括登録成功: {url}"
        except Exception as e:
            return f"[ERROR] 一括登録失敗: {e}"

    def apply_add(self, url: str):
        try:
            path = download_zip(url)
            apply_add_zip(path, url)
            return f"[OK] 差分追加成功: {url}"
        except Exception as e:
            return f"[ERROR] 差分追加失敗: {e}"

    def apply_del(self, url: str):
        try:
            path = download_zip(url)
            apply_del_zip(path, url)
            return f"[OK] 差分削除成功: {url}"
        except Exception as e:
            return f"[ERROR] 差分削除失敗: {e}"

    def get_all_addresses(self):
        records = get_all()
        return [(r["zipcode"], r["pref"], r["city"], r["town"]) for r in records]

    def search_addresses(self, zipcode: str = "", pref: str = "", city: str = "",
                         town: str = "", page: int = 1, per_page: int = 30):
        results, total = search_with_filters(zipcode, pref, city, town,
                                            page, per_page)
        data = [(r["zipcode"], r["pref"], r["city"], r["town"]) for r in results]
        return data, total

    def clear_database(self):
        """Remove all address records."""
        try:
            clear_all()
            return "[OK] 全データを削除しました"
        except Exception as e:
            return f"[ERROR] 全データ削除失敗: {e}"

    def get_record_count(self) -> int:
        """Return number of records in the database."""
        return count_records()

    def get_record(self, zipcode: str):
        """Return a single record by zipcode or None."""
        return get_by_zipcode(zipcode)

    # --- log handling ---
    def fetch_logs(self, page: int = 1, per_page: int = 30):
        """Return paginated import logs and total count."""
        return get_logs(page, per_page)

    def reverse_logs(self, indices):
        msgs = []
        for idx in sorted(indices):
            msgs.append(reverse_log_entry(idx))
        return "\n".join(msgs)

    def delete_logs(self, indices):
        for idx in sorted(indices, reverse=True):
            delete_log(idx)
        return "[OK] 履歴を削除しました"

    def reapply_logs(self, indices):
        msgs = []
        for idx in sorted(indices):
            msgs.append(reapply_log_entry(idx))
        return "\n".join(msgs)

    # --- custom field handling ---
    def update_custom_fields(self, zipcodes, custom):
        """Apply the same custom dict to multiple records."""
        for zc in zipcodes:
            update_custom(zc, custom)
        return f"[OK] カスタム項目を更新しました ({len(zipcodes)} 件)"

    def update_custom_map(self, mapping):
        """Apply different custom dicts for multiple records."""
        for zc, custom in mapping.items():
            update_custom(zc, custom)
        return f"[OK] カスタム項目を更新しました ({len(mapping)} 件)"

