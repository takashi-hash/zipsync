import csv
import io
import zipfile


def create_zip(path, rows):
    with zipfile.ZipFile(path, "w") as z:
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerows(rows)
        z.writestr("data.csv", buf.getvalue())


def test_load_csv_from_zip(temp_env):
    env = temp_env
    loader = env["reload"]("japanpost_backend.data_loader")
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
    zip_path = env["tmp_path"] / "sample.zip"
    create_zip(zip_path, [row1, row2])

    records = loader.load_csv_from_zip(str(zip_path))
    assert len(records) == 2
    assert records[0]["zipcode"] == "1000001"
    assert records[1]["town"] == "二番町"
