#!/usr/bin/env bash
set -euo pipefail

VAULT_ROOT="${1:-.}"
cd "$VAULT_ROOT"

mkdir -p "00 Relacje" "10 Miejsca" "20 Wydarzenia" "30 Zrodla" "40 Fakty" "50 Serie" "60 Command Center" "Templates"

copy_if_exists() {
  src="$1"; dst="$2"
  if [[ -f "$src" ]]; then
    cp "$src" "$dst"
    echo "OK  $dst"
  else
    echo "WARN brak: $src"
  fi
}

copy_if_exists "Templates/Relacja.md" "00 Relacje/_README.md"
copy_if_exists "Templates/Wydarzenie.md" "20 Wydarzenia/_README.md"
copy_if_exists "Templates/Seria.md" "50 Serie/_README.md"
copy_if_exists "Dashboard.md" "60 Command Center/Dashboard.md"

mkdir -p ".obsidian/snippets"
if [[ -f ".obsidian/snippets/skynet.css" ]]; then
  echo "OK  .obsidian/snippets/skynet.css"
else
  echo "INFO CSS snippet jest w repo: .obsidian/snippets/skynet.css"
fi

echo
echo "Historian OS SKYNET vault structure ready."
echo "Enable SKYNET CSS in Obsidian: Settings > Appearance > CSS snippets."
