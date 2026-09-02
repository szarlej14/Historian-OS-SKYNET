#!/usr/bin/env python3
"""Build a normalized temporal index while preserving uncertainty."""
import json,re
from collections import Counter
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"; INDEX=ROOT/"index"
def load():
 out={}
 for p in DATA.glob("*.json"):
  try:o=json.loads(p.read_text(encoding="utf-8"))
  except Exception:continue
  if isinstance(o,dict) and str(o.get("id","")).startswith("HOS-"): out[o["id"]]=o
 return out
def year(v):
 m=re.search(r"(?<!\d)(1[0-9]{3}|20[0-9]{2})(?!\d)",str(v or ""))
 return int(m.group(1)) if m else None
def iso(v):
 try:return date.fromisoformat(str(v).strip()).isoformat() if v else None
 except ValueError:return None
def state(rid,o):
 t=o.get("temporal") if isinstance(o.get("temporal"),dict) else {}
 raw=t.get("narrative_date") or o.get("data_narracyjna") or o.get("date")
 y=year(raw); tpq=iso(t.get("tpq") or o.get("tpq")); taq=iso(t.get("taq") or o.get("taq"))
 precision=t.get("precision") or o.get("precyzja") or ("day" if iso(raw) else ("year" if y else "unknown"))
 if y and not tpq: tpq=f"{y:04d}-01-01"
 if y and not taq: taq=f"{y:04d}-12-31"
 return {"id":rid,"narrative_date":str(raw) if raw else None,"year":y,"tpq":tpq,"taq":taq,
         "precision":precision,"temporal_relations":t.get("temporal_relations",[]),
         "confidence":t.get("confidence") or o.get("ocena"),
         "order":"invalid" if tpq and taq and tpq>taq else "valid"}
def main():
 rows=sorted([state(r,o) for r,o in load().items()],key=lambda x:(x["year"] is None,x["year"] or 9999,x["id"]))
 INDEX.mkdir(exist_ok=True); p=INDEX/"temporal.json"
 p.write_text(json.dumps({"type":"temporal_index","version":"1.0","count":len(rows),
 "precision_counts":dict(Counter(x["precision"] for x in rows)),
 "invalid_ranges":[x["id"] for x in rows if x["order"]=="invalid"],"records":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(f"OK: temporal index written to {p.relative_to(ROOT)}")
if __name__=="__main__":main()
