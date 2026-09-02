# SKYNET Analytics Layers

The analytic stack is now explicit and reproducible:

1. **RELATIONS** — directed relation edges, incoming/outgoing counts and node degree.
2. **MIEJSCA** — conservative place index from explicit place/location/venue/city/country fields and place-like tags.
3. **WYDARZENIA** — event candidates using explicit event fields plus conservative category/title signals.
4. **SOURCES** — source inventory with source-to-record mapping and URL-domain counts.
5. **TIMELINE** — chronological record index; year is read from `date`, then from the title.
6. **GAP DETECTOR** — chronological gaps of at least three years plus records missing summary, sources or relations.
7. **SERIE** — grouped series by corpus + category with count and year range.
8. **COMMAND CENTER** — builds the complete stack and writes a compact health snapshot.

## Usage

From the repository root:

```bash
python3 scripts/skynet.py relations
python3 scripts/skynet.py places
python3 scripts/skynet.py events
python3 scripts/skynet.py sources
python3 scripts/skynet.py timeline
python3 scripts/skynet.py gaps
python3 scripts/skynet.py series
python3 scripts/skynet.py command-center
```

Or build everything in one pass:

```bash
python3 scripts/skynet.py all
```

Derived artifacts are written under `index/`:

- `relations.json`
- `places.json`
- `events.json`
- `sources.json`
- `timeline.json`
- `gaps.json`
- `series.json`
- `command_center.json`

The layers do not modify source records. They are derived views, so rebuilding them is safe and deterministic.

## Design rule

The detectors are deliberately conservative. A missing inferred place/event is not treated as a fact. The system records what can be established from current structured fields and leaves uncertain enrichment for a later evidence-aware ingestion layer.
