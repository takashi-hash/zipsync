import json
from collections import defaultdict
from typing import Callable, Dict, List, Any

import pandas as pd


# ========== I/O ==========

def load_json(path: str) -> Dict[str, Any]:
    """Load JSON file with UTF-8 encoding."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj: dict) -> None:
    """Save mapping as JSON with UTF-8."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ========== Utility ==========

def normalize_zip(zipcode: str) -> str:
    return str(zipcode).zfill(7)


def apply_to_zip(df: pd.DataFrame, zip_key: str) -> pd.DataFrame:
    df[zip_key] = df[zip_key].apply(normalize_zip)
    return df


# ========== Transformation ==========

def to_grouped_list(
    df: pd.DataFrame,
    zip_key: str,
    group_value_key: str,
    field_name: str,
) -> Dict[str, Dict[str, List[str]]]:
    df = apply_to_zip(df, zip_key)
    grouped = df.groupby(zip_key)[group_value_key].apply(list).to_dict()
    return {k: {field_name: v} for k, v in grouped.items()}


def to_deep_nested_with_values(
    df: pd.DataFrame,
    zip_key: str,
    nest_keys: List[str],
    value_map: Dict[str, List[str]],
    field_name: str,
) -> Dict[str, Dict[str, Any]]:
    df = apply_to_zip(df, zip_key)
    result: Dict[str, Dict[str, Any]] = defaultdict(dict)

    for _, row in df.iterrows():
        zip_val = row[zip_key]
        current = result[zip_val].setdefault(field_name, {})

        for key in nest_keys:
            key_val = row[key]
            next_dict = current.setdefault(key_val, {})

            for vkey in value_map.get(key, []):
                if vkey in row:
                    next_dict[vkey] = row[vkey]
            current = next_dict

    return result


def to_dict(
    df: pd.DataFrame,
    zip_key: str,
    value_keys: List[str],
    field_name: str = None,
) -> Dict[str, Dict[str, Any]]:
    df = apply_to_zip(df, zip_key)
    result: Dict[str, Dict[str, Any]] = defaultdict(dict)
    for _, row in df.iterrows():
        zip_val = row[zip_key]
        values = {key: row.get(key, "") for key in value_keys}
        if field_name:
            result[zip_val][field_name] = values
        else:
            result[zip_val].update(values)
    return result


# ========== Merge ==========

def merge_dicts(a: dict, b: dict) -> dict:
    return {**a, **b}


# ========== Source Loader ==========

def create_loader(
    path: str,
    sheet: str,
    method: str,
    args: dict,
    field_name: str = None,
) -> Callable[[], Dict[str, dict]]:
    def load() -> Dict[str, dict]:
        df = pd.read_excel(path, sheet_name=sheet, dtype=str).fillna("")
        if method == "grouped_list":
            return to_grouped_list(df, field_name=field_name, **args)
        if method == "deep_nested_with_values":
            return to_deep_nested_with_values(df, field_name=field_name, **args)
        if method == "dict":
            return to_dict(df, field_name=field_name, **args)
        raise ValueError(f"Unsupported method: {method}")

    return load


# ========== Custom Builder ==========

def build_customs(loaders: List[Callable[[], Dict[str, dict]]]) -> Dict[str, dict]:
    customs: Dict[str, dict] = {}
    for load_fn in loaders:
        part = load_fn()
        for zip_key, values in part.items():
            customs[zip_key] = merge_dicts(customs.get(zip_key, {}), values)
    return customs


# ========== Injection ==========

def inject_customs(
    address_dict: dict,
    customs: Dict[str, dict],
    zip_field: str = "zipcode",
) -> None:
    for _, data in address_dict.get("_default", {}).items():
        zipcode = normalize_zip(data.get(zip_field, ""))
        if zipcode in customs:
            data["custom"] = customs[zipcode]


# ========== Main Execution ==========

def update_address_json(
    json_path: str,
    excel_path: str,
    loaders: List[Callable[[], Dict[str, dict]]],
    output_path: str,
) -> None:
    address_dict = load_json(json_path)
    customs = build_customs(loaders)
    inject_customs(address_dict, customs)
    save_json(output_path, address_dict)
