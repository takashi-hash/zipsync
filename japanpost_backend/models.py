from typing import Dict, List


def create_address_entry(row: List[str]) -> Dict:
    return {
        "zipcode": row[2],
        "pref": row[6],
        "city": row[7],
        "town": row[8],
        "kana": {
            "pref": row[3],
            "city": row[4],
            "town": row[5],
        },
        "custom": {}  # 後からUIで編集
    }


def create_log_entry(source_file: str, file_type: str, records: List[Dict], url: str) -> Dict:
    return {
        "source_file": source_file,
        "type": file_type,  # "add" or "del"
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "record_count": len(records),
        "download_url": url,
        "details": [{"zipcode": r["zipcode"], "pref": r["pref"], "town": r["town"]} for r in records]
    }
