import os
from japanpost_backend.data_loader import load_csv_from_zip
from japanpost_backend.db_manager import clear_all, insert_all
from japanpost_backend.log_manager import append_log
from japanpost_backend.models import create_log_entry


def bulk_register(zip_path: str, download_url: str = ""):
    if not os.path.exists(zip_path):
        print(f"[ERROR] ファイルが見つかりません: {zip_path}")
        return

    print("[INFO] 既存データを全件削除中...")
    clear_all()

    print(f"[INFO] ファイル読込中: {zip_path}")
    records = load_csv_from_zip(zip_path)
    if not records:
        print("[WARN] データが空です。中断します。")
        return

    print(f"[INFO] {len(records)} 件 登録中...")
    insert_all(records)

    log_entry = create_log_entry(
        source_file=os.path.basename(zip_path),
        file_type="all",  # ← ← ここだけ"add"ではなく"all"
        records=records[:5],  # ログには例として先頭5件だけ記録
        url=download_url
    )
    append_log(log_entry)

    print(f"[OK] 一括登録が完了しました（{len(records)} 件）")
