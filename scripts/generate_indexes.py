#!/usr/bin/env python3
"""Generate navigation indexes from canonical Historian OS SKYNET records."""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "data" / "records"
INDEX = ROOT / "index"


def load_records():
    records = []
    for path in sorted(RECORDS.glob("*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def records_index(records):
    lines = [
        "# RECORDS INDEX — Historian OS SKYNET",
        "",
        "| ID | Tytuł | Korpus | Status |",
        "|---|---|---|---|",
    ]
    for record in records:
        lines.append(
            f"| {record['id']} | {record['title']} | {record['corpus']} | {record['status']} |"
        )
    lines += [
        "",
        "Indeks jest generowany z rekordów kanonicznych. Rekord źródłowy pozostaje w `data/records/`.",
        "",
    ]
    return "\n".join(lines)


def relations_index(records):
    titles = {r["id"]: r["title"] for r in records}
    grouped = defaultdict(list)
    for record in records:
        for relation in record["relations"]:
            grouped[record["corpus"]].append(
                (record["id"], relation["type"], relation["target"], relation.get("label") or titles.get(relation["target"], ""))
            )

    lines = [
        "# RELATIONS INDEX — Historian OS SKYNET",
        "",
        "Indeks relacji jest generowany z pól `relations` rekordów kanonicznych.",
        "",
        "## Relacje",
        "",
    ]
    for corpus in sorted(grouped):
        lines += [f"### {corpus}", ""]
        for source, rel_type, target, label in sorted(grouped[corpus]):
            suffix = f" {label}" if label else ""
            lines.append(f"- `{source}` → `{rel_type}` → `{target}`{suffix}")
        lines.append("")

    if not grouped:
        lines.append("Brak zdefiniowanych relacji.")
        lines.append("")

    return "\n".join(lines)


def main():
    records = load_records()
    (INDEX / "RECORDS-INDEX.md").write_text(records_index(records), encoding="utf-8")
    (INDEX / "RELATIONS-INDEX.md").write_text(relations_index(records), encoding="utf-8")
    print(f"Generated indexes for {len(records)} record(s).")


if __name__ == "__main__":
    main()
