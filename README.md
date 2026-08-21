# Historian OS SKYNET

Centralny szkielet projektu **Historian OS SKYNET** — modularnego archiwum wiedzy, indeksowania źródeł i powiązań między rekordami.

## Status

**FAZA 1 — korpus + indeks + graf + silnik zapytań + synchronizacja**

Repozytorium posiada kanoniczne rekordy JSON, indeksy, relacje między rekordami, automatyczną walidację oraz lokalny silnik zapytań.

## Architektura

- `data/` — kanoniczne rekordy HOS.
- `index/` — indeksy osób, wydarzeń, relacji i katalog.
- `scripts/historian_query.py` — lokalny silnik wyszukiwania, odczytu i nawigacji po relacjach.
- `scripts/sync_catalog.py` — walidacja i synchronizacja katalogu.
- `.github/workflows/historian-sync.yml` — automatyczna walidacja i synchronizacja.
- `docs/QUERY_ENGINE.md` — instrukcja silnika zapytań.
- `schemas/` — schematy danych.

## Szybki start

```bash
python3 scripts/historian_query.py search Zumbach
python3 scripts/historian_query.py show HOS-PERSON-JAN-ZUMBACH
python3 scripts/historian_query.py related HOS-ORG-303-SQUADRON
python3 scripts/historian_query.py stats
```

## Założenia

- modularna struktura wiedzy,
- jednoznaczne identyfikatory rekordów,
- indeksowanie tematyczne i chronologiczne,
- powiązania krzyżowe między rekordami,
- oddzielenie danych źródłowych od warstwy indeksu,
- automatyczna walidacja i synchronizacja,
- możliwość uruchomienia lokalnie bez dodatkowych zależności.

## Zasada główna

Najpierw stabilny fundament i schemat danych, potem rozbudowa korpusu wiedzy. Każdy kolejny moduł ma być możliwy do jednoznacznego indeksowania, wyszukania i powiązania z innymi rekordami.
