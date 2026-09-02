# SKYNET Graph Engine REAL

## Cel

Silnik czyta rzeczywisty korpus Historian OS z repozytorium, zamiast zakładać, że rekordy znajdują się wyłącznie w `/mnt/data/HOS-*.json`.

## Obsługiwane lokalizacje

- `data/*.json`
- `data/**/*.json`
- `data/records/*.json`
- `memory/data/**/*.json`
- `index/*.json`
- `data/corpus/*/*.json`
- fallback `HOS-*.json` i `/mnt/data/HOS-*.json`

## Ważna zgodność ze schematem REAL

Korpus obecny w `main` używa pól:

- `title` zamiast `name`,
- `category` zamiast `type`,
- `relations` jako lista identyfikatorów, np. `"HOS-ORG-303-SQUADRON"`.

Fundament z PR #1 używa natomiast relacji obiektowych, np.:

```json
{"type":"related_to","target":"HOS-LOTNICTWO-000001"}
```

Silnik obsługuje oba warianty, aby nie uzależniać grafu od kolejności scalania zmian.

## Uruchomienie

```bash
python scripts/skynet_graph_engine.py stats --mode directed
python scripts/skynet_graph_engine.py graph HOS-PERSON-JAN-ZUMBACH 2 --mode directed
python scripts/skynet_graph_engine.py graph HOS-PERSON-JAN-ZUMBACH 2 --mode undirected
```

## Wynik

Silnik wypisuje liczbę węzłów i krawędzi, listę odwiedzonych rekordów oraz deduplikowane relacje. Dodatkowo zapisuje wynik do:

```text
graph-<ID>-<depth>-<mode>.json
```

## Uwaga diagnostyczna

Przed tą wersją silnik zakładał relacje wyłącznie jako obiekty z kluczem `to`. W aktualnych rekordach REAL relacje są stringami. Bez normalizacji dawało to poprawne wczytanie rekordów, ale zerową liczbę relacji w grafie. To jest osobny problem od lokalizacji `/mnt/data` i oba problemy muszą być rozwiązane jednocześnie.
