# Historian OS SKYNET

**Evidence-first historical research engine:** corpus → provenance → selection → conflicts → human decisions → reproducible releases.

## Live status

[![Mega Test](https://github.com/szarlej14/Historian-OS-SKYNET/actions/workflows/historianos-mega-test.yml/badge.svg)](https://github.com/szarlej14/Historian-OS-SKYNET/actions/workflows/historianos-mega-test.yml)
[![Docker Release](https://github.com/szarlej14/Historian-OS-SKYNET/actions/workflows/docker-release.yml/badge.svg)](https://github.com/szarlej14/Historian-OS-SKYNET/actions/workflows/docker-release.yml)

**Deployment:** Fly.io / Railway / GHCR — configured by release workflow.

## Core architecture

- `data/` — canonical HOS records.
- `index/` — searchable indexes and relationships.
- `historianos-toolkit/app/` — Selection Engine + Command Center.
- `historianos-toolkit/tests/` — integration and end-to-end tests.
- `schemas/` — data contracts.
- `.github/workflows/` — automated validation and release automation.
- `docs/` — architecture and operational documentation.

## Research loop

```
IMPORT
  ↓
QUALITY SCORE
  ↓
ENTITY RESOLUTION
  ↓
PROVENANCE
  ↓
CONFLICT / GAP
  ↓
HUMAN DECISION
  ↓
CANONICAL KNOWLEDGE
  ↓
GRAPH / TIMELINE / ANALYSIS
```

## Security & reproducibility

Release images should publish an SBOM and SLSA provenance. Deployment credentials belong only in GitHub Actions secrets; never commit tokens to the repository.

## Quick start

```bash
python3 scripts/historian_query.py search Zumbach
python3 scripts/historian_query.py show HOS-PERSON-JAN-ZUMBACH
python3 scripts/historian_query.py related HOS-ORG-303-SQUADRON
python3 scripts/historian_query.py stats
```

See the workflow files and `historianos-toolkit/DEPLOYMENT.md` for deployment instructions.
