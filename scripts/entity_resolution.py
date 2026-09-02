#!/usr/bin/env python3
"""Conservative entity-resolution candidate detector.

It proposes pairs; it never merges records automatically.
"""
import json, re
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"; INDEX=ROOT/"index"

def load():
    out={}
    for p in DATA.glob("*.json"):
        try:o=json.loads(p.read_text(encoding="utf-8"))
        except Exception:continue
        if isinstance(o,dict) and isinstance(o.get("id"),str) and o["id"].startswith("HOS-"):
            out[o["id"]]=o
    return out

def norm(s):
    s=str(s or "").lower()
    return re.sub(r"[^a-z0-9ąćęłńóśźż ]+"," ",s).strip()

def similarity(a,b):
    ta=set(norm(a).split()); tb=set(norm(b).split())
    if not ta or not tb:return 0.0
    return len(ta&tb)/len(ta|tb)

def typ(o):
    c=norm(o.get("category"))
    if any(x in c for x in ("person","osoba","biography","biografia")): return "person"
    if any(x in c for x in ("place","miejsce","location","lokacja")): return "place"
    if any(x in c for x in ("institution","instytucja","organization","organizacja","club","klub")): return "institution"
    if any(x in c for x in ("event","wydarzenie","grand prix","championship")): return "event"
    return "unknown"

def main():
    rs=load(); rows=[]
    for (a,oa),(b,ob) in combinations(sorted(rs.items()),2):
        ta,tb=typ(oa),typ(ob)
        if ta!=tb: continue
        score=similarity(oa.get("title"),ob.get("title"))
        if score < .45: continue
        rows.append({"id":f"ERC-{a[4:]}-{b[4:]}","entity_type":ta,
                     "canonical_id":a,"candidate_id":b,"score":round(score,3),
                     "signals":["title_token_overlap"],"status":"needs_review",
                     "review_note":None})
    INDEX.mkdir(exist_ok=True)
    out={"type":"entity_resolution_candidates","version":"1.0",
         "candidate_count":len(rows),"policy":"never_auto_merge","candidates":rows}
    p=INDEX/"entity_candidates.json"
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"OK: {len(rows)} entity candidates written to {p.relative_to(ROOT)}")

if __name__=="__main__": main()
