import json

import screenflix.core.utils.shortcuts as shortcuts


def test_get_json_schemas_reads_from_base_dir(tmp_path, monkeypatch):
    schema_file = tmp_path / "schemas.json"
    payload = {"media": {"type": "object"}, "episode": {"type": "object"}}
    schema_file.write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(shortcuts, "_BASE_DIR", tmp_path)

    result = shortcuts.get_json_schemas()

    assert result == payload
