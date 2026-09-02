# Contributing to Historian OS SKYNET

## Zasada nadrzędna

Każda zmiana musi zachować **provenance, uncertainty i human responsibility**.

## Zgodność z RFC

Zmiany architektury, modelu danych lub workflow badawczego, które wpływają na więcej niż jeden komponent, powinny mieć RFC.

Nowe RFC:
1. używa `rfcs/0001-template.md`,
2. ma unikalny numer,
3. wskazuje powiązane zasady Constitution,
4. definiuje model danych i workflow,
5. określa walidację oraz kryteria akceptacji.

## Dane kanoniczne

- Nie modyfikuj źródłowych rekordów wyłącznie po to, aby poprawić indeks pochodny.
- Indeksy i raporty muszą być możliwe do ponownego wygenerowania.
- Źródło nie jest automatycznie dowodem potwierdzającym fakt.
- Niepewność jest prawidłowym stanem danych.

## GAP DETECTOR

GAP DETECTOR raportuje problemy. Nie kasuje rekordów i nie rozstrzyga samodzielnie sporów historycznych.

## Entity Resolution

Podobieństwo nazw jest sygnałem, nie dowodem tożsamości. Automatyczne scalanie encji jest zabronione bez jawnej reguły i wystarczających dowodów.

## Decyzje człowieka

Zmiany interpretacyjne wymagające osądu badacza powinny pozostawiać Decision Log z decyzją, autorem, uzasadnieniem i datą.

## Pull requests

Każdy PR powinien krótko opisywać:
- co się zmieniło,
- dlaczego,
- jaki RFC/Constitution ma zastosowanie,
- jak wykonano walidację,
- czy zmieniono dane kanoniczne.

## Minimalny test

Przed zaakceptowaniem zmiany uruchom:

```bash
python3 scripts/validate_skynet.py
```

Jeżeli zmiana dotyczy wyłącznie warstwy analitycznej, upewnij się również, że indeksy pochodne można odtworzyć bez utraty danych źródłowych.
