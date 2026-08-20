# Historian OS SKYNET

Centralny szkielet modularnego archiwum wiedzy, źródeł i relacji między rekordami.

## Status

**FAZA 1 — stabilizacja rdzenia**

Repozytorium posiada teraz kanoniczny schemat rekordów, konwencję identyfikatorów, magazyn rekordów oraz osobne indeksy korpusów i relacji.

## Fundament

- rekordy przechowywane pojedynczo jako JSON w `data/records/`,
- identyfikatory `HOS-<KORPUS>-<NUMER>`,
- walidacja przez `schemas/record.schema.json`,
- statusy `draft`, `review`, `verified`, `archived`,
- jawne źródła i relacje między rekordami,
- indeksy oddzielone od danych źródłowych,
- konfiguracja centralna w `config/historian.json`.

## Korpusy

- HISTORIA
- SPORT
- LOTNICTWO
- TECHNOLOGIA
- OSOBY
- ŹRÓDŁA

Rejestr korpusów znajduje się w `index/CORPUS-INDEX.md`.

## Zasada główna

Nie duplikujemy wiedzy. Tworzymy jeden rekord kanoniczny i łączymy go z innymi rekordami za pomocą relacji. Każdy rekord powinien być możliwy do prześledzenia do źródeł.

## Następny etap

Automatyczna walidacja rekordów, generator indeksów oraz pierwsze rzeczywiste rekordy korpusów.
