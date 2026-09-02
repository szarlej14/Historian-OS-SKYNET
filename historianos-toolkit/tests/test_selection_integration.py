#!/usr/bin/env python3
"""HistorianOS catalog integration smoke test.
Validates the current repository data contract and generated catalog.
Run from historianos-toolkit: python tests/test_selection_integration.py
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "sync_catalog.py"
CATALOG = ROOT / "index" / "catalog.json"

def run():
    p = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert p.returncode == 0, ("sync_catalog failed", p.stdout, p.stderr)
    assert CATALOG.exists(), "index/catalog.json missing"
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert data["type"] == "catalog"
    assert data["record_count"] > 0
    ids = {item["id"] for item in data["records"]}
    assert "HOS-FOOT-WISLA-OPROIESCU-2013-001" in ids
    print("PASS catalog pipeline:", data["record_count"], "records")

if __name__ == "__main__":
    run()
