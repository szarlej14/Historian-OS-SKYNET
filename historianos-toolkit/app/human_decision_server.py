#!/usr/bin/env python3
"""Minimal stdlib HTTP API + UI for the Human Decision queue."""
import json,sqlite3
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
DB=Path("historianos.sqlite3"); UI=Path(__file__).with_name("human_decision.html")
SCHEMA="CREATE TABLE IF NOT EXISTS decision_log(decision_id TEXT PRIMARY KEY,conflict_id TEXT,action TEXT,author TEXT,justification TEXT,golden_value TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
class H(BaseHTTPRequestHandler):
 def send(self,code,data,ctype="application/json"):
  b=data if isinstance(data,bytes) else data.encode(); self.send_response(code); self.send_header("Content-Type",ctype); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  if self.path=="/": return self.send(200,UI.read_bytes(),"text/html; charset=utf-8")
  if self.path=="/api/queue":
   c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute("CREATE TABLE IF NOT EXISTS conflict_ledger(conflict_id TEXT PRIMARY KEY,entity_id TEXT,attribute TEXT,source_a_val TEXT,source_b_val TEXT,status TEXT,golden_value TEXT,decision_note TEXT,resolved_at TEXT)")
   rows=[dict(x) for x in c.execute("SELECT * FROM conflict_ledger WHERE status IN ('OPEN','EXPORTED') ORDER BY updated_at DESC")]; return self.send(200,json.dumps(rows,ensure_ascii=False))
  return self.send(404,"{}")
 def do_POST(self):
  if not self.path.startswith("/api/decision/"): return self.send(404,"{}")
  cid=self.path.rsplit("/",1)[-1]; n=int(self.headers.get("Content-Length","0")); body=json.loads(self.rfile.read(n) or b"{}"); action=body.get("action",""); author=body.get("author","Piotr Florczyk"); value=body.get("golden_value",""); note=body.get("justification","")
  if action not in {"APPROVE","REJECT","MERGE"}: return self.send(400,json.dumps({"error":"invalid action"}))
  c=sqlite3.connect(DB); c.execute(SCHEMA)
  status="RESOLVED" if action in {"APPROVE","MERGE"} else "OPEN"
  c.execute("UPDATE conflict_ledger SET status=?,golden_value=?,decision_note=?,resolved_at=CASE WHEN ?='RESOLVED' THEN CURRENT_TIMESTAMP ELSE resolved_at END WHERE conflict_id=? AND status IN ('OPEN','EXPORTED')",(status,value,note,status,cid))
  c.execute("INSERT OR REPLACE INTO decision_log(decision_id,conflict_id,action,author,justification,golden_value) VALUES(?,?,?,?,?,?)",(cid+"-"+action,cid,action,author,note,value)); c.commit()
  return self.send(200,json.dumps({"ok":True,"conflict_id":cid,"status":status}))
if __name__=="__main__":
 import argparse; p=argparse.ArgumentParser(); p.add_argument("--port",type=int,default=8000); a=p.parse_args(); print(f"Human Decision: http://localhost:{a.port}"); HTTPServer(("0.0.0.0",a.port),H).serve_forever()
