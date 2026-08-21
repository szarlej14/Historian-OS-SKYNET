#!/usr/bin/env python3
"""SKYNET Graph Engine REAL.

Canonicalizes the Historian OS corpus before graph traversal.
Source states are explicit: REAL, EMPTY, FALLBACK.
The engine never manufactures fallback records.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import defaultdict, deque
from pathlib import Path

SOURCE_REAL = "REAL"
SOURCE_EMPTY = "EMPTY"
SOURCE_FALLBACK = "FALLBACK"
SCHEMA_VERSION = "1.0"


def find_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    candidates = [cwd, *cwd.parents,
        Path("/storage/emulated/0/Documents/Historian-OS-SKYNET"),
        Path("/storage/emulated/0/Documents/Pete"), Path("/mnt/data")]
    seen = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "data").is_dir() and (candidate / "scripts").is_dir():
            return candidate
    return cwd


REPO_ROOT = find_repo_root()
SEARCH_PATTERNS = (
    "data/*.json", "data/**/*.json", "memory/data/*.json", "memory/data/**/*.json",
    "index/*.json", "data/corpus/*/*.json", "data/records/*.json",
    "Pete/memory/data/corpus/*/*.json", "HOS-*.json", "/mnt/data/HOS-*.json",
)


def find_json_files() -> list[str]:
    files: set[str] = set()
    for pattern in SEARCH_PATTERNS:
        files.update(glob.glob(str(REPO_ROOT / pattern), recursive=True))
        if not pattern.startswith("/"):
            files.update(glob.glob(pattern, recursive=True))
    return sorted(files)


def normalize_relation(source_id: str, relation) -> dict | None:
    """Return the canonical relation: source, target, relation."""
    if isinstance(relation, str):
        target = relation.strip()
        return {"source": source_id, "target": target, "relation": "related_to"} if target else None
    if isinstance(relation, dict):
        target = relation.get("target") or relation.get("to") or relation.get("id")
        if not target:
            return None
        relation_type = (relation.get("type") or relation.get("relation")
                         or relation.get("label") or "related_to")
        return {"source": source_id, "target": str(target), "relation": str(relation_type)}
    return None


def normalize_record(raw: dict, source_file: str) -> tuple[dict, list[dict]]:
    """Normalize current and legacy records into one internal contract."""
    record_id = str(raw.get("id", "")).strip()
    record = {
        "id": record_id,
        "title": str(raw.get("title") or raw.get("name") or ""),
        "category": str(raw.get("category") or raw.get("type") or ""),
        "corpus": raw.get("corpus"),
        "status": raw.get("status"),
        "date": raw.get("date"),
        "summary": raw.get("summary"),
        "sources": list(raw.get("sources", [])) if isinstance(raw.get("sources", []), list) else [],
        "relations": [],
        "metadata": raw.get("metadata", {}) if isinstance(raw.get("metadata", {}), dict) else {},
        "_source_file": source_file,
        "_schema_version": SCHEMA_VERSION,
    }
    normalized_relations = []
    raw_relations = raw.get("relations", [])
    if isinstance(raw_relations, list):
        for raw_relation in raw_relations:
            relation = normalize_relation(record_id, raw_relation)
            if relation:
                normalized_relations.append(relation)
    record["relations"] = normalized_relations
    return record, normalized_relations


def load_corpus() -> tuple[dict[str, dict], list[dict], list[str], dict]:
    records: dict[str, dict] = {}
    relations: list[dict] = []
    files = find_json_files()
    invalid_files = []

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:
            invalid_files.append({"file": filepath, "error": str(exc)})
            continue
        items = payload if isinstance(payload, list) else [payload]
        for raw in items:
            if not isinstance(raw, dict) or not raw.get("id"):
                continue
            record, record_relations = normalize_record(raw, filepath)
            record_id = record["id"]
            if record_id not in records:
                records[record_id] = record
                relations.extend(record_relations)

    if records:
        source_state = SOURCE_REAL
        reason = "canonical corpus loaded"
    else:
        source_state = SOURCE_EMPTY
        reason = "no valid HOS records found"

    diagnostics = {
        "source_state": source_state,
        "schema_version": SCHEMA_VERSION,
        "repo_root": str(REPO_ROOT),
        "files_found": len(files),
        "files_invalid": len(invalid_files),
        "records": len(records),
        "relations": len(relations),
        "reason": reason,
        "fallback_used": False,
        "invalid_files": invalid_files,
    }
    return records, relations, files, diagnostics


def build_adjacency(relations, mode: str):
    adjacency = defaultdict(list)
    for relation in relations:
        adjacency[relation["source"]].append(relation)
        if mode == "undirected":
            adjacency[relation["target"]].append({
                "source": relation["target"], "target": relation["source"],
                "relation": relation["relation"], "_reverse": True,
            })
    return adjacency


def traverse(start_id: str, depth: int, records, relations, mode: str = "directed"):
    if start_id not in records:
        candidates = [rid for rid in records if start_id.lower() in rid.lower()]
        if not candidates:
            return {}, []
        start_id = candidates[0]
    adjacency = build_adjacency(relations, mode)
    visited = {start_id: 0}
    queue = deque([(start_id, 0)])
    seen_edges = set()
    collected = []
    while queue:
        current, distance = queue.popleft()
        if distance >= depth:
            continue
        for relation in adjacency.get(current, []):
            if mode == "directed" and relation.get("_reverse"):
                continue
            source, target, relation_type = relation["source"], relation["target"], relation["relation"]
            edge_key = (source, target, relation_type)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                collected.append({"source": source, "target": target, "relation": relation_type, "depth": distance})
            other = source if mode == "undirected" and relation.get("_reverse") else target
            if other in records and other not in visited:
                visited[other] = distance + 1
                queue.append((other, distance + 1))
    visited_ids = set(visited)
    final_edges, final_seen = [], set()
    for edge in collected:
        if edge["source"] not in visited_ids or edge["target"] not in visited_ids:
            continue
        key = (edge["source"], edge["target"], edge["relation"])
        if key not in final_seen:
            final_seen.add(key)
            final_edges.append(edge)
    return visited, final_edges


def record_title(record: dict) -> str:
    return record.get("title", "")


def record_category(record: dict) -> str:
    return record.get("category", "")


def cmd_stats(records, relations, files, diagnostics, mode: str):
    print(f"\n=== SKYNET STATS REAL [{mode.upper()}] ===")
    print(f"SOURCE: {diagnostics['source_state']} | SCHEMA: {diagnostics['schema_version']}")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Plików JSON: {len(files)} | Rekordów: {len(records)} | Relacji: {len(relations)}")
    unique_relations = {(r["source"], r["target"], r["relation"]) for r in relations}
    print(f"Relacji unikalnych: {len(unique_relations)}")
    by_corpus, by_category = defaultdict(int), defaultdict(int)
    for record in records.values():
        by_corpus[record.get("corpus") or "?"] += 1
        by_category[record_category(record) or "?"] += 1
    print("\nPer corpus:")
    for key, value in sorted(by_corpus.items()): print(f"  {key}: {value}")
    print("\nPer category/type:")
    for key, value in sorted(by_category.items()): print(f"  {key}: {value}")


def cmd_graph(start_id: str, depth: int, records, relations, diagnostics, mode: str):
    visited, edges = traverse(start_id, depth, records, relations, mode)
    print(f"\n=== SKYNET GRAPH REAL [{mode.upper()}]: {start_id} depth={depth} ===")
    print(f"SOURCE: {diagnostics['source_state']} | SCHEMA: {diagnostics['schema_version']}")
    print(f"Węzłów: {len(visited)} | Krawędzi: {len(edges)} | Przeszukano do głębokości {depth}")
    for node_id, distance in sorted(visited.items(), key=lambda item: (item[1], item[0])):
        record = records[node_id]
        print(f"[{node_id}] {record_title(record)} ({record_category(record)}/{record.get('corpus') or ''}) dist={distance}")
    print("\n--- RELACJE (deduplikowane) ---")
    for edge in sorted(edges, key=lambda item: (item["source"], item["relation"], item["target"])):
        source_name = record_title(records.get(edge["source"], {})) or edge["source"]
        target_name = record_title(records.get(edge["target"], {})) or edge["target"]
        print(f"{source_name} --[{edge['relation']}]--> {target_name} ({edge['target']})")
    output = {
        "schema_version": SCHEMA_VERSION, "source_state": diagnostics["source_state"],
        "start": start_id, "depth": depth, "mode": mode, "repo_root": str(REPO_ROOT),
        "nodes_count": len(visited), "edges_count": len(edges),
        "nodes": [{"id": node_id, "distance": distance, "title": records[node_id]["title"],
                   "category": records[node_id]["category"], "corpus": records[node_id].get("corpus")}
                  for node_id, distance in visited.items()],
        "edges": [{"from": e["source"], "type": e["relation"], "to": e["target"]} for e in edges],
    }
    output_path = REPO_ROOT / f"graph-{start_id}-{depth}-{mode}.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[SKYNET REAL] Zapisano: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="SKYNET REAL - Historian OS SKYNET")
    parser.add_argument("cmd", nargs="?", default="stats", choices=["stats", "list", "graph"])
    parser.add_argument("arg1", nargs="?", help="ID dla graph")
    parser.add_argument("arg2", nargs="?", help="depth dla graph")
    parser.add_argument("--mode", choices=["directed", "undirected"], default="directed")
    args = parser.parse_args()
    records, relations, files, diagnostics = load_corpus()
    if args.cmd == "stats":
        cmd_stats(records, relations, files, diagnostics, args.mode)
    elif args.cmd == "list":
        print(f"\n=== {len(records)} REKORDÓW {diagnostics['source_state']} ===")
        for record_id in sorted(records):
            record = records[record_id]
            print(f"{record_id} | {record_title(record)} | {record.get('corpus') or '-'} | {record.get('_source_file', '')}")
    else:
        start_id = args.arg1 or "HOS-PERSON-JAN-ZUMBACH"
        depth = int(args.arg2) if args.arg2 and args.arg2.isdigit() else 2
        cmd_graph(start_id, depth, records, relations, diagnostics, args.mode)


if __name__ == "__main__":
    main()
