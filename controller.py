from japanpost_backend.file_fetcher import download_zip
from japanpost_backend.bulk_register import bulk_register
from japanpost_backend.diff_applier import apply_add_zip, apply_del_zip


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
