#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INDEX = ROOT / "index"
CATALOG = INDEX / "catalog.json"

REQUIRED = ("id", "title", "corpus", "status", "sources", "created_at")
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

    if not isinstance(obj["sources"], list):
        errors.append(f"{path.name}: sources must be an array")

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
        "source_count": len(obj["sources"]) if isinstance(obj["sources"], list) else 0,
        "relation_count": len(relations),
        "file": f"data/{path.name}"
    })

for path in sorted(DATA.glob("*.json")):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    for target in obj.get("relations", []) if isinstance(obj, dict) else []:
        if isinstance(target, str) and target not in ids:
            warnings.append(f"{path.name}: relation target not found: {target}")

records.sort(key=lambda item: item["id"])

catalog = {
    "type": "catalog",
    "version": "0.1.0",
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
    print(f"WARNING: {len(warnings)} dangling relation(s)")
