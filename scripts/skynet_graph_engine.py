#!/usr/bin/env python3
"""SKYNET Graph Engine REAL for Historian OS SKYNET.

Reads the repository's real JSON corpus instead of assuming /mnt/data/HOS-*.json.
Supports both relation formats currently present in the project:
  - ["HOS-..."]
  - [{"type": "related_to", "target": "HOS-...", ...}]

The loader also understands the canonical field names used by the corpus:
  title/category
and remains compatible with name/type when older records use them.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import defaultdict, deque
from pathlib import Path


def find_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    candidates = [cwd, *cwd.parents]
    candidates += [
        Path("/storage/emulated/0/Documents/Historian-OS-SKYNET"),
        Path("/storage/emulated/0/Documents/Pete"),
        Path("/mnt/data"),
    ]
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
    "data/*.json",
    "data/**/*.json",
    "memory/data/*.json",
    "memory/data/**/*.json",
    "index/*.json",
    "data/corpus/*/*.json",
    "data/records/*.json",
    "Pete/memory/data/corpus/*/*.json",
    "HOS-*.json",
    "/mnt/data/HOS-*.json",
)


def find_json_files() -> list[str]:
    files: set[str] = set()
    for pattern in SEARCH_PATTERNS:
        files.update(glob.glob(str(REPO_ROOT / pattern), recursive=True))
        if not pattern.startswith("/"):
            files.update(glob.glob(pattern, recursive=True))
    return sorted(files)


def normalize_relation(source_id: str, relation) -> dict | None:
    if isinstance(relation, str):
        target = relation.strip()
        if not target:
            return None
        return {"source": source_id, "target": target, "relation": "related_to"}

    if isinstance(relation, dict):
        target = relation.get("target") or relation.get("to") or relation.get("id")
        if not target:
            return None
        relation_type = (
            relation.get("type")
            or relation.get("relation")
            or relation.get("label")
            or "related_to"
        )
        return {
            "source": source_id,
            "target": target,
            "relation": relation_type,
        }
    return None


def load_corpus():
    records: dict[str, dict] = {}
    relations: list[dict] = []
    files = find_json_files()

    print(f"[SKYNET REAL] Repo root: {REPO_ROOT}")
    print(f"[SKYNET REAL] Znaleziono {len(files)} plików JSON")

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:
            print(f"[WARN] {filepath}: {exc}", file=sys.stderr)
            continue

        items = payload if isinstance(payload, list) else [payload]
        for record in items:
            if not isinstance(record, dict):
                continue
            record_id = record.get("id")
            if not record_id:
                continue

            if record_id not in records:
                record = dict(record)
                record["_source_file"] = filepath
                records[record_id] = record

            for raw_relation in record.get("relations", []):
                normalized = normalize_relation(record_id, raw_relation)
                if normalized:
                    relations.append(normalized)

    return records, relations, files


def build_adjacency(relations, mode: str):
    adjacency = defaultdict(list)
    for relation in relations:
        adjacency[relation["source"]].append(relation)
        if mode == "undirected":
            adjacency[relation["target"]].append(
                {
                    "source": relation["target"],
                    "target": relation["source"],
                    "relation": relation["relation"],
                    "_reverse": True,
                }
            )
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

            source = relation["source"]
            target = relation["target"]
            relation_type = relation["relation"]
            edge_key = (source, target, relation_type)

            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                collected.append(
                    {
                        "source": source,
                        "target": target,
                        "relation": relation_type,
                        "depth": distance,
                    }
                )

            other = target
            if mode == "undirected" and relation.get("_reverse"):
                other = source

            if other in records and other not in visited:
                visited[other] = distance + 1
                queue.append((other, distance + 1))

    visited_ids = set(visited)
    final_edges = []
    final_seen = set()
    for edge in collected:
        if edge["source"] not in visited_ids or edge["target"] not in visited_ids:
            continue
        key = (edge["source"], edge["target"], edge["relation"])
        if key not in final_seen:
            final_seen.add(key)
            final_edges.append(edge)

    return visited, final_edges


def record_title(record: dict) -> str:
    return record.get("title") or record.get("name") or ""


def record_category(record: dict) -> str:
    return record.get("category") or record.get("type") or ""


def cmd_stats(records, relations, files, mode: str):
    print(f"\n=== SKYNET STATS REAL [{mode.upper()}] ===")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Plików JSON: {len(files)}")
    print(f"Rekordów: {len(records)}")
    print(f"Relacji surowych: {len(relations)}")
    unique_relations = {(r["source"], r["target"], r["relation"]) for r in relations}
    print(f"Relacji unikalnych: {len(unique_relations)}")

    by_corpus = defaultdict(int)
    by_category = defaultdict(int)
    for record in records.values():
        by_corpus[record.get("corpus", "?")] += 1
        by_category[record_category(record) or "?"] += 1

    print("\nPer corpus:")
    for key, value in sorted(by_corpus.items()):
        print(f"  {key}: {value}")

    print("\nPer category/type:")
    for key, value in sorted(by_category.items()):
        print(f"  {key}: {value}")


def cmd_graph(start_id: str, depth: int, records, relations, mode: str):
    visited, edges = traverse(start_id, depth, records, relations, mode)
    print(f"\n=== SKYNET GRAPH REAL [{mode.upper()}]: {start_id} depth={depth} ===")
    print(f"Repo: {REPO_ROOT}")
    print(f"Węzłów: {len(visited)} | Krawędzi: {len(edges)} | Przeszukano do głębokości {depth} | Tryb: {mode}\n")

    for node_id, distance in sorted(visited.items(), key=lambda item: (item[1], item[0])):
        record = records.get(node_id, {})
        print(
            f"[{node_id}] {record_title(record)} "
            f"({record_category(record)}/{record.get('corpus', '')}) "
            f"dist={distance} <- {record.get('_source_file', '')}"
        )

    print("\n--- RELACJE (deduplikowane) ---")
    for edge in sorted(edges, key=lambda item: (item["source"], item["relation"], item["target"])):
        source_name = record_title(records.get(edge["source"], {})) or edge["source"]
        target_name = record_title(records.get(edge["target"], {})) or edge["target"]
        print(f"{source_name} --[{edge['relation']}]--> {target_name} ({edge['target']})")

    output = {
        "start": start_id,
        "depth": depth,
        "mode": mode,
        "repo_root": str(REPO_ROOT),
        "nodes_count": len(visited),
        "edges_count": len(edges),
        "nodes": [
            {
                "id": node_id,
                "distance": distance,
                "title": record_title(records[node_id]),
                "category": record_category(records[node_id]),
                "corpus": records[node_id].get("corpus"),
            }
            for node_id, distance in visited.items()
        ],
        "edges": [
            {"from": edge["source"], "type": edge["relation"], "to": edge["target"]}
            for edge in edges
        ],
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

    records, relations, files = load_corpus()

    if args.cmd == "stats":
        cmd_stats(records, relations, files, args.mode)
    elif args.cmd == "list":
        print(f"\n=== {len(records)} REKORDÓW REAL ===")
        for record_id in sorted(records):
            record = records[record_id]
            print(f"{record_id} | {record_title(record)} | {record.get('corpus', '-')} | {record.get('_source_file', '')}")
    else:
        start_id = args.arg1 or "HOS-PERSON-JAN-ZUMBACH"
        depth = int(args.arg2) if args.arg2 and args.arg2.isdigit() else 2
        cmd_graph(start_id, depth, records, relations, args.mode)


if __name__ == "__main__":
    main()
