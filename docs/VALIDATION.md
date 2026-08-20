# Walidacja rekordów

Historian OS SKYNET rozdziela dwa poziomy danych:

1. **Rekord pełny** — element korpusu wiedzy. Poza polami bazowymi powinien posiadać `sources` i `created_at`.
2. **Rekord indeksowy / seed** — rekord opisujący zakres, indeks lub punkt startowy korpusu. Może używać pól takich jak `scope`, `records` albo `seed_records` bez pełnej warstwy proweniencji.

## Narzędzie

Walidator znajduje się w `scripts/validate_records.py` i korzysta wyłącznie ze standardowej biblioteki Pythona.

Uruchomienie lokalne:

```bash
python3 scripts/validate_records.py
```

Walidator sprawdza:

- poprawność JSON,
- wymagane pola bazowe,
- format identyfikatora HOS,
- dozwolone statusy,
- typy `tags` i `relations`,
- obecność `sources` i `created_at` w pełnych rekordach,
- poprawność znacznika czasu `created_at`,
- duplikaty ID,
- relacje wskazujące na nieistniejące rekordy.

## Zasada normalizacji

Walidator **nie dopisuje danych historycznych automatycznie**. Brakujące źródło, data utworzenia lub relacja wymagają świadomego uzupełnienia. Dzięki temu automatyzacja nie może przypadkowo stworzyć fałszywej proweniencji.

## CI

Workflow `.github/workflows/validate-records.yml` uruchamia walidację przy zmianach na `main` oraz przy pull requestach do `main`.
