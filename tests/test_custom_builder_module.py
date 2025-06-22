import pandas as pd
from unittest.mock import mock_open

def test_custom_builder_pipeline(temp_env, monkeypatch):
    env = temp_env
    cb = env["reload"]("japanpost_backend.custom_builder")

    # sample data
    address_dict = {"_default": {"row1": {"zipcode": "1234567"}}}
    entries_df = pd.DataFrame([
        {"zipcode": "1234567", "office_code": "O1", "destination_name": "D1", "shiwake_code": "S1"}
    ])
    courses_df = pd.DataFrame([
        {"zipcode": "1234567", "course_code": "C1"}
    ])
    variants_df = pd.DataFrame([
        {"zipcode": "1234567", "pickup_location": "L1", "delivery_type": "T1", "destination_name": "VD1", "shiwake_code": "VS1"}
    ])

    # mock file loaders
    monkeypatch.setattr(cb, "load_json", lambda path: address_dict)
    def fake_read_excel(path, sheet_name=None, dtype=str):
        if sheet_name == "entries":
            return entries_df
        if sheet_name == "course_codes":
            return courses_df
        if sheet_name == "pickup_variants":
            return variants_df
        return pd.DataFrame()
    monkeypatch.setattr(cb.pd, "read_excel", fake_read_excel)

    # capture save_json output
    saved = {}
    m = mock_open()
    monkeypatch.setattr("builtins.open", m)
    monkeypatch.setattr(cb.json, "dump", lambda obj, f, ensure_ascii=False, indent=2: saved.update(obj))

    adict, e_df, c_df, v_df = cb.load_data_strict("addr.json", "data.xlsx")
    customs = cb.build_customs(
        cb.normalize_entries(e_df),
        cb.normalize_course_codes(c_df),
        cb.normalize_pickup_variants(v_df)
    )
    cb.inject_customs(adict, customs)
    cb.save_json("addr.json", adict)

    custom = saved["_default"]["row1"]["custom"]
    assert custom["office_code"] == "O1"
    assert custom["course_codes"] == ["C1"]
    assert custom["pickup_variants"]["L1"]["T1"]["destination_name"] == "VD1"

