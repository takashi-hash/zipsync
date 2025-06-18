import os
from typing import Literal
from .db_manager import remove_by_zipcode
from .data_loader import load_csv_from_zip
from .db_manager import insert_all
from .log_manager import append_log
from .models import create_log_entry


def apply_add_zip(zip_path: str, download_url: str = ""):
    """追加データを登録し、履歴を記録"""
    records = load_csv_from_zip(zip_path)
    if not records:
        print(f"[WARN] データが空: {zip_path}")
        return

    insert_all(records)
    log = create_log_entry(
        source_file=os.path.basename(zip_path),
        file_type="add",
        records=records,
        url=download_url
    )
    append_log(log)
    print(f"[OK] {len(records)} 件を追加しました。")


def apply_del_zip(zip_path: str, download_url: str = ""):
    """削除データを削除し、履歴を記録"""
    records = load_csv_from_zip(zip_path)
    if not records:
        print(f"[WARN] データが空: {zip_path}")
        return

    for record in records:
        remove_by_zipcode(record["zipcode"])

    log = create_log_entry(
        source_file=os.path.basename(zip_path),
        file_type="del",
        records=records,
        url=download_url
    )
    append_log(log)
    print(f"[OK] {len(records)} 件を削除しました。")
