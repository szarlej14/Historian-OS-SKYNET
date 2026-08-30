#!/usr/bin/env python3
"""Validate Historian OS SKYNET JSON records without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ID_RE = re.compile(r"^HOS-[A-Z0-9-]+$")
STATUSES = {"draft", "review", "verified", "archived"}
CORE_FIELDS = ("id", "title", "corpus", "status")
FULL_FIELDS = ("sources", "created_at")


def is_index_record(record: dict, path: Path) -> bool:
    """Index/seed records are metadata records and may omit full provenance fields."""
    return (
        "-INDEX-" in path.stem
        or "scope" in record
        or "records" in record
        or "seed_records" in record
    )


def valid_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_file(path: Path, known_ids: set[str]) -> list[str]:
    errors: list[str] = []
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.relative_to(ROOT)}: invalid JSON ({exc})"]

    if not isinstance(record, dict):
        return [f"{path.relative_to(ROOT)}: top-level value must be an object"]

    for field in CORE_FIELDS:
        if field not in record:
            errors.append(f"{path.relative_to(ROOT)}: missing required field '{field}'")

    record_id = record.get("id")
    if not isinstance(record_id, str) or not ID_RE.fullmatch(record_id):
        errors.append(f"{path.relative_to(ROOT)}: invalid id '{record_id}'")
    elif record_id in known_ids:
        errors.append(f"{path.relative_to(ROOT)}: duplicate id '{record_id}'")

    if not isinstance(record.get("title"), str) or not record.get("title"):
        errors.append(f"{path.relative_to(ROOT)}: title must be a non-empty string")

    if not isinstance(record.get("corpus"), str) or not record.get("corpus"):
        errors.append(f"{path.relative_to(ROOT)}: corpus must be a non-empty string")

    if record.get("status") not in STATUSES:
        errors.append(f"{path.relative_to(ROOT)}: invalid status '{record.get('status')}'")

    for field in ("tags", "relations"):
        if field in record and not isinstance(record[field], list):
            errors.append(f"{path.relative_to(ROOT)}: '{field}' must be an array")

    if not is_index_record(record, path):
        for field in FULL_FIELDS:
            if field not in record:
                errors.append(f"{path.relative_to(ROOT)}: missing provenance field '{field}'")
        if "sources" in record and not isinstance(record["sources"], list):
            errors.append(f"{path.relative_to(ROOT)}: 'sources' must be an array")
        if "created_at" in record and not valid_datetime(record["created_at"]):
            errors.append(f"{path.relative_to(ROOT)}: invalid created_at timestamp")

    return errors


def main() -> int:
    if not DATA_DIR.exists():
        print("ERROR: data/ directory not found")
        return 1

    files = sorted(DATA_DIR.glob("*.json"))
    if not files:
        print("ERROR: no JSON records found in data/")
        return 1

    errors: list[str] = []
    known_ids: set[str] = set()

    # First pass: parse and collect IDs so relation checks can be deterministic.
    records: list[tuple[Path, dict]] = []
    for path in files:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(record, dict):
            records.append((path, record))
            record_id = record.get("id")
            if isinstance(record_id, str):
                if record_id in known_ids:
                    errors.append(f"{path.relative_to(ROOT)}: duplicate id '{record_id}'")
                known_ids.add(record_id)

    for path, _ in records:
        errors.extend(validate_file(path, set()))

    for path, record in records:
        relations = record.get("relations", [])
        if isinstance(relations, list):
            for relation in relations:
                if isinstance(relation, str) and relation not in known_ids:
                    errors.append(
                        f"{path.relative_to(ROOT)}: relation points to missing id '{relation}'"
                    )

    if errors:
        print(f"VALIDATION FAILED: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"VALIDATION OK: {len(files)} JSON file(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
