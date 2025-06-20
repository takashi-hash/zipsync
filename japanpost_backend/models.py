# 住所データおよびログエントリを生成するモデル

from typing import Dict, List


def create_address_entry(row: List[str]) -> Dict:
    """CSV の1行から住所レコードを生成"""
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
    """ログエントリを生成"""
    return {
        "source_file": source_file,
        "type": file_type,  # "add" or "del"
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "record_count": len(records),
        "download_url": url,
        "details": [{
            "zipcode": r.get("zipcode", ""),
            "pref": r.get("pref", ""),
            "city": r.get("city", ""),
            "town": r.get("town", "")
        } for r in records]
    }
