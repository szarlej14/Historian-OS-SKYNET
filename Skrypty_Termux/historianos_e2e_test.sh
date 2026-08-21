#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO_URL="https://github.com/szarlej14/Historian-OS-SKYNET.git"
REPO_DIR="${HISTORIAN_REPO_DIR:-$HOME/Historian-OS-SKYNET}"
WORKSPACE="${HISTORIAN_WORKSPACE:-/storage/emulated/0/HistorianOS_Workspace}"
SOURCE_DIR="$WORKSPACE/Zrodla_Surowe"
TEST_ID="HOS-TEST-001"
TEST_FILE="data/${TEST_ID}.json"
TEST_NAME="${TEST_ID}.json"
DRIVE_PATH="${HISTORIAN_DRIVE_PATH:-}"

log() { printf '\n[HOS-E2E] %s\n' "$*"; }
fatal() { printf '\n[HOS-E2E][FAIL] %s\n' "$*" >&2; exit 1; }
sha256() { sha256sum "$1" | awk '{print $1}'; }

log "0/8 Sprawdzam i przygotowuję zależności"
if ! command -v git >/dev/null 2>&1; then
  pkg install -y git || fatal "Nie udało się zainstalować git"
fi
if ! command -v python3 >/dev/null 2>&1; then
  pkg install -y python || fatal "Nie udało się zainstalować Python"
fi
if ! command -v sha256sum >/dev/null 2>&1; then
  pkg install -y coreutils || fatal "Nie udało się zainstalować coreutils"
fi

log "1/8 GitHub → lokalny Historian OS"
if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" fetch origin main
  if [ -n "$(git -C "$REPO_DIR" status --porcelain)" ]; then
    fatal "Lokalne zmiany w repozytorium. Nie nadpisuję ich."
  fi
  git -C "$REPO_DIR" checkout main >/dev/null 2>&1 || true
  git -C "$REPO_DIR" pull --ff-only origin main
else
  git clone "$REPO_URL" "$REPO_DIR"
fi

CANONICAL="$REPO_DIR/$TEST_FILE"
[ -f "$CANONICAL" ] || fatal "Brak kanonicznego rekordu $TEST_FILE"

log "2/8 SHA-256 kanonicznego rekordu"
CANONICAL_SHA="$(sha256 "$CANONICAL")"
echo "GitHub/local canonical: $CANONICAL_SHA"

log "3/8 Historian OS → Workspace/Zrodla_Surowe"
mkdir -p "$SOURCE_DIR"
cp -f "$CANONICAL" "$SOURCE_DIR/$TEST_NAME"
WORKSPACE_SHA="$(sha256 "$SOURCE_DIR/$TEST_NAME")"
echo "Workspace:             $WORKSPACE_SHA"
[ "$CANONICAL_SHA" = "$WORKSPACE_SHA" ] || fatal "SHA-256 GitHub/local != Workspace"

log "4/8 Czekam na lokalny mirror Drive / Syncthing"
if [ -z "$DRIVE_PATH" ]; then
  echo "Nie ustawiono HISTORIAN_DRIVE_PATH."
  echo "Jeśli Drive Sync tworzy lokalny folder, ustaw jego ścieżkę np.:"
  echo '  export HISTORIAN_DRIVE_PATH="/storage/emulated/0/NAZWA_FOLDERU"'
  echo "Dla pełnego PASS skrypt musi widzieć lokalny mirror Drive."
else
  [ -d "$DRIVE_PATH" ] || fatal "HISTORIAN_DRIVE_PATH nie istnieje: $DRIVE_PATH"
  DRIVE_FILE="$DRIVE_PATH/$TEST_NAME"
  for i in $(seq 1 30); do
    [ -f "$DRIVE_FILE" ] && break
    sleep 2
  done
  [ -f "$DRIVE_FILE" ] || fatal "Plik nie dotarł do lokalnego mirroru Drive w 60 s: $DRIVE_FILE"
  DRIVE_SHA="$(sha256 "$DRIVE_FILE")"
  echo "Drive mirror:          $DRIVE_SHA"
  [ "$CANONICAL_SHA" = "$DRIVE_SHA" ] || fatal "SHA-256 GitHub/local != Drive mirror"
fi

log "5/8 Test odwrotny: mirror → Workspace"
if [ -n "$DRIVE_PATH" ]; then
  ROUNDTRIP="$SOURCE_DIR/${TEST_ID}.roundtrip.json"
  cp -f "$DRIVE_FILE" "$ROUNDTRIP"
  ROUNDTRIP_SHA="$(sha256 "$ROUNDTRIP")"
  echo "Round-trip:            $ROUNDTRIP_SHA"
  [ "$CANONICAL_SHA" = "$ROUNDTRIP_SHA" ] || fatal "SHA-256 round-trip nie zgadza się z CANONICAL"
  rm -f "$ROUNDTRIP"
else
  echo "Pomijam: brak lokalnego mirroru Drive."
fi

log "6/8 Walidacja korpusu"
cd "$REPO_DIR"
python3 scripts/sync_catalog.py

log "7/8 Budowanie i test grafu"
python3 scripts/build_graph.py
python3 - <<'PY'
import json
from pathlib import Path
g = json.loads(Path('index/graph.json').read_text(encoding='utf-8'))
ids = {n['id'] for n in g.get('nodes', [])}
assert 'HOS-TEST-001' in ids, 'HOS-TEST-001 nie ma w grafie'
assert g.get('edge_count', 0) >= 1, 'Graf nie ma relacji'
print('GRAPH OK: HOS-TEST-001 jest w grafie i graf ma relacje.')
PY

log "8/8 Test zapytania"
python3 scripts/historian_query.py search "HOS-TEST-001"

log "========================================"
if [ -n "$DRIVE_PATH" ]; then
  echo "E2E PASS: CANONICAL = WORKSPACE = DRIVE = ROUNDTRIP"
  echo "SHA-256: $CANONICAL_SHA"
else
  echo "E2E PARTIAL: CANONICAL = WORKSPACE oraz validator/graf OK"
  echo "Brakuje tylko lokalnego mirroru Drive do pełnego PASS."
fi
echo "========================================"
