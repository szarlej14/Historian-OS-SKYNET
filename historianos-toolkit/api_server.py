#!/usr/bin/env python3
"""Read-only Knowledge Fabric REST API."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, os, re
ROOT=Path(os.environ.get("HISTORIANOS_VAULT","/vault")).resolve()

def files(): return list(ROOT.rglob("*.md")) if ROOT.exists() else []
def parse(p):
    t=p.read_text(encoding="utf-8",errors="ignore"); out={"file":str(p.relative_to(ROOT))}
    for line in t.splitlines():
        m=re.match(r'^([A-Za-z_][\w-]*):\s*["\']?(.*?)["\']?$',line)
        if m: out[m.group(1)]=m.group(2)
    return out
def records(kind=None):
    xs=[]
    for p in files():
        r=parse(p)
        if not kind or r.get("type")==kind: xs.append(r)
    return xs

class Handler(BaseHTTPRequestHandler):
    def send_json(self,o,c=200):
        b=json.dumps(o,ensure_ascii=False).encode(); self.send_response(c)
        self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        path=self.path.split("?",1)[0]
        routes={"/api/health":lambda:{"status":"ok","mode":"read-only"},
                "/api/entities":lambda:{"items":records()},
                "/api/events":lambda:{"items":records("wydarzenie")},
                "/api/sources":lambda:{"items":records("zrodlo")},
                "/api/relations":lambda:{"items":records("relacja")},
                "/api/gaps":lambda:{"items":[{"type":"ORPHAN_FACT","file":r["file"]} for r in records("fakt") if not any(k in r for k in ("zrodlo","źródło","zrodla","sources"))]},
                "/api/provenance":lambda:{"items":[r for r in records() if any(k in r for k in ("zrodlo","źródło","zrodla","sources"))]}}
        if path in routes:return self.send_json(routes[path]())
        return self.send_json({"error":"not_found"},404)
    def log_message(self,*a):pass
if __name__=="__main__": ThreadingHTTPServer(("0.0.0.0",int(os.environ.get("PORT","8080"))),Handler).serve_forever()
