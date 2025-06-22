import json
from collections import defaultdict
from typing import Tuple, Dict, Any
import pandas as pd


def load_json(path: str) -> Dict[str, Any]:
    """Load JSON file with UTF-8 encoding."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_data_strict(json_path: str, excel_path: str) -> Tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load JSON and three sheets from Excel as string DataFrames."""
    address_dict = load_json(json_path)
    entries_df = pd.read_excel(excel_path, sheet_name="entries", dtype=str).fillna("")
    courses_df = pd.read_excel(excel_path, sheet_name="course_codes", dtype=str).fillna("")
    variants_df = pd.read_excel(excel_path, sheet_name="pickup_variants", dtype=str).fillna("")
    return address_dict, entries_df, courses_df, variants_df


def normalize_entries(df: pd.DataFrame) -> Dict[str, dict]:
    """Return mapping from zipcode to entry dict."""
    return {
        str(row["zipcode"]).zfill(7): {
            "office_code": row.get("office_code", ""),
            "destination_name": row.get("destination_name", ""),
            "shiwake_code": row.get("shiwake_code", ""),
        }
        for _, row in df.iterrows()
    }


def normalize_course_codes(df: pd.DataFrame) -> Dict[str, list]:
    """Return mapping from zipcode to list of course codes."""
    df["zipcode"] = df["zipcode"].apply(lambda x: str(x).zfill(7))
    grouped = df.groupby("zipcode")["course_code"].apply(list)
    return grouped.to_dict()


def normalize_pickup_variants(df: pd.DataFrame) -> Dict[str, dict]:
    """Return mapping from zipcode to pickup variants mapping."""
    df["zipcode"] = df["zipcode"].apply(lambda x: str(x).zfill(7))
    result = defaultdict(lambda: defaultdict(dict))
    for _, row in df.iterrows():
        result[row["zipcode"]][row["pickup_location"]][row["delivery_type"]] = {
            "destination_name": row["destination_name"],
            "shiwake_code": row["shiwake_code"],
        }
    return result


def build_customs(entries: Dict[str, dict], courses: Dict[str, list], variants: Dict[str, dict]) -> Dict[str, dict]:
    """Build custom object per zipcode."""
    customs = {}
    for zipcode, entry in entries.items():
        custom = {}
        if entry.get("office_code"):
            custom["office_code"] = entry["office_code"]
        if entry.get("destination_name") and entry.get("shiwake_code"):
            custom["destination_name"] = entry["destination_name"]
            custom["shiwake_code"] = entry["shiwake_code"]
        if zipcode in courses:
            custom["course_codes"] = courses[zipcode]
        if zipcode in variants:
            custom["pickup_variants"] = variants[zipcode]
        customs[zipcode] = custom
    return customs


def inject_customs(address_dict: dict, customs: Dict[str, dict]) -> None:
    """Replace custom section in address entries."""
    for _, data in address_dict.get("_default", {}).items():
        zipcode = str(data.get("zipcode", "")).zfill(7)
        if zipcode in customs:
            data["custom"] = customs[zipcode]


def save_json(path: str, obj: dict) -> None:
    """Save mapping as JSON with UTF-8."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
