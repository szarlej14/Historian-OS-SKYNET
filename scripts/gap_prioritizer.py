#!/usr/bin/env python3
"""Rank GAP DETECTOR findings by research impact.

The prioritizer does not resolve or delete anything. It only orders work.
"""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"; INDEX=ROOT/"index"
WEIGHTS={"ORPHAN_FACT":10,"CONFLICT_DATE":10,"ORPHAN_RELATION":8,
         "MISSING_TPQ_TAQ":7,"LOW_CONFIDENCE_CLUSTER":6,"ORPHAN_SOURCE":5}

def load_records():
 out={}
 for p in DATA.glob("*.json"):
  try:o=json.loads(p.read_text(encoding="utf-8"))
  except Exception:continue
  if isinstance(o,dict) and str(o.get("id","")).startswith("HOS-"):out[o["id"]]=o
 return out

def main():
 rs=load_records(); gaps=[]
 for rid,o in rs.items():
  sources=o.get("sources") if isinstance(o.get("sources"),list) else []
  relations=o.get("relations") if isinstance(o.get("relations"),list) else []
  temporal=o.get("temporal") if isinstance(o.get("temporal"),dict) else {}
  if not sources:
   gaps.append((rid,"ORPHAN_FACT",10,["missing_source"]))
  if relations and not o.get("relation_timeframe"):
   gaps.append((rid,"ORPHAN_RELATION",8,["missing_relation_timeframe"]))
  if o.get("type") in ("wydarzenie","event") and not temporal.get("tpq") and not o.get("tpq"):
   gaps.append((rid,"MISSING_TPQ_TAQ",7,["missing_tpq"]))
  if o.get("date_conflict") is True:
   gaps.append((rid,"CONFLICT_DATE",10,["explicit_date_conflict"]))
 rows=[]
 degree=Counter()
 for o in rs.values():
  for x in o.get("relations",[]) if isinstance(o.get("relations"),list) else []: degree[x]+=1
 for rid,kind,base,signals in gaps:
  impact=degree[rid]
  score=base + min(impact,10)
  rows.append({"record_id":rid,"title":rs[rid].get("title",""),"gap_type":kind,
               "priority_score":score,"impact_degree":impact,"signals":signals,
               "status":"open"})
 rows.sort(key=lambda x:(-x["priority_score"],x["gap_type"],x["record_id"]))
 INDEX.mkdir(exist_ok=True); p=INDEX/"gap_priorities.json"
 p.write_text(json.dumps({"type":"gap_priorities","version":"1.0",
 "policy":"rank_only_no_auto_resolution","count":len(rows),
 "type_counts":dict(Counter(x["gap_type"] for x in rows)),
 "items":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(f"OK: {len(rows)} gaps prioritized")
if __name__=="__main__":main()
