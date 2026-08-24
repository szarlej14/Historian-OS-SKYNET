#!/usr/bin/env python3
"""Normalize legacy HOS JSON records to schema v0.1.0 requirements."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MIGRATION_TIME = datetime.now(timezone.utc).isoformat(timespec="seconds")
changed = 0

for path in sorted(DATA.glob("*.json")):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(obj, dict) or not str(obj.get("id", "")).startswith("HOS-"):
        continue

    dirty = False
    if "sources" not in obj:
        obj["sources"] = []
        dirty = True
    if "created_at" not in obj:
        obj["created_at"] = MIGRATION_TIME
        dirty = True

    if dirty:
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed += 1
        print(f"MIGRATED: {path.name}")

print(f"OK: normalized {changed} record(s)")
print("NOTE: records without an original source now have sources=[] and should be sourced later.")
