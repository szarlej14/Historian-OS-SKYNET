# SKYNET — warstwa grafu wiedzy

SKYNET jest warstwą nad korpusem Historian OS. Nie kopiuje danych: czyta rekordy `data/*.json` i wykorzystuje ich `relations` do budowania grafu.

## Zapytania

```bash
python3 scripts/skynet.py ask "Jan Zumbach"
python3 scripts/skynet.py graph HOS-PERSON-JAN-ZUMBACH 2
python3 scripts/skynet.py path HOS-PERSON-JAN-ZUMBACH HOS-ORG-DEBLIN-AVIATION-SCHOOL
```

## Model

`DATA` → `QUERY ENGINE` → `RELATION GRAPH` → `SKYNET`

### `ask`
Wyszukuje rekordy na podstawie tekstu i od razu rozwija ich najbliższe powiązania.

### `graph`
Rozwija graf wokół wskazanego rekordu do podanej głębokości.

### `path`
Znajduje najkrótszą ścieżkę relacji między dwoma rekordami.

Warstwa działa bez zewnętrznej bazy i bez wymaganych bibliotek zewnętrznych.
