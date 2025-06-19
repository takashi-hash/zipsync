def test_update_custom_fields(temp_env):
    env = temp_env
    ctrl = env["reload"]("controller").Controller()
    db = env["reload"]("japanpost_backend.db_manager")
    m = env["reload"]("japanpost_backend.models")
    recs = [m.create_address_entry([
        "13101", "1000001", "1000001",
        "トウキョウト", "チヨダク", "イチバンチョウ",
        "東京都", "千代田区", "一番町",
        "0", "0", "0", "0", "0", "0",
    ])]
    db.insert_all(recs)
    msg = ctrl.update_custom_fields(["1000001"], {"メモ": "test"})
    assert "更新" in msg
    rec = db.get_by_zipcode("1000001")
    assert rec["custom"]["メモ"] == "test"
