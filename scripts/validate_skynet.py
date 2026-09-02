#!/usr/bin/env python3
"""Validate the complete Historian OS SKYNET derived layer stack.

Runs source-record validation first, then rebuilds all analytical indexes.
Returns non-zero when canonical records are invalid.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / "scripts" / "sync_catalog.py"
LAYERS = ROOT / "scripts" / "layers.py"
ENTITY = ROOT / "scripts" / "entity_resolution.py"
TEMPORAL = ROOT / "scripts" / "temporal_engine.py"

def run(script, label):
    result = subprocess.run([sys.executable, str(script), "all"] if script == LAYERS
                            else [sys.executable, str(script)],
                            cwd=ROOT, text=True)
    if result.returncode:
        print(f"FAILED: {label}")
        return False
    print(f"OK: {label}")
    return True

def main():
    if not run(SYNC, "canonical records"):
        return 1
    if not run(LAYERS, "analytics layers"):
        return 1
    if not run(ENTITY, "entity resolution candidates"):
        return 1
    if not run(TEMPORAL, "temporal engine"):
        return 1
    print("OK: SKYNET integrity pipeline complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
