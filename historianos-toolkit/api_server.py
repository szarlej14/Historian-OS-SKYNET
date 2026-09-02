#!/usr/bin/env python3
"""Minimal read-only REST API for the Historian OS Command Center."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os
from pathlib import Path

ROOT=Path(os.environ.get("HISTORIANOS_VAULT","/vault")).resolve()

def md_files():
    return list(ROOT.rglob("*.md")) if ROOT.exists() else []

def stats():
    counts={}
    for p in md_files():
        t=p.read_text(encoding="utf-8",errors="ignore")
        for k in ("fakt","wydarzenie","miejsce","relacja","seria","zrodlo"):
            counts[k]=counts.get(k,0)+t.count("type: "+k)
    return counts

class Handler(BaseHTTPRequestHandler):
    def send_json(self, obj, code=200):
        data=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path=="/api/health":
            return self.send_json({"status":"ok","service":"Historian OS Command Center"})
        if self.path=="/api/stats":
            return self.send_json({"vault":str(ROOT),"stats":stats()})
        if self.path=="/api/files":
            return self.send_json({"files":[str(p.relative_to(ROOT)) for p in md_files()]})
        return self.send_json({"error":"not_found"},404)
    def log_message(self,*args): pass

if __name__=="__main__":
    port=int(os.environ.get("PORT","8080"))
    HTTPServer(("0.0.0.0",port),Handler).serve_forever()
