#!/usr/bin/env python3
"""Build the human-decision Command Center from derived SKYNET indexes."""
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; INDEX=ROOT/"index"
def read(name,default):
 p=INDEX/name
 if not p.exists(): return default
 try:return json.loads(p.read_text(encoding="utf-8"))
 except Exception:return default
def main():
 gaps=read("gap_priorities.json",{"items":[]}); rel=read("relations.json",{"nodes":[]})
 ev=read("evidence.json",{"evidence":[]}); ent=read("entity_candidates.json",{"candidates":[]})
 temporal=read("temporal.json",{"records":[]}); series=read("series.json",{"series":[]})
 items=gaps.get("items",[])
 payload={"type":"command_center","version":"2.0","generated_at":datetime.now(timezone.utc).isoformat(),
 "principle":"AI recommends; human decides",
 "health":{"relation_nodes":len(rel.get("nodes",[])),"evidence_records":len(ev.get("evidence",[])),
 "entity_candidates":len(ent.get("candidates",[])),"temporal_records":len(temporal.get("records",[])),
 "series":len(series.get("series",[])),"open_gaps":len(items)},
 "priority_queue":items[:25],"entity_review_queue":ent.get("candidates",[])[:25],
 "decision_log_schema":{"decision":"","author":"","justification":"","date":""},"decisions":[]}
 INDEX.mkdir(exist_ok=True)
 (INDEX/"command_center_v2.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("OK: command center v2 generated")
if __name__=="__main__":main()
