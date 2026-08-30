#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO_URL="https://github.com/szarlej14/Historian-OS-SKYNET.git"
REPO_DIR="${HISTORIAN_REPO_DIR:-$HOME/Historian-OS-SKYNET}"
WORKSPACE="${HISTORIAN_WORKSPACE:-/storage/emulated/0/HistorianOS_Workspace}"

printf '\n[SKYNET] Przygotowanie Termuxa...\n'

# Nie uruchamiaj termux-setup-storage ponownie, jeżeli dostęp już istnieje.
if [ ! -d "$HOME/storage/shared" ]; then
  printf '\n[SKYNET] Brak aktywnego dostępu do pamięci Androida.\n'
  printf '[SKYNET] Uruchamiam konfigurację pamięci tylko raz.\n'
  termux-setup-storage || true
  printf '\n[SKYNET] Po przyznaniu uprawnienia uruchom ten sam starter ponownie.\n'
  exit 0
fi

pkg install -y git python coreutils >/dev/null

printf '\n[SKYNET] Synchronizacja repozytorium...\n'
if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" fetch origin main
  if [ -n "$(git -C "$REPO_DIR" status --porcelain)" ]; then
    printf '\n[SKYNET][STOP] W repozytorium są lokalne zmiany. Nie nadpisuję ich.\n'
    git -C "$REPO_DIR" status --short
    exit 2
  fi
  git -C "$REPO_DIR" checkout main >/dev/null 2>&1 || true
  git -C "$REPO_DIR" pull --ff-only origin main
else
  git clone "$REPO_URL" "$REPO_DIR"
fi

mkdir -p "$WORKSPACE"

printf '\n[SKYNET] Uruchamiam pełny test Historian OS...\n'
export HISTORIAN_REPO_DIR="$REPO_DIR"
export HISTORIAN_WORKSPACE="$WORKSPACE"
bash "$REPO_DIR/Skrypty_Termux/historianos_e2e_test.sh"

printf '\n[SKYNET] Gotowe.\n'
printf 'Repo:      %s\n' "$REPO_DIR"
printf 'Workspace: %s\n' "$WORKSPACE"
printf '\nW Obsidianie otwórz folder jako vault: %s\n' "$WORKSPACE"
