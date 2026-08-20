# Rekordy

`data/records/` jest kanonicznym magazynem rekordów Historian OS SKYNET.

## Zasady

- Jeden rekord = jeden plik JSON.
- Nazwa pliku powinna odpowiadać identyfikatorowi rekordu, np. `HOS-LOTNICTWO-000001.json`.
- Rekord musi przechodzić walidację względem `schemas/record.schema.json`.
- Powiązania zapisujemy jako relacje do identyfikatorów `HOS-*`; nie kopiujemy całych rekordów.
- Źródła zapisujemy jawnie, aby każdy fakt można było prześledzić.
- `verified` oznacza rekord sprawdzony źródłowo; `review` oznacza rekord wymagający kontroli.
