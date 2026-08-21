# Historian OS — E2E Test

## Cel

Udowodnić, że rekord kanoniczny może przejść przez lokalny Workspace / transport synchronizacyjny i wrócić bez zmiany bajtów, a następnie przejść walidację i wejść do automatycznego grafu.

## Zasada kanoniczności

`GitHub / Historian OS` jest jedynym źródłem prawdy dla rekordów `HOS-*`.

`Workspace`, `Syncthing`, `Drive Sync` i inne kopie są warstwą transportu/cache. Nie tworzą ani nie rozstrzygają HOS-ID.

## Rekord testowy

`data/HOS-TEST-001.json`

Rekord ma relację do `HOS-PERSON-JAN-ZUMBACH`, dzięki czemu test sprawdza nie tylko obecność w grafie, ale również poprawność istniejącej relacji.

## Uruchomienie w Termuxie

```bash
bash ~/Historian-OS-SKYNET/Skrypty_Termux/historianos_e2e_test.sh
```

Skrypt sam sprawdza lub instaluje `git`, `python` i `coreutils`.

## Pełny PASS

Pełny test E2E wymaga ustawienia `HISTORIAN_DRIVE_PATH` na lokalny folder, który jest rzeczywistym mirrorem Drive/warstwy synchronizacji:

```bash
export HISTORIAN_DRIVE_PATH="/storage/emulated/0/NAZWA_FOLDERU"
bash ~/Historian-OS-SKYNET/Skrypty_Termux/historianos_e2e_test.sh
```

Warunki PASS:

1. rekord z GitHub/local canonical istnieje,
2. SHA-256 canonical = SHA-256 Workspace,
3. SHA-256 canonical = SHA-256 mirroru Drive,
4. SHA-256 mirroru = SHA-256 po powrocie do Workspace,
5. `sync_catalog.py` kończy się bez błędu,
6. `build_graph.py` generuje graf,
7. `HOS-TEST-001` znajduje się w grafie,
8. graf posiada co najmniej jedną relację,
9. silnik zapytań znajduje `HOS-TEST-001`.

Brak lokalnego mirroru Drive daje wynik `E2E PARTIAL`, a nie fałszywy `PASS`.

## Ważne

Standardowa aplikacja Google Drive na Androidzie nie jest traktowana jako lokalny, obserwowany przez Termux folder. Jeśli Drive Sync używa osobnej aplikacji lub mechanizmu, skrypt musi dostać ścieżkę do jej lokalnego mirroru. Nie uznajemy samej obecności pliku w aplikacji Drive za dowód zgodności SHA-256.
