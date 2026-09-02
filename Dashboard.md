# HISTORIAN OS · SKYNET
## Research Command Center

> [!abstract] SYSTEM PRINCIPLE
> **AI proposes. Evidence constrains. Human decides.**

## STATUS

```dataviewjs
const p=dv.pages();
dv.table(["WARSTWA","REKORDY"],[["FAKTY",p.where(x=>x.type==="fakt").length],["WYDARZENIA",p.where(x=>x.type==="wydarzenie").length],["MIEJSCA",p.where(x=>x.type==="miejsce").length],["ŹRÓDŁA",p.where(x=>x.type==="zrodlo"||x.type==="źródło").length],["RELACJE",p.where(x=>x.type==="relacja").length],["SERIE",p.where(x=>x.type==="seria").length]]);
```

## GAP DETECTOR

> [!gap] AUDYT GRAFU
> GAP DETECTOR raportuje problemy. Nie usuwa rekordów i nie rozstrzyga samodzielnie sporów.

```dataviewjs
const facts=dv.pages().where(p=>(p.type==="fakt"||p.type==="fact")&&!p.zrodlo&&!p.zrodla&&!p.source&&!p.sources);
dv.table(["ORPHAN FACT","OCENA","PLIK"],facts.map(p=>[p.tresc??p.nazwa??p.file.name,p.ocena_koncowa??p.ocena??"—",p.file.link]));
```

### ALERTY

| Kod | Znaczenie |
|---|---|
| ORPHAN_FACT | Fakt bez provenance |
| ORPHAN_SOURCE | Źródło bez powiązania |
| MISSING_TPQ_TAQ | Niepełny zakres czasowy |
| CONFLICT_DATE | Konflikt chronologiczny |
| LOW_CONFIDENCE_CLUSTER | Skupisko słabych ocen |
| ORPHAN_RELATION | Relacja bez wymaganych danych |

## TIMELINE · UNCERTAINTY

```dataview
TABLE data_narracyjna, tpq, taq, precyzja, miejsce
FROM "20 Wydarzenia"
WHERE type = "wydarzenie"
SORT tpq ASC
```

> [!uncertainty] ZASADA CZASU
> 1000 nie oznacza automatycznie konkretnego dnia. SKYNET zachowuje TPQ, TAQ i precyzję.

## EVIDENCE

```dataview
TABLE zrodlo, status, quality, locator
FROM "40 Fakty"
WHERE zrodlo
SORT quality ASC
LIMIT 30
```

> [!evidence] PROVENANCE FIRST
> Obecność źródła nie oznacza jeszcze, że źródło potwierdza twierdzenie.

## ENTITY RESOLUTION

```dataview
TABLE entity_type, canonical_id, candidate_id, score, status
FROM "60 Command Center"
WHERE status = "needs_review"
SORT score DESC
LIMIT 25
```

> [!warning] NIE SCALAJ AUTOMATYCZNIE
> Podobieństwo nazw jest sygnałem do badania, nie dowodem tożsamości.

## SERIE · LONGUE DURÉE

```dataview
TABLE typ, data, miejsce
FROM "50 Serie"
SORT data ASC
```

> [!info] SERIE
> Seria jest warstwą interpretacyjną i nie może nadpisywać faktów jednostkowych.

## DECISION LOG

| Data | Decyzja | Autor | Uzasadnienie |
|---|---|---|---|
| — | — | — | — |

> [!decision] HUMAN RESPONSIBILITY
> Zmiana oceny historycznej wymaga jawnej decyzji, autora, uzasadnienia i daty.

## OPERATIONS

- [[00 Relacje]]
- [[10 Miejsca]]
- [[20 Wydarzenia]]
- [[30 Zrodla]]
- [[40 Fakty]]
- [[50 Serie]]
- [[60 Command Center]]

### PIPELINE

**RELATIONS → MIEJSCA → WYDARZENIA → SOURCES → EVIDENCE → ENTITY RESOLUTION → TIMELINE → GAP DETECTOR → GAP PRIORITIZER → SERIE → COMMAND CENTER**

> [!success] ARCHITECTURE
> Kanoniczne dane → indeksy pochodne → audyt → priorytety → decyzja człowieka.
