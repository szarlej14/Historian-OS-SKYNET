#!/usr/bin/env python3
"""Audit provenance and evidence coverage without changing canonical records."""
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
INDEX=ROOT/"index"

def load():
    out={}
    for p in DATA.glob("*.json"):
        try:o=json.loads(p.read_text(encoding="utf-8"))
        except Exception:continue
        if isinstance(o,dict) and isinstance(o.get("id"),str) and o["id"].startswith("HOS-"):
            out[o["id"]]=o
    return out

def main():
    rs=load()
    rows=[]
    status=Counter()
    for rid,o in rs.items():
        sources=o.get("sources") if isinstance(o.get("sources"),list) else []
        evid=o.get("evidence") if isinstance(o.get("evidence"),list) else []
        flags=[]
        if not sources: flags.append("no_source")
        if not evid: flags.append("no_evidence_record")
        for e in evid:
            if isinstance(e,dict):
                status[e.get("status","unassessed")]+=1
        rows.append({"id":rid,"title":o.get("title",""),"source_count":len(sources),
                     "evidence_count":len(evid),"flags":flags})
    INDEX.mkdir(exist_ok=True)
    report={"type":"evidence_audit","version":"1.0","record_count":len(rows),
            "coverage":{"with_source":sum(r["source_count"]>0 for r in rows),
                        "with_evidence":sum(r["evidence_count"]>0 for r in rows)},
            "evidence_status":dict(status),"records":sorted(rows,key=lambda x:x["id"])}
    p=INDEX/"evidence_audit.json"
    p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"OK: evidence audit written to {p.relative_to(ROOT)}")
    print(f"Records: {len(rows)} | with source: {report['coverage']['with_source']} | with evidence: {report['coverage']['with_evidence']}")
if __name__=="__main__": main()
