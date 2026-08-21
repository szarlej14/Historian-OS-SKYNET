# Automatyczny graf wiedzy

Historian OS buduje graf automatycznie z rekordów `data/*.json`.

## Źródło prawdy

Rekordy pozostają kanonicznym źródłem danych. Skrypt `scripts/build_graph.py` nie zmienia rekordów; tworzy z nich `index/graph.json`.

## Węzły

Każdy rekord z identyfikatorem `HOS-*` staje się węzłem. Węzeł zawiera m.in. tytuł, kategorię, korpus i status.

## Krawędzie

Pole `relations` tworzy skierowane krawędzie `from -> to`. Na potrzeby przechodzenia grafu skrypt tworzy również krawędzie odwrotne w `traversal_edges`.

## Automatyzacja

GitHub Actions uruchamia `scripts/build_graph.py` po zmianach na `main`, podczas PR, ręcznie oraz według harmonogramu. Workflow waliduje również wynik grafu i API, a następnie zapisuje `index/catalog.json` i `index/graph.json`.

## API

- `GET /graph` — pełny wygenerowany graf.
- `GET /related/<HOS-ID>` — sąsiedzi rekordu.
- `GET /path?from=<HOS-ID>&to=<HOS-ID>` — najkrótsza ścieżka między rekordami.

Graf jest pochodną danych i może być bezpiecznie regenerowany w dowolnym momencie.
