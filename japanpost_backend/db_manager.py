from tinydb import TinyDB, Query
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
