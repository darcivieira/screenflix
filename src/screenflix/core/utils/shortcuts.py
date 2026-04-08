import json

from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parents[4]

def get_json_schemas() -> dict:
    schemas_path = _BASE_DIR / "schemas.json"
    with open(schemas_path, "r") as f:
        return json.load(f)