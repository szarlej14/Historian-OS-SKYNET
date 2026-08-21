# Historian OS SKYNET — Query Engine

The repository now contains a small local query engine in `scripts/historian_query.py`.

## Commands

```bash
python3 scripts/historian_query.py search Zumbach
python3 scripts/historian_query.py show HOS-PERSON-JAN-ZUMBACH
python3 scripts/historian_query.py related HOS-ORG-303-SQUADRON
python3 scripts/historian_query.py stats
```

The engine reads canonical `data/*.json` records and exposes four primitives: full-text search, exact record lookup, direct relation lookup, and corpus statistics.

This is intentionally dependency-free so it can run on GitHub Actions, a local Linux/Termux environment, or another Python 3 environment.
