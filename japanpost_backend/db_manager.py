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
    """Insert multiple address records."""
    db.insert_multiple(records)


def clear_all():
    """Remove all records from the database."""
    db.truncate()


def remove_by_zipcode(zipcode: str):
    """Delete record matching the given zip code."""
    db.remove(Address.zipcode == zipcode)


def update_custom(zipcode: str, custom: dict):
    """Update custom data for a record."""
    db.update({"custom": custom}, Address.zipcode == zipcode)


def get_all() -> List[Dict]:
    """Return all address records."""
    return db.all()


def count_records() -> int:
    """Return the number of address records."""
    return len(db)
