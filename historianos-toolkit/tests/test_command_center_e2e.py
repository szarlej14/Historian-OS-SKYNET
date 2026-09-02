#!/usr/bin/env python3
"""HistorianOS end-to-end contract test.
Verifies: selection report -> SQLite ledger -> API decision -> Decision Log -> RESOLVED.
Run from historianos-toolkit: python tests/test_command_center_e2e.py
"""
import json,sqlite3,tempfile,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/"app"/"command_center_server.py"
def req(url,method="GET",payload=None):
 data=None
 if payload is not None:data=json.dumps(payload).encode()
 r=urllib.request.Request(url,data=data,method=method,headers={"Content-Type":"application/json"})
 with urllib.request.urlopen(r,timeout=5) as x:return json.loads(x.read())
def main():
 with tempfile.TemporaryDirectory() as td:
  work=Path(td); db=work/"historianos.sqlite3"
  # Isolate server DB by launching from temp working directory while importing server by absolute path.
  p=subprocess.Popen([sys.executable,str(SERVER),"--host","127.0.0.1","--port","8765"],cwd=work,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   for _ in range(30):
    try:
     if req("http://127.0.0.1:8765/api/health")["ok"]:break
    except Exception:time.sleep(.1)
   else:raise AssertionError("Command Center health check failed")
   c=sqlite3.connect(db)
   c.execute("CREATE TABLE conflict_ledger(conflict_id TEXT PRIMARY KEY,entity_id TEXT,attribute TEXT,source_a_val TEXT,source_b_val TEXT,status TEXT,golden_value TEXT,decision_note TEXT,created_at TEXT,updated_at TEXT,resolved_at TEXT)")
   c.execute("CREATE TABLE decision_log(decision_id TEXT PRIMARY KEY,conflict_id TEXT,action TEXT,author TEXT,justification TEXT,golden_value TEXT,created_at TEXT)")
   c.execute("INSERT INTO conflict_ledger VALUES('E2E-001','Test Person','birth_year','1762','1763','OPEN','','','','','','')")
   c.commit();c.close()
   q=req("http://127.0.0.1:8765/api/queue");assert len(q)==1 and q[0]["conflict_id"]=="E2E-001"
   bad=None
   try:req("http://127.0.0.1:8765/api/decision/E2E-001","POST",{"action":"APPROVE","author":"Piotr Florczyk","justification":"missing golden"})
   except urllib.error.HTTPError as e:bad=e.code
   assert bad==400,"invalid decision was accepted"
   out=req("http://127.0.0.1:8765/api/decision/E2E-001","POST",{"action":"APPROVE","author":"Piotr Florczyk","golden_value":"1763","justification":"Source B is corroborated by the cited edition."})
   assert out["ok"] and out["status"]=="RESOLVED"
   c=sqlite3.connect(db);row=c.execute("SELECT status,golden_value,decision_note FROM conflict_ledger WHERE conflict_id='E2E-001'").fetchone();d=c.execute("SELECT action,author,golden_value FROM decision_log WHERE conflict_id='E2E-001'").fetchone();c.close()
   assert row==("RESOLVED","1763","Source B is corroborated by the cited edition.")
   assert d==("APPROVE","Piotr Florczyk","1763")
   q=req("http://127.0.0.1:8765/api/queue");assert q==[],"resolved conflict remains in queue"
   print("MEGA E2E PASS: health -> queue -> validation -> decision -> ledger -> decision_log -> queue empty")
  finally:
   p.terminate();p.wait(timeout=5)
if __name__=="__main__":main()
