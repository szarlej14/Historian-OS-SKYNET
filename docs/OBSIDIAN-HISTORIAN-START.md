# Historian OS — Obsidian start

## Cel

Ten dokument jest punktem wejścia dla mobilnego vaulta Obsidian powiązanego z repozytorium `szarlej14/Historian-OS-SKYNET`.

## Repozytorium

- Remote: `szarlej14/Historian-OS-SKYNET`
- Branch: `main`
- Obsidian/GitSync: synchronizacja dwukierunkowa dopiero po wykonaniu pierwszego bezpiecznego testu.

## Struktura

- `data/` — rekordy i materiały źródłowe
- `schemas/` — schematy rekordów
- `index/` — indeksy
- `config/` — konfiguracja
- `docs/` — dokumentacja

## Zasada bezpieczeństwa

Pierwsza synchronizacja nie powinna automatycznie nadpisywać lokalnego vaulta. Najpierw należy wykonać kopię lokalnego vaulta, następnie sprawdzić stan repozytorium i dopiero wykonać synchronizację dwukierunkową.

## Model rekordu

Minimalny rekord Historian OS powinien zawierać:

- `id`
- `title`
- `category`
- `tags`
- `date`
- `summary`
- `sources`
- `relations`
- `status`

## Następny etap

1. Ustabilizować synchronizację.
2. Przygotować szablony rekordów Obsidian.
3. Dodać indeksy tematyczne i relacyjne.
4. Dodać walidację rekordów.
5. Rozbudowywać korpus wiedzy bez zmiany fundamentu repozytorium.
