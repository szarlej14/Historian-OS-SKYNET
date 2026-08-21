#!/usr/bin/env python3
"""Validate and index both current and legacy Historian OS records."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INDEX = ROOT / "index"
CATALOG = INDEX / "catalog.json"

# These fields define the minimum identity of a usable Historian record.
REQUIRED = ("id", "title", "corpus", "status")
STATUSES = {"draft", "review", "verified", "archived"}
ID_RE = re.compile(r"^HOS-[A-Z0-9-]+$")

records = []
ids = {}
errors = []
warnings = []

for path in sorted(DATA.glob("*.json")):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name}: invalid JSON: {exc}")
        continue

    if not isinstance(obj, dict):
        errors.append(f"{path.name}: root must be an object")
        continue

    missing = [key for key in REQUIRED if key not in obj]
    if missing:
        errors.append(f"{path.name}: missing required fields: {', '.join(missing)}")
        continue

    record_id = obj["id"]
    if not isinstance(record_id, str) or not ID_RE.match(record_id):
        errors.append(f"{path.name}: invalid id: {record_id!r}")
        continue

    if record_id in ids:
        errors.append(f"duplicate id {record_id}: {ids[record_id]} and {path.name}")
        continue
    ids[record_id] = path.name

    if obj["status"] not in STATUSES:
        errors.append(f"{path.name}: invalid status: {obj['status']!r}")

    sources = obj.get("sources", [])
    if "sources" not in obj:
        warnings.append(f"{path.name}: legacy record without sources; using []")
    elif not isinstance(sources, list):
        errors.append(f"{path.name}: sources must be an array")
        sources = []

    if "created_at" not in obj:
        warnings.append(f"{path.name}: legacy record without created_at; using null")

    relations = obj.get("relations", [])
    if not isinstance(relations, list):
        errors.append(f"{path.name}: relations must be an array")
        relations = []

    records.append({
        "id": record_id,
        "title": obj["title"],
        "corpus": obj["corpus"],
        "category": obj.get("category", ""),
        "status": obj["status"],
        "date": obj.get("date"),
        "source_count": len(sources),
        "relation_count": len(relations),
        "created_at": obj.get("created_at"),
        "file": f"data/{path.name}"
    })

for path in sorted(DATA.glob("*.json")):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(obj, dict):
        continue
    for relation in obj.get("relations", []):
        target = None
        if isinstance(relation, str):
            target = relation
        elif isinstance(relation, dict):
            target = relation.get("target") or relation.get("to")
        if isinstance(target, str) and target not in ids:
            warnings.append(f"{path.name}: relation target not found: {target}")

records.sort(key=lambda item: item["id"])

catalog = {
    "type": "catalog",
    "version": "0.2.0",
    "generated_by": "scripts/sync_catalog.py",
    "record_count": len(records),
    "records": records
}
INDEX.mkdir(parents=True, exist_ok=True)
CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for warning in warnings:
    print(f"WARNING: {warning}")

if errors:
    for error in errors:
        print(f"ERROR: {error}")
    raise SystemExit(1)

print(f"OK: validated {len(records)} records")
print(f"OK: catalog written to {CATALOG.relative_to(ROOT)}")
if warnings:
    print(f"WARNING: {len(warnings)} warning(s)")
