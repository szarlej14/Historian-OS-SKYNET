#!/usr/bin/env python3
"""HistorianOS integration smoke test. Uses only stdlib and a temporary vault."""
import json,sqlite3,tempfile,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/"app"
def run():
 with tempfile.TemporaryDirectory() as td:
  v=Path(td)/"vault";v.mkdir();(v/"40 Fakty").mkdir()
  (v/"40 Fakty"/"supported.md").write_text('---\ntype: fakt\nnazwa: Test fakt\nzrodlo: "[[Source A]]"\n---\n',encoding="utf8")
  (v/"40 Fakty"/"orphan.md").write_text('---\ntype: fakt\nnazwa: Orphan fact\n---\n',encoding="utf8")
  (v/"person.md").write_text('---\ntype: osoba\nnazwa: Test Person\nzrodlo: "[[Source A]]"\n---\n',encoding="utf8")
  cmd=[sys.executable,str(APP/"selection_engine.py"),str(v)]
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
  report=v/"selection_report.json"
  assert p.returncode==0,("selection_engine failed",p.stdout,p.stderr)
  assert report.exists(),"selection_report.json missing"
  data=json.loads(report.read_text(encoding="utf8")); assert "stats" in data and "gaps" in data
  gaps=json.dumps(data["gaps"]); assert "ORPHAN_FACT" in gaps,"orphan fact was not detected"
  print("PASS selection pipeline:",data["stats"])
if __name__=="__main__": run()
