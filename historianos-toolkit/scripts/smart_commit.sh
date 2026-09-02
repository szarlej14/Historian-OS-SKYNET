#!/usr/bin/env bash
set -euo pipefail
python3 scripts/validate.py .
git add .
git commit -m "chore: validated SKYNET update"
