#!/usr/bin/env python3
"""Zero-dependency HTTP API for Historian OS SKYNET.

Endpoints: /health, /stats, /search?q=..., /record/<HOS-ID>,
/related/<HOS-ID>, /graph, /path?from=<HOS-ID>&to=<HOS-ID>
"""
import json
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
GRAPH = ROOT / "index" / "graph.json"


def records():
    for path in sorted(DATA.glob("*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("id", "").startswith("HOS-"):
            yield obj


def all_records():
    return list(records())


def find_record(rs, record_id):
    return next((r for r in rs if r.get("id") == record_id), None)


def blob_text(obj):
    return json.dumps(obj, ensure_ascii=False).lower()


def load_graph():
    try:
        return json.loads(GRAPH.read_text(encoding="utf-8"))
    except Exception:
        return {"type": "knowledge_graph", "nodes": [], "edges": [], "traversal_edges": []}


def neighbors(rs, record_id):
    ids = {r.get("id") for r in rs}
    target = find_record(rs, record_id)
    if not target:
        return set()
    out = set(target.get("relations", [])) & ids
    for r in rs:
        if record_id in r.get("relations", []):
            out.add(r.get("id"))
    return out


def shortest_path(rs, start, target):
    if not find_record(rs, start) or not find_record(rs, target):
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


class Handler(BaseHTTPRequestHandler):
    server_version = "HistorianOS/0.3"

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        rs = all_records()

        if path == "/health":
            self.send_json({"ok": True, "service": "historian-os", "version": "0.3", "records": len(rs)})
            return
        if path == "/stats":
            from collections import Counter
            self.send_json({"records": len(rs), "status": dict(Counter(r.get("status", "unknown") for r in rs)), "corpus": dict(Counter(r.get("corpus", "unknown") for r in rs)), "categories": dict(Counter(r.get("category", "unknown") for r in rs))})
            return
        if path == "/graph":
            self.send_json(load_graph())
            return
        if path == "/search":
            q = " ".join(query.get("q", [""])).strip().lower()
            if not q:
                self.send_json({"error": "Parametr q jest wymagany."}, 400)
                return
            terms = q.split()
            hits = [r for r in rs if all(term in blob_text(r) for term in terms)]
            self.send_json({"query": q, "count": len(hits), "results": hits})
            return
        if path.startswith("/record/"):
            rid = unquote(path[len("/record/"):])
            obj = find_record(rs, rid)
            self.send_json(obj if obj else {"error": "Nie znaleziono rekordu.", "id": rid}, 200 if obj else 404)
            return
        if path.startswith("/related/"):
            rid = unquote(path[len("/related/"):])
            if not find_record(rs, rid):
                self.send_json({"error": "Nie znaleziono rekordu.", "id": rid}, 404)
                return
            related = [r for r in rs if r.get("id") in neighbors(rs, rid)]
            self.send_json({"id": rid, "count": len(related), "results": related})
            return
        if path == "/path":
            start = query.get("from", [""])[0]
            target = query.get("to", [""])[0]
            result = shortest_path(rs, start, target)
            if result is None:
                self.send_json({"error": "Brak ścieżki albo nieznany rekord.", "from": start, "to": target}, 404)
                return
            self.send_json({"from": start, "to": target, "length": len(result) - 1, "path": result, "records": [find_record(rs, rid) for rid in result]})
            return

        self.send_json({"service": "Historian OS SKYNET API", "endpoints": ["/health", "/stats", "/search?q=...", "/record/<HOS-ID>", "/related/<HOS-ID>", "/graph", "/path?from=<HOS-ID>&to=<HOS-ID>"]})

    def log_message(self, fmt, *args):
        print("[historian-api]", fmt % args)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Historian OS SKYNET HTTP API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Historian OS API: http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
