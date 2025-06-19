
def test_create_address_entry(temp_env):
    models = temp_env["reload"]("japanpost_backend.models")
    row = [
        "13101", "1000001", "1000001",
        "トウキョウト", "チヨダク", "イチバンチョウ",
        "東京都", "千代田区", "一番町",
        "0", "0", "0", "0", "0", "0",
    ]
    addr = models.create_address_entry(row)
    assert addr["zipcode"] == "1000001"
    assert addr["pref"] == "東京都"
    assert addr["city"] == "千代田区"
    assert addr["town"] == "一番町"
    assert addr["kana"]["pref"] == "トウキョウト"


def test_create_log_entry(temp_env):
    models = temp_env["reload"]("japanpost_backend.models")
    records = [
        {"zipcode": "1000001", "pref": "東京都", "city": "千代田区", "town": "一番町"}
    ]
    log = models.create_log_entry("src.zip", "add", records, "http://example.com/src.zip")
    assert log["source_file"] == "src.zip"
    assert log["type"] == "add"
    assert log["record_count"] == 1
    assert len(log["details"]) == 1
    assert log["details"][0]["zipcode"] == "1000001"
