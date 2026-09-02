# Knowledge Fabric

## Sources

The reference layer is designed around machine-readable public data sources:

- Wikidata: weekly JSON and RDF dumps; RDF preserves statements, qualifiers and references in the full dump.
- Europeana: Search, Record and IIIF APIs for cultural-heritage metadata.
- DBpedia: quality-controlled knowledge-graph releases and datasets.
- Library of Congress Linked Data Service: authority and bibliographic metadata.

## Rule

External datasets are **reference data**, never canonical historical truth.

Every imported claim keeps:
- provider
- external identifier / URI
- retrieval timestamp
- original source URI
- raw statement when practical
- normalization status
- entity-resolution status
- provenance

Canonical Historian OS records remain governed by Constitution + provenance + human Decision Log.

## Layout

```
70 Knowledge Base/
├── wikidata/
├── europeana/
├── dbpedia/
├── loc/
├── imports/
├── normalized/
├── entity-resolution/
└── provenance/
```
