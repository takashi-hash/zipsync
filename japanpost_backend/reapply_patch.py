import os
from typing import Literal
from .file_fetcher import download_zip
from .diff_applier import (
    apply_add_zip_without_log,
    apply_del_zip_without_log,
)
from .log_manager import load_logs

RESOURCE_DIR = "resources"


def reapply_log_entry(index: int) -> str:
    """Reapply the import corresponding to a log entry without creating logs."""
    logs = load_logs()
    if index < 0 or index >= len(logs):
        return f"[ERROR] 指定インデックスが無効: {index}"

    log = logs[index]
    entry_type: Literal["add", "del"] = log.get("type")
    url = log.get("download_url", "")
    src = log.get("source_file", "")

    try:
        # get zip path (download again if needed)
        if url:
            zip_path = download_zip(url)
        elif src:
            zip_path = os.path.join(RESOURCE_DIR, src)
            if not os.path.exists(zip_path):
                return f"[ERROR] ZIP が見つかりません: {src}"
        else:
            return f"[ERROR] ZIP 情報がありません: {index}"

        if entry_type == "add":
            apply_add_zip_without_log(zip_path)
            return f"[REAPPLIED] add ログ #{index} を再実行しました"
        elif entry_type == "del":
            apply_del_zip_without_log(zip_path)
            return f"[REAPPLIED] del ログ #{index} を再実行しました"
        else:
            return f"[ERROR] 未知のログタイプ: {entry_type}"
    except Exception as e:
        return f"[ERROR] 再実行失敗: {e}"
