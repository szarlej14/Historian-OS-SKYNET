#!/usr/bin/env python3
"""SKYNET knowledge-graph query layer for Historian OS.

Commands:
  ask <text>             Search records and expand their relation graph.
  path <id> <id>         Find a shortest relation path between two records.
  graph <id> [depth]     Expand the graph around one record.
"""
import json
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def records():
    result = {}
    for path in sorted(DATA.glob("*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("id", "").startswith("HOS-"):
            result[obj["id"]] = obj
    return result


def neighbors(rs, rid):
    obj = rs.get(rid)
    if not obj:
        return set()
    out = set(obj.get("relations", [])) & set(rs)
    for other_id, other in rs.items():
        if rid in other.get("relations", []):
            out.add(other_id)
    return out


def graph(rs, start, depth=2):
    if start not in rs:
        return {}
    seen = {start: 0}
    q = deque([start])
    while q:
        current = q.popleft()
        if seen[current] >= depth:
            continue
        for nxt in neighbors(rs, current):
            if nxt not in seen:
                seen[nxt] = seen[current] + 1
                q.append(nxt)
    return seen


def shortest_path(rs, start, target):
    if start not in rs or target not in rs:
        return None
    q = deque([start])
    previous = {start: None}
    while q:
        current = q.popleft()
        if current == target:
            path = []
            while current is not None:
                path.append(current)
                current = previous[current]
            return list(reversed(path))
        for nxt in neighbors(rs, current):
            if nxt not in previous:
                previous[nxt] = current
                q.append(nxt)
    return None


def score(obj, terms):
    text = json.dumps(obj, ensure_ascii=False).lower()
    return sum(text.count(term) for term in terms)


def print_record(rs, rid):
    obj = rs[rid]
    print(f"{rid} | {obj.get('title', '')}")
    print(f"  corpus: {obj.get('corpus', '')}")
    print(f"  category: {obj.get('category', '')}")
    print(f"  summary: {obj.get('summary', '')}")


def main():
    args = sys.argv[1:]
    rs = records()
    if not args:
        print(__doc__.strip())
        return 0

    cmd = args[0]
    if cmd == "ask" and len(args) > 1:
        terms = [x.lower() for x in " ".join(args[1:]).split()]
        hits = sorted(rs, key=lambda r: score(rs[r], terms), reverse=True)
        hits = [r for r in hits if score(rs[r], terms) > 0][:10]
        print(f"ZNALEZIONO: {len(hits)}")
        for rid in hits:
            print_record(rs, rid)
            ids = graph(rs, rid, 2)
            related = [x for x in ids if x != rid]
            if related:
                print("  graf:", ", ".join(related))
        return 0

    if cmd == "graph" and len(args) >= 2:
        depth = int(args[2]) if len(args) >= 3 else 2
        expanded = graph(rs, args[1], depth)
        if not expanded:
            print("Nie znaleziono rekordu:", args[1])
            return 1
        for rid, level in sorted(expanded.items(), key=lambda x: (x[1], x[0])):
            print(f"{level}: {rid} | {rs[rid].get('title', '')}")
        return 0

    if cmd == "path" and len(args) >= 3:
        result = shortest_path(rs, args[1], args[2])
        if result is None:
            print("Brak ścieżki.")
            return 1
        print(" -> ".join(result))
        for rid in result:
            print_record(rs, rid)
        return 0

    print(__doc__.strip())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
