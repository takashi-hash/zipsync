from tinydb import TinyDB, Query
from functools import reduce
from typing import List, Dict, Tuple
import os

DB_DIR = os.path.join(os.getcwd(), "data")
DB_PATH = os.path.join(DB_DIR, "address.json")

# ディレクトリがなければ作成
os.makedirs(DB_DIR, exist_ok=True)

db = TinyDB(DB_PATH)
Address = Query()


def insert_all(records):
    db.insert_multiple(records)


def search(partial: str):
    return db.search((Address.zipcode.matches(partial)) |
                     (Address.pref.matches(partial)) |
                     (Address.city.matches(partial)) |
                     (Address.town.matches(partial)) |
                     (Address.custom.test(lambda c: partial in str(c))))


def clear_all():
    db.truncate()


def remove_by_zipcode(zipcode: str):
    db.remove(Address.zipcode == zipcode)


def update_custom(zipcode: str, custom: dict):
    db.update({"custom": custom}, Address.zipcode == zipcode)


def get_all() -> List[Dict]:
    """Return all address records."""
    return db.all()


def search_with_filters(zipcode: str = "", pref: str = "", city: str = "",
                        page: int = 1, per_page: int = 30) -> Tuple[List[Dict], int]:
    """Search addresses with optional filters and pagination.

    Parameters
    ----------
    zipcode : str
        Zip code to match exactly.
    pref : str
        Prefecture name to match exactly.
    city : str
        City name to match exactly.
    page : int
        1-based page number.
    per_page : int
        Number of records per page.

    Returns
    -------
    Tuple[List[Dict], int]
        A list of matched address dictionaries for the requested page and the
        total number of matched records.
    """

    conditions = []
    if zipcode:
        conditions.append(Address.zipcode == zipcode)
    if pref:
        conditions.append(Address.pref == pref)
    if city:
        conditions.append(Address.city == city)

    if conditions:
        query = reduce(lambda a, b: a & b, conditions)
        matched = db.search(query)
    else:
        matched = db.all()

    total = len(matched)
    start = max(page - 1, 0) * per_page
    end = start + per_page
    return matched[start:end], total
