# Architektura Historian OS SKYNET

## Warstwy

1. **DATA** — rekordy i materiały źródłowe.
2. **SCHEMAS** — definicje struktury rekordów.
3. **INDEX** — indeksy tematyczne, chronologiczne i relacyjne.
4. **CONFIG** — konfiguracja systemu.
5. **DOCS** — dokumentacja i roadmapa.

## Model rekordu

Każdy rekord powinien docelowo posiadać:

- `id` — unikalny identyfikator,
- `title` — nazwę,
- `category` — kategorię główną,
- `tags` — tagi,
- `date` — datę lub zakres dat, jeśli dotyczy,
- `summary` — krótki opis,
- `sources` — źródła,
- `relations` — powiązania z innymi rekordami,
- `status` — stan opracowania.

## Kierunek rozwoju

Architektura ma pozostać prosta na początku, ale umożliwiać późniejsze dodanie wyszukiwania, automatycznego indeksowania, walidacji danych oraz synchronizacji z zewnętrznymi źródłami.