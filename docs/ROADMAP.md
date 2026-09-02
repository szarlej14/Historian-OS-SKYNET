# Roadmap — Historian OS SKYNET

## FAZA 0 — Fundament
- [x] Repozytorium, README, architektura, schemat rekordu
- [x] DATA + INDEX
- [x] Walidacja i synchronizacja katalogu

## FAZA 1 — Korpus + graf
- [x] Rekordy historyczne
- [x] Indeksy osób i kategorii
- [x] Powiązania krzyżowe
- [x] Silnik zapytań
- [x] Graf relacji

## FAZA 2 — Warstwy analityczne
- [x] RELATIONS
- [x] MIEJSCA
- [x] WYDARZENIA
- [x] SOURCES
- [x] TIMELINE
- [x] GAP DETECTOR
- [x] SERIE
- [x] COMMAND CENTER
- [x] Pipeline `validate_skynet.py`

## FAZA 3 — Evidence
- [ ] Oddzielenie istnienia źródła od potwierdzenia faktu
- [ ] Typ i jakość źródła
- [ ] Dowody sprzeczne / konflikt faktów
- [ ] Ślad audytowy zmian

## FAZA 4 — Entity + Time
- [ ] Wykrywanie możliwych duplikatów
- [ ] Bezpieczne rozpoznawanie encji
- [ ] Zakresy dat i daty niepewne
- [ ] Relacje temporalne: przed / po / w trakcie

## FAZA 5 — Intelligence
- [ ] Priorytetyzacja luk
- [ ] Wykrywanie osieroconych rekordów
- [ ] Ranking najważniejszych węzłów
- [ ] Konflikty i anomalie jako osobna warstwa

## FAZA 6 — Command Center
- [ ] Jeden raport stanu całego archiwum
- [ ] Health score
- [ ] Ostatnie zmiany
- [ ] Lista problemów wymagających decyzji

## FAZA 7 — Obsidian Bridge
- [ ] Eksport rekordów do Markdown
- [ ] Stabilne linki między encjami
- [ ] Widoki timeline / places / series
- [ ] GitHub jako źródło kanoniczne, Obsidian jako warstwa pracy i wizualizacji

## Zasada nadrzędna
SKYNET może wykrywać hipotezy, luki i konflikty, ale nie może zamieniać niepewności w fakt. Automatyczne scalanie rekordów wymaga wystarczających dowodów.
