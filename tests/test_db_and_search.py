
def sample_records(models):
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
    return [models.create_address_entry(row1), models.create_address_entry(row2)]


def test_db_operations_and_search(temp_env):
    env = temp_env
    db_manager = env["reload"]("japanpost_backend.db_manager")
    search_manager = env["reload"]("japanpost_backend.search_manager")
    models = env["reload"]("japanpost_backend.models")

    records = sample_records(models)
    db_manager.insert_all(records)
    assert db_manager.count_records() == 2

    results, total = search_manager.search_with_filters(zipcode="1000001")
    assert total == 1
    assert results[0]["town"] == "一番町"

    db_manager.remove_by_zipcode("1000002")
    assert db_manager.count_records() == 1

    db_manager.clear_all()
    assert db_manager.count_records() == 0


def test_search_multiple(temp_env):
    env = temp_env
    db_manager = env["reload"]("japanpost_backend.db_manager")
    search_manager = env["reload"]("japanpost_backend.search_manager")
    models = env["reload"]("japanpost_backend.models")

    records = sample_records(models)
    db_manager.insert_all(records)

    filters = [
        {"zipcode": "1000001"},
        {"town": "二番町"},
    ]

    results, total = search_manager.search_multiple(filters)
    assert total == 2
    towns = sorted([r["town"] for r in results])
    assert towns == ["一番町", "二番町"]
