#!/usr/bin/env python3
"""Validate Historian OS SKYNET records against the canonical schema."""

import json
import re
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Missing dependency: jsonschema", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "record.schema.json"
RECORDS_PATH = ROOT / "data" / "records"
ID_RE = re.compile(r"^HOS-[A-Z0-9-]+-[0-9]{6}$")


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    records = sorted(RECORDS_PATH.glob("*.json"))
    records_by_id = {}
    errors = []

    for path in records:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            validator.validate(data)
        except Exception as exc:
            errors.append(f"{path}: {exc}")
            continue

        record_id = data["id"]
        if not ID_RE.fullmatch(record_id):
            errors.append(f"{path}: invalid id format: {record_id}")
        if path.stem != record_id:
            errors.append(f"{path}: filename must match record id {record_id}")
        if record_id in records_by_id:
            errors.append(f"{path}: duplicate id {record_id}")
        records_by_id[record_id] = data

    for record_id, data in records_by_id.items():
        for relation in data["relations"]:
            target = relation["target"]
            if target not in records_by_id:
                errors.append(f"{record_id}: relation target does not exist: {target}")

    if errors:
        print("\n".join(errors))
        return 1

    print(f"Validated {len(records)} record(s) successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
