from typing import List, Dict, Tuple
from functools import reduce
from tinydb import Query

from .db_manager import db

Address = Query()


def search_partial(partial: str) -> List[Dict]:
    """Return records whose fields contain the given keyword."""
    if not partial:
        return []
    return db.search(
        (Address.zipcode.search(partial)) |
        (Address.pref.search(partial)) |
        (Address.city.search(partial)) |
        (Address.town.search(partial)) |
        (Address.custom.test(lambda c: partial in str(c)))
    )


def search_with_filters(
    zipcode: str = "",
    pref: str = "",
    city: str = "",
    page: int = 1,
    per_page: int = 30,
) -> Tuple[List[Dict], int]:
    """Search addresses with optional filters and pagination."""
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
