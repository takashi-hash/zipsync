# 取込履歴ファイルの管理
import json
import os

LOG_PATH = os.path.join("data", "import_log.json")


def load_logs():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_logs(logs):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def append_log(entry):
    logs = load_logs()
    logs.append(entry)
    save_logs(logs)


def delete_log(index: int) -> bool:
    """指定の履歴を物理削除"""
    logs = load_logs()
    if index < 0 or index >= len(logs):
        return False
    logs.pop(index)
    save_logs(logs)
    return True


def get_logs(page: int = 1, per_page: int = 30):
    """ページ分割した履歴と総数を返す"""
    logs = load_logs()
    total = len(logs)
    start = max(page - 1, 0) * per_page
    end = start + per_page
    result = []
    for i, log in enumerate(logs[start:end], start=start):
        entry = log.copy()
        entry["index"] = i
        result.append(entry)
    return result, total
