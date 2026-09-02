# RFC-0002 — Research Workflow Pipeline

**Status:** Draft / implementation-aligned  
**Scope:** Historian OS SKYNET research workflow

## Abstract

RFC-0002 defines the complete research loop of Historian OS SKYNET:

**RELATIONS → MIEJSCA → WYDARZENIA → SOURCES → TIMELINE → GAP DETECTOR → SERIE → COMMAND CENTER**

The pipeline turns isolated research objects into an auditable evidence graph while preserving uncertainty and human responsibility.

## 1. Ontology — RELATIONS

Relations establish who or what is connected before chronology is asserted.

Canonical Obsidian representation:

```yaml
type: relacja
from: "[[Osoba A]]"
to: "[[Osoba B]]"
typ_relacji: sojusz
certainty: B2
czas_trwania: 1000-1002
zrodlo: "[[Źródło]]"
```

The relation layer corresponds conceptually to CIDOC CRM relationship/event participation patterns. It does not assert a historical interpretation merely because two entities are linked.

## 2. Spatial layer — MIEJSCA

Places represent E53 Place concepts and provide the spatial anchor for events and facts.

Required direction:
- stable place identity,
- human-readable name,
- coordinates when known,
- optional map representation,
- links to events, people and sources.

## 3. Event core — WYDARZENIA

Events are the central temporal/spatial container.

```yaml
type: wydarzenie
nazwa: ""
data: ""
taq: ""
tpq: ""
miejsce: "[[Miejsce]]"
uczestnicy:
  - "[[Osoba]]"
poprzedza: "[[Wydarzenie]]"
nastepuje_po: "[[Wydarzenie]]"
skutek: ""
zrodla:
  - "[[Źródło]]"
ocena: B2
tags:
  - wydarzenie
```

An event may have an exact date, an interval, or uncertainty bounds.

## 4. Provenance — SOURCES

Every historical claim in `40 Fakty/` must have provenance.

Important distinction:

**source exists ≠ source confirms the claim.**

The Evidence layer will therefore distinguish:
- source presence,
- evidentiary relevance,
- source quality,
- agreement/conflict,
- human assessment.

## 5. Temporal uncertainty — TIMELINE

Dates are modeled as structured uncertainty rather than forced precision.

Example:

```yaml
data_narracyjna: 1000
tpq: 0999-12-31
taq: 1000-03-15
precyzja: rok
```

The timeline layer may sort by normalized temporal values while retaining the original uncertainty.

## 6. Audit — GAP DETECTOR

GAP DETECTOR is the automated auditor.

Initial checks:
- facts without sources,
- events with incomplete temporal bounds,
- dangling relations,
- missing summaries,
- weakly connected records,
- chronological gaps,
- source deficiencies.

The detector reports problems; it does not silently repair historical assertions.

## 7. Longue durée — SERIE

SERIE groups events into recurring patterns such as coronations, congresses, invasions or campaigns.

The series layer enables longitudinal analysis and future domain modules such as Military History and Economic History.

## 8. Decision layer — COMMAND CENTER

COMMAND CENTER is a decision log, not merely a dashboard.

Any change in historical assessment should retain:

```yaml
decyzja: zaakceptowano
autor_decyzji: ""
uzasadnienie: ""
data_decyzji: ""
```

Automated analysis may recommend. A human researcher owns the final decision.

## 9. Constitution alignment

This RFC operationalizes the principles described in the project's research constitution, especially:
- provenance-first research,
- valid uncertainty,
- explicit decisions,
- human responsibility.

No constitutional file named `CONSTITUTION.md` was found at repository root during implementation; therefore this RFC does not invent chapter text or claim exact clause numbering. Once the canonical Constitution is present, the references to Chapters III and IV should be bound to its exact headings/clauses.

## 10. Implementation order

1. Evidence model
2. Entity resolution
3. Temporal engine
4. Gap prioritization
5. Command Center decision log
6. Obsidian export/bridge

## 11. Non-goals

The pipeline must not:
- convert uncertainty into certainty,
- merge entities solely on name similarity,
- treat a citation as proof without evidence assessment,
- overwrite canonical source records during indexing.

## Acceptance criterion

A research item is considered pipeline-complete when its relevant relation, place, event, provenance, temporal state, series membership and decision/audit state can be traversed without losing uncertainty or provenance.
