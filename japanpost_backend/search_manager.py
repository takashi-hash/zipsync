# 住所データの検索機能

from typing import List, Dict, Tuple
from functools import reduce
from tinydb import Query

from .db_manager import db

Address = Query()


def search_partial(partial: str) -> List[Dict]:
    """部分一致検索を行う"""
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
    town: str = "",
    page: int = 1,
    per_page: int = 30,
) -> Tuple[List[Dict], int]:
    """各種フィルタで検索しページ分割する"""
    conditions = []
    if zipcode:
        conditions.append(Address.zipcode.search(zipcode))
    if pref:
        conditions.append(Address.pref.search(pref))
    if city:
        conditions.append(Address.city.search(city))
    if town:
        conditions.append(Address.town.search(town))

    if conditions:
        query = reduce(lambda a, b: a & b, conditions)
        matched = db.search(query)
    else:
        matched = db.all()

    total = len(matched)
    start = max(page - 1, 0) * per_page
    end = start + per_page
    return matched[start:end], total


def search_multiple(filters: List[Dict], page: int = 1, per_page: int = 30) -> Tuple[List[Dict], int]:
    """複数条件の結果を結合して返す"""
    combined = []
    for f in filters:
        z = f.get("zipcode", "")
        p = f.get("pref", "")
        c = f.get("city", "")
        t = f.get("town", "")
        results, _ = search_with_filters(z, p, c, t, page=1, per_page=len(db))
        combined.extend(results)

    unique = []
    seen = set()
    for r in combined:
        key = (r.get("zipcode"), r.get("pref"), r.get("city"), r.get("town"))
        if key not in seen:
            seen.add(key)
            unique.append(r)

    total = len(unique)
    start = max(page - 1, 0) * per_page
    end = start + per_page
    return unique[start:end], total
