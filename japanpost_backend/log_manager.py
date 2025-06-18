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
