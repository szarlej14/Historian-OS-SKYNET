#!/usr/bin/env python3
"""Reference-layer manifest for Historian OS Knowledge Fabric.

No external dataset is copied by this script. It records authoritative endpoints
and keeps source metadata separate from canonical Historian OS facts.
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

SOURCES = {
    "wikidata": {
        "kind": "dump",
        "formats": ["json", "rdf"],
        "url": "https://dumps.wikimedia.org/wikidatawiki/entities/",
        "note": "Weekly canonical JSON/RDF dumps; full RDF retains qualifiers and references."
    },
    "europeana": {
        "kind": "api",
        "url": "https://api.europeana.eu/",
        "note": "Search, Record and IIIF APIs; API key required."
    },
    "dbpedia": {
        "kind": "dataset",
        "url": "https://www.dbpedia.org/resources/",
        "note": "Quality-controlled knowledge-graph releases and datasets."
    },
    "library_of_congress": {
        "kind": "linked_data",
        "url": "https://id.loc.gov/",
        "note": "Authority and bibliographic metadata."
    },
}

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "70 Knowledge Base")
    root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "type": "knowledge_fabric_manifest",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "reference_data_is_not_canonical_truth",
        "sources": SOURCES,
    }
    (root / "sources.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"OK: wrote {root / 'sources.json'}")

if __name__ == "__main__":
    main()
