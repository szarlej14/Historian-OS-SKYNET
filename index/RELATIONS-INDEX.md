# RELATIONS INDEX — Historian OS SKYNET

Indeks relacji opisuje połączenia między rekordami bez duplikowania ich treści.

## Typy relacji

- `related_to` — ogólne powiązanie
- `person_involved` — osoba związana z wydarzeniem
- `event_related` — wydarzenie związane z rekordem
- `place_related` — miejsce związane z rekordem
- `source_for` — źródło dokumentujące rekord
- `part_of` — rekord podrzędny względem większej całości
- `cross_reference` — świadome powiązanie między korpusami

## Format

Każda relacja ma postać:

`<źródłowy rekord> -> <typ relacji> -> <docelowy rekord>`

Docelowe ID muszą istnieć w korpusie albo być oznaczone jako oczekujące na utworzenie.
