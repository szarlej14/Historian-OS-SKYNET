#!/usr/bin/env python3
"""HistorianOS Command Center API: queue, decisions, dashboard stats, health."""
import json, sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"historianos.sqlite3"
UI=Path(__file__).with_name("command_center.html")

SCHEMA="""CREATE TABLE IF NOT EXISTS conflict_ledger(
 conflict_id TEXT PRIMARY KEY, entity_id TEXT, attribute TEXT,
 source_a_val TEXT, source_b_val TEXT, status TEXT NOT NULL DEFAULT 'OPEN',
 golden_value TEXT, decision_note TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 updated_at TEXT DEFAULT CURRENT_TIMESTAMP, resolved_at TEXT)
"""
DECISIONS="""CREATE TABLE IF NOT EXISTS decision_log(
 decision_id TEXT PRIMARY KEY, conflict_id TEXT, action TEXT NOT NULL,
 author TEXT NOT NULL, justification TEXT NOT NULL, golden_value TEXT,
 created_at TEXT DEFAULT CURRENT_TIMESTAMP)
"""
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute(SCHEMA); c.execute(DECISIONS); return c
class H(BaseHTTPRequestHandler):
 def send(self,code,obj,ctype="application/json"):
  b=obj if isinstance(obj,bytes) else json.dumps(obj,ensure_ascii=False).encode()
  self.send_response(code); self.send_header("Content-Type",ctype); self.send_header("Cache-Control","no-store"); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers(); self.wfile.write(b)
 def do_OPTIONS(self): self.send(204,{})
 def do_GET(self):
  if self.path in ("/","/index.html"): return self.send(200,UI.read_bytes(),"text/html; charset=utf-8")
  c=db()
  if self.path=="/api/health": return self.send(200,{"ok":True,"db":str(DB),"schema":"ready"})
  if self.path=="/api/stats":
   return self.send(200,{r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM conflict_ledger GROUP BY status")})
  if self.path=="/api/queue":
   return self.send(200,[dict(r) for r in c.execute("SELECT * FROM conflict_ledger WHERE status IN ('OPEN','EXPORTED') ORDER BY updated_at DESC")])
  if self.path=="/api/decisions":
   return self.send(200,[dict(r) for r in c.execute("SELECT * FROM decision_log ORDER BY created_at DESC LIMIT 100")])
  return self.send(404,{"error":"not_found"})
 def do_POST(self):
  if not self.path.startswith("/api/decision/"): return self.send(404,{"error":"not_found"})
  cid=self.path.rsplit("/",1)[-1]; n=int(self.headers.get("Content-Length","0"))
  try: body=json.loads(self.rfile.read(n) or b"{}")
  except: return self.send(400,{"error":"invalid_json"})
  action=body.get("action"); author=(body.get("author") or "").strip(); value=(body.get("golden_value") or "").strip(); note=(body.get("justification") or "").strip()
  if action not in {"APPROVE","REJECT","MERGE"}: return self.send(400,{"error":"invalid_action"})
  if not author or not note: return self.send(400,{"error":"author_and_justification_required"})
  if action in {"APPROVE","MERGE"} and not value: return self.send(400,{"error":"golden_value_required"})
  c=db(); row=c.execute("SELECT * FROM conflict_ledger WHERE conflict_id=? AND status IN ('OPEN','EXPORTED')",(cid,)).fetchone()
  if not row: return self.send(409,{"error":"conflict_not_open","conflict_id":cid})
  status="RESOLVED" if action in {"APPROVE","MERGE"} else "OPEN"
  c.execute("UPDATE conflict_ledger SET status=?,golden_value=?,decision_note=?,updated_at=CURRENT_TIMESTAMP,resolved_at=CASE WHEN ?='RESOLVED' THEN CURRENT_TIMESTAMP ELSE resolved_at END WHERE conflict_id=?",(status,value,note,status,cid))
  did=f"{cid}-{action}-{row['updated_at'] or ''}"
  c.execute("INSERT OR IGNORE INTO decision_log(decision_id,conflict_id,action,author,justification,golden_value) VALUES(?,?,?,?,?,?)",(did,cid,action,author,note,value))
  c.commit(); return self.send(200,{"ok":True,"conflict_id":cid,"status":status,"action":action})
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser(); p.add_argument("--host",default="127.0.0.1"); p.add_argument("--port",type=int,default=8000); a=p.parse_args()
 print(f"HistorianOS Command Center: http://{a.host}:{a.port}")
 ThreadingHTTPServer((a.host,a.port),H).serve_forever()
