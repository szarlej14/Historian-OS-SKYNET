#!/usr/bin/env python3
"""Build the canonical Historian OS knowledge graph from data/*.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INDEX = ROOT / "index"
GRAPH = INDEX / "graph.json"

records = {}
for path in sorted(DATA.glob("*.json")):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    if isinstance(obj, dict) and isinstance(obj.get("id"), str) and obj["id"].startswith("HOS-"):
        records[obj["id"]] = obj

nodes = []
edges = []
edge_keys = set()

for record_id, obj in sorted(records.items()):
    nodes.append({
        "id": record_id,
        "label": obj.get("title", record_id),
        "category": obj.get("category", ""),
        "corpus": obj.get("corpus", ""),
        "status": obj.get("status", "")
    })
    for target in obj.get("relations", []):
        if not isinstance(target, str) or target not in records:
            continue
        key = (record_id, target)
        if key in edge_keys:
            continue
        edge_keys.add(key)
        edges.append({"from": record_id, "to": target, "type": "relation"})

reverse = [{"from": e["to"], "to": e["from"], "type": "reverse_relation"} for e in edges]
INDEX.mkdir(parents=True, exist_ok=True)
graph = {
    "type": "knowledge_graph",
    "version": "0.1.0",
    "generated_by": "scripts/build_graph.py",
    "node_count": len(nodes),
    "edge_count": len(edges),
    "nodes": nodes,
    "edges": edges,
    "traversal_edges": edges + reverse
}
GRAPH.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"OK: graph written to {GRAPH.relative_to(ROOT)}")
print(f"OK: {len(nodes)} nodes, {len(edges)} directed relation(s)")
