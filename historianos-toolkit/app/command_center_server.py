#!/usr/bin/env python3
import json,os,sqlite3,subprocess,sys
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DB=Path(os.environ.get("HISTORIANOS_DB", str(ROOT/"historianos.sqlite3"))).resolve(); UI=Path(__file__).with_name("command_center.html")
SCHEMA="CREATE TABLE IF NOT EXISTS conflict_ledger(conflict_id TEXT PRIMARY KEY,entity_id TEXT,attribute TEXT,source_a_val TEXT,source_b_val TEXT,status TEXT NOT NULL DEFAULT 'OPEN',golden_value TEXT,decision_note TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP,resolved_at TEXT)"
DECISIONS="CREATE TABLE IF NOT EXISTS decision_log(decision_id TEXT PRIMARY KEY,conflict_id TEXT,action TEXT NOT NULL,author TEXT NOT NULL,justification TEXT NOT NULL,golden_value TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute(SCHEMA);c.execute(DECISIONS);c.commit();return c
def send(h,code,obj,ct="application/json"):
 b=obj if isinstance(obj,bytes) else json.dumps(obj,ensure_ascii=False).encode();h.send_response(code);h.send_header("Content-Type",ct);h.send_header("Cache-Control","no-store");h.send_header("Access-Control-Allow-Origin","*");h.send_header("Access-Control-Allow-Headers","Content-Type");h.end_headers();h.wfile.write(b)
class H(BaseHTTPRequestHandler):
 def do_OPTIONS(self):send(self,204,{})
 def do_GET(self):
  if self.path in ("/","/index.html"):return send(self,200,UI.read_bytes(),"text/html; charset=utf-8")
  c=db()
  if self.path=="/api/health":return send(self,200,{"ok":True,"db":str(DB),"schema":"ready"})
  if self.path=="/api/stats":return send(self,200,{r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM conflict_ledger GROUP BY status")})
  if self.path=="/api/queue":return send(self,200,[dict(r) for r in c.execute("SELECT * FROM conflict_ledger WHERE status IN ('OPEN','EXPORTED') ORDER BY updated_at DESC")])
  if self.path=="/api/decisions":return send(self,200,[dict(r) for r in c.execute("SELECT * FROM decision_log ORDER BY created_at DESC LIMIT 200")])
  return send(self,404,{"error":"not_found"})
 def do_POST(self):
  if self.path=="/api/selection/run":
   try:
    p=subprocess.run([sys.executable,str(ROOT/"app"/"selection_engine.py"),str(ROOT)],capture_output=True,text=True,timeout=300)
    f=ROOT/"selection_report.json";d=json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    return send(self,200,{"ok":p.returncode==0,"stats":d.get("stats",{}),"stderr":p.stderr[-4000:]})
   except Exception as e:return send(self,500,{"ok":False,"error":str(e)})
  if not self.path.startswith("/api/decision/"):return send(self,404,{"error":"not_found"})
  cid=self.path.rsplit("/",1)[-1];n=int(self.headers.get("Content-Length","0"))
  try:b=json.loads(self.rfile.read(n) or b"{}")
  except:return send(self,400,{"error":"invalid_json"})
  a=b.get("action");author=(b.get("author") or "").strip();v=(b.get("golden_value") or "").strip();note=(b.get("justification") or "").strip()
  if a not in {"APPROVE","REJECT","MERGE"} or not author or not note or (a!="REJECT" and not v):return send(self,400,{"error":"invalid_decision_payload"})
  c=db();row=c.execute("SELECT * FROM conflict_ledger WHERE conflict_id=? AND status IN ('OPEN','EXPORTED')",(cid,)).fetchone()
  if not row:return send(self,409,{"error":"conflict_not_open"})
  status="RESOLVED" if a in {"APPROVE","MERGE"} else "OPEN"
  c.execute("UPDATE conflict_ledger SET status=?,golden_value=?,decision_note=?,updated_at=CURRENT_TIMESTAMP,resolved_at=CASE WHEN ?='RESOLVED' THEN CURRENT_TIMESTAMP ELSE resolved_at END WHERE conflict_id=?",(status,v,note,status,cid))
  c.execute("INSERT OR IGNORE INTO decision_log VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP)",(cid+"-"+a+"-"+str(row["updated_at"]),cid,a,author,note,v));c.commit()
  return send(self,200,{"ok":True,"conflict_id":cid,"status":status,"action":a})
if __name__=="__main__":
 import argparse;p=argparse.ArgumentParser();p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=8000);x=p.parse_args();print(f"HistorianOS Command Center: http://{x.host}:{x.port}");ThreadingHTTPServer((x.host,x.port),H).serve_forever()
