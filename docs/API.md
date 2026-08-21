# Historian OS SKYNET API

Lekki interfejs HTTP bez zewnętrznych zależności.

Uruchomienie lokalne:

```bash
python3 scripts/historian_api.py
```

Domyślnie API nasłuchuje na `127.0.0.1:8787`.

## Endpointy

- `GET /health` — stan usługi
- `GET /stats` — statystyki korpusu
- `GET /search?q=zumbach` — wyszukiwanie pełnotekstowe
- `GET /record/HOS-PERSON-JAN-ZUMBACH` — rekord po ID
- `GET /related/HOS-PERSON-JAN-ZUMBACH` — graf bezpośrednich relacji

API korzysta bezpośrednio z kanonicznych rekordów `data/*.json`. Nie tworzy drugiej bazy danych.
