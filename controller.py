from japanpost_backend.file_fetcher import download_zip
from japanpost_backend.bulk_register import bulk_register
from japanpost_backend.diff_applier import apply_add_zip, apply_del_zip
from japanpost_backend.db_manager import get_all, clear_all
from japanpost_backend.search_manager import search_with_filters


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
                         page: int = 1, per_page: int = 30):
        results, total = search_with_filters(zipcode, pref, city, page, per_page)
        data = [(r["zipcode"], r["pref"], r["city"], r["town"]) for r in results]
        return data, total

    def clear_database(self):
        """Remove all address records."""
        try:
            clear_all()
            return "[OK] 全データを削除しました"
        except Exception as e:
            return f"[ERROR] 全データ削除失敗: {e}"

