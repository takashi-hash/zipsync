import pandas as pd
from unittest.mock import mock_open


def test_update_address_json_dynamic(temp_env, monkeypatch):
    env = temp_env
    mod = env["reload"]("japanpost_backend.excel_custom_loader")

    address_dict = {"_default": {"row1": {"zipcode": "1234567"}}}
    entries_df = pd.DataFrame([
        {"zipcode": "1234567", "office_code": "O1", "destination_name": "D1", "shiwake_code": "S1"}
    ])
    courses_df = pd.DataFrame([
        {"zipcode": "1234567", "course_code": "C1"}
    ])
    variants_df = pd.DataFrame([
        {
            "zipcode": "1234567",
            "pickup_location": "L1",
            "delivery_type": "T1",
            "destination_name": "VD1",
            "shiwake_code": "VS1",
        }
    ])

    def fake_read_excel(path, sheet_name=None, dtype=str):
        if sheet_name == "entries":
            return entries_df
        if sheet_name == "course_codes":
            return courses_df
        if sheet_name == "pickup_variants":
            return variants_df
        return pd.DataFrame()

    monkeypatch.setattr(mod.pd, "read_excel", fake_read_excel)
    monkeypatch.setattr(mod, "load_json", lambda p: address_dict)

    saved = {}
    m = mock_open()
    monkeypatch.setattr("builtins.open", m)
    monkeypatch.setattr(mod.json, "dump", lambda obj, f, ensure_ascii=False, indent=2: saved.update(obj))

    loaders = [
        mod.create_loader(
            path="dummy.xlsx",
            sheet="entries",
            method="dict",
            args={"zip_key": "zipcode", "value_keys": ["office_code", "destination_name", "shiwake_code"]},
            field_name=None,
        ),
        mod.create_loader(
            path="dummy.xlsx",
            sheet="course_codes",
            method="grouped_list",
            args={"zip_key": "zipcode", "group_value_key": "course_code"},
            field_name="course_codes",
        ),
        mod.create_loader(
            path="dummy.xlsx",
            sheet="pickup_variants",
            method="deep_nested_with_values",
            args={
                "zip_key": "zipcode",
                "nest_keys": ["pickup_location", "delivery_type"],
                "value_map": {
                    "pickup_location": ["destination_name"],
                    "delivery_type": ["shiwake_code"],
                },
            },
            field_name="pickup_variants",
        ),
    ]

    mod.update_address_json("addr.json", "dummy.xlsx", loaders, "out.json")

    custom = saved["_default"]["row1"]["custom"]
    assert custom["office_code"] == "O1"
    assert custom["course_codes"] == ["C1"]
    assert custom["pickup_variants"]["L1"]["destination_name"] == "VD1"
    assert custom["pickup_variants"]["L1"]["T1"]["shiwake_code"] == "VS1"
