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

## Łańcuch LOTNICTWO

`Dęblin → pilot → jednostka → bitwy → losy`

### Dęblin / Szkoła Orląt

- `HOS-LOTNICTWO-000002` → `part_of` → korpus LOTNICTWO
- `HOS-LOTNICTWO-000002` → `related_to` → `HOS-LOTNICTWO-000001` Jan Zumbach
- `HOS-LOTNICTWO-000002` → `related_to` → `HOS-LOTNICTWO-000004` Stanisław Skalski
- `HOS-LOTNICTWO-000002` → `related_to` → `HOS-LOTNICTWO-000005` Wacław Urbanowicz
- `HOS-LOTNICTWO-000002` → `related_to` → `HOS-LOTNICTWO-000006` Zdzisław Horbaczewski

### Dywizjon 303

- `HOS-LOTNICTWO-000003` → `related_to` → `HOS-LOTNICTWO-000001` Jan Zumbach
- `HOS-LOTNICTWO-000003` → `related_to` → `HOS-LOTNICTWO-000005` Wacław Urbanowicz
- `HOS-LOTNICTWO-000003` → `related_to` → `HOS-LOTNICTWO-000006` Zdzisław Horbaczewski

## Format

Każda relacja ma postać:

`<źródłowy rekord> -> <typ relacji> -> <docelowy rekord>`

Docelowe ID muszą istnieć w korpusie albo być oznaczone jako oczekujące na utworzenie.
