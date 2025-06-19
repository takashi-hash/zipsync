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
    """Physically remove a log entry by index."""
    logs = load_logs()
    if index < 0 or index >= len(logs):
        return False
    logs.pop(index)
    save_logs(logs)
    return True


def get_logs(page: int = 1, per_page: int = 30):
    """Return paginated logs and total count."""
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
