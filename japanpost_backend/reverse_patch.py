# 履歴を取り消す処理

from .db_manager import insert_all, remove_by_zipcode
from .log_manager import load_logs
from typing import Literal


def reverse_log_entry(index: int) -> str:
    """指定履歴の効果を取り消して結果を返す"""
    logs = load_logs()
    if index < 0 or index >= len(logs):
        return f"[ERROR] 指定インデックスが無効: {index}"

    log = logs[index]
    entry_type: Literal["add", "del"] = log["type"]
    details = log["details"]

    if entry_type == "add":
        # 「追加ログ」を取り消す → 削除する
        for record in details:
            remove_by_zipcode(record["zipcode"])
        return f"[REVERSED] add ログ #{index} を取り消しました（{len(details)} 件削除）"

    elif entry_type == "del":
        # 「削除ログ」を復元する → 追加する
        # このとき他の項目(pref/city/town)が必要 → 再構築する
        records = []
        for r in details:
            records.append({
                "zipcode": r["zipcode"],
                "pref": r["pref"],
                "city": r.get("city", ""),  # ログに市区町村があれば使用
                "town": r["town"],
                "kana": {"pref": "", "city": "", "town": ""},
                "custom": {}
            })
        insert_all(records)
        return f"[REVERSED] del ログ #{index} を復元しました（{len(records)} 件追加）"

    else:
        return f"[ERROR] 未知のログタイプ: {entry_type}"
