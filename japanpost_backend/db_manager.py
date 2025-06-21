# TinyDB を用いたデータベース操作モジュール
from tinydb import TinyDB, Query
from typing import List, Dict
import os

DB_DIR = os.path.join(os.getcwd(), "data")
DB_PATH = os.path.join(DB_DIR, "address.json")

os.makedirs(DB_DIR, exist_ok=True)

# Use UTF-8 encoding and keep non-ASCII chars as-is
db = TinyDB(DB_PATH, encoding="utf-8", ensure_ascii=False)
Address = Query()


def insert_all(records):
    """住所レコードをまとめて挿入"""
    db.insert_multiple(records)


def clear_all():
    """データベースを空にする"""
    db.truncate()


def remove_by_zipcode(zipcode: str):
    """郵便番号に一致するレコードを削除"""
    db.remove(Address.zipcode == zipcode)


def update_custom(zipcode: str, custom: dict):
    """カスタムデータを更新"""
    db.update({"custom": custom}, Address.zipcode == zipcode)


def get_all() -> List[Dict]:
    """全レコードを取得"""
    return db.all()


def get_by_zipcode(zipcode: str) -> Dict:
    """郵便番号で検索し最初のレコードを返す"""
    result = db.search(Address.zipcode == zipcode)
    return result[0] if result else None


def count_records() -> int:
    """登録件数を返す"""
    return len(db)
