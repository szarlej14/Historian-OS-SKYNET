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

## Share / Embed

The toolkit now exposes a self-contained share surface for every vault:

- `/vault/{id}` — share page with stats, dashboard, ZIP export and embed snippets.
- `/vault/{id}?embed=true` — compact full embed.
- `/vault/{id}?embed=timeline` — timeline-only embed.
- `/vault/{id}?embed=map` — map/coordinates-only embed.
- `/vault/{id}?embed=stats` — stats-only embed.
- `/api/vaults/{id}/share` — machine-readable share metadata.
- `/api/vaults/{id}/export` — filtered ZIP export.
- `POST /api/vaults/upload` — import a ZIP as a new vault.

The default showcase is **Zjazd Gnieźnieński 1000**, exposed as vault id `gniezno`.

## Quick start — Docker

From the repository root:

```bash
docker compose up --build
```

Then open:

```
http://localhost:8080/
http://localhost:8080/vault/gniezno
http://localhost:8080/dashboard?vault=gniezno
```

Uploaded vaults are persisted locally in `.local-vaults/`.

## GHCR release

The release workflow builds multi-architecture images for `linux/amd64` and `linux/arm64`, publishes SBOM/provenance and signs the image.

To publish release **v1.2-embed**:

```bash
git tag v1.2-embed
git push origin v1.2-embed
```

The image is published as:

```
ghcr.io/szarlej14/historian-os-skynet:v1.2-embed
```

Security credentials belong only in GitHub Actions secrets; never commit tokens to the repository.

See `historianos-toolkit/docker-compose.yml` for the nested toolkit compose file.
