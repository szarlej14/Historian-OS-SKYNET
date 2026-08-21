#!/usr/bin/env python3
"""Local query engine for Historian OS SKYNET.

Commands:
  search <text>      Full-text search across data records.
  show <id>          Show one record by HOS id.
  related <id>       Show directly related records.
  stats              Print corpus statistics.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def records():
    for p in sorted(DATA.glob("*.json")):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("id", "").startswith("HOS-"):
            yield obj


def rid(obj):
    return obj.get("id", "")


def text(obj):
    return json.dumps(obj, ensure_ascii=False).lower()


def show(obj):
    print(f"{rid(obj)} | {obj.get('title','')}")
    print(f"status: {obj.get('status','')}")
    print(f"corpus: {obj.get('corpus','')}")
    print(f"category: {obj.get('category','')}")
    if obj.get("date"):
        print(f"date: {obj['date']}")
    if obj.get("summary"):
        print(f"summary: {obj['summary']}")
    if obj.get("relations"):
        print("relations: " + ", ".join(obj["relations"]))
    if obj.get("sources"):
        print("sources: " + ", ".join(obj["sources"]))


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__.strip())
        return 0
    rs = list(records())
    cmd = args[0]
    if cmd == "search":
        q = " ".join(args[1:]).lower().strip()
        hits = [r for r in rs if q in text(r)]
        for r in hits:
            print(f"{rid(r)} | {r.get('title','')}")
        print(f"\n{len(hits)} wynik(ów)")
        return 0
    if cmd == "show" and len(args) >= 2:
        for r in rs:
            if rid(r) == args[1]:
                show(r)
                return 0
        print("Nie znaleziono rekordu:", args[1])
        return 1
    if cmd == "related" and len(args) >= 2:
        target = args[1]
        hits = [r for r in rs if target in r.get("relations", [])]
        for r in hits:
            print(f"{rid(r)} | {r.get('title','')}")
        print(f"\n{len(hits)} powiązanych rekordów")
        return 0
    if cmd == "stats":
        from collections import Counter
        print("records:", len(rs))
        print("status:", dict(Counter(r.get("status", "unknown") for r in rs)))
        print("corpus:", dict(Counter(r.get("corpus", "unknown") for r in rs)))
        print("categories:", dict(Counter(r.get("category", "unknown") for r in rs)))
        return 0
    print(__doc__.strip())
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
