import csv
import io
import zipfile


def create_zip(path, rows):
    with zipfile.ZipFile(path, "w") as z:
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerows(rows)
        z.writestr("data.csv", buf.getvalue())


def sample_rows():
    row1 = [
        "13101", "1000001", "1000001",
        "トウキョウト", "チヨダク", "イチバンチョウ",
        "東京都", "千代田区", "一番町",
        "0", "0", "0", "0", "0", "0",
    ]
    row2 = [
        "13101", "1000002", "1000002",
        "トウキョウト", "チヨダク", "ニバンチョウ",
        "東京都", "千代田区", "二番町",
        "0", "0", "0", "0", "0", "0",
    ]
    return row1, row2


def test_reverse_and_reapply(temp_env):
    env = temp_env
    db_manager = env["reload"]("japanpost_backend.db_manager")
    log_manager = env["reload"]("japanpost_backend.log_manager")
    reverse_patch = env["reload"]("japanpost_backend.reverse_patch")
    reapply_patch = env["reload"]("japanpost_backend.reapply_patch")
    models = env["reload"]("japanpost_backend.models")

    row1, row2 = sample_rows()
    rec1 = models.create_address_entry(row1)
    rec2 = models.create_address_entry(row2)

    add_zip = env["resources"] / "add.zip"
    del_zip = env["resources"] / "del.zip"
    create_zip(add_zip, [row1])
    create_zip(del_zip, [row2])

    logs = [
        models.create_log_entry("add.zip", "add", [rec1], ""),
        models.create_log_entry("del.zip", "del", [rec2], ""),
    ]
    log_manager.save_logs(logs)

    db_manager.insert_all([rec1])

    msg1 = reverse_patch.reverse_log_entry(0)
    assert "取り消しました" in msg1
    assert db_manager.count_records() == 0

    msg2 = reverse_patch.reverse_log_entry(1)
    assert "復元しました" in msg2
    assert db_manager.count_records() == 1
    assert db_manager.get_all()[0]["zipcode"] == rec2["zipcode"]

    db_manager.clear_all()

    msg3 = reapply_patch.reapply_log_entry(0)
    assert "再実行しました" in msg3
    assert db_manager.count_records() == 1

    msg4 = reapply_patch.reapply_log_entry(1)
    assert "再実行しました" in msg4
    assert db_manager.count_records() == 1
