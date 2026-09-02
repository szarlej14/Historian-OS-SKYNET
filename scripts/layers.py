#!/usr/bin/env python3
"""Historian OS SKYNET analytic layers.

RELATIONS -> MIEJSCA -> WYDARZENIA -> SOURCES -> TIMELINE -> GAP DETECTOR
-> SERIE -> COMMAND CENTER.

Zero dependencies. Reads data/*.json and writes derived indexes to index/.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INDEX = ROOT / "index"

def load_records():
    out = {}
    for p in sorted(DATA.glob("*.json")):
        try:
            o = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(o, dict) and isinstance(o.get("id"), str) and o["id"].startswith("HOS-"):
            o["_file"] = str(p.relative_to(ROOT))
            out[o["id"]] = o
    return out

def text(o):
    return json.dumps({k:v for k,v in o.items() if k != "_file"}, ensure_ascii=False).lower()

def tokens(value):
    if isinstance(value, list):
        return [str(x) for x in value]
    return [str(value)] if value else []

def save(name, payload):
    INDEX.mkdir(parents=True, exist_ok=True)
    p = INDEX / name
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p

def relations(rs):
    ids = set(rs)
    edges = []
    incoming = Counter()
    for rid, o in rs.items():
        for target in tokens(o.get("relations")):
            if target in ids:
                edges.append({"from": rid, "to": target})
                incoming[target] += 1
    degree = {rid: 0 for rid in rs}
    for e in edges:
        degree[e["from"]] += 1
        degree[e["to"]] += 1
    return save("relations.json", {
        "type":"relations_index", "version":"1.0",
        "record_count":len(rs), "edge_count":len(edges),
        "edges":edges,
        "nodes":[{"id":rid,"title":rs[rid].get("title",""),
                  "out":sum(e["from"]==rid for e in edges),
                  "in":sum(e["to"]==rid for e in edges),
                  "degree":degree[rid]} for rid in sorted(rs)]
    })

def classify_place(o):
    fields = " ".join(tokens(o.get("place")) + tokens(o.get("location")) + tokens(o.get("venue")) + tokens(o.get("city")) + tokens(o.get("country")))
    if fields:
        return fields.strip()
    # Conservative fallback: only infer a place from explicit place-like tags.
    for tag in tokens(o.get("tags")):
        if any(k in tag.lower() for k in ("place:","location:","city:","circuit:","venue:")):
            return tag.split(":",1)[-1].strip()
    return None

def places(rs):
    by_place = defaultdict(list)
    for rid,o in rs.items():
        p = classify_place(o)
        if p:
            by_place[p].append(rid)
    return save("places.json", {
        "type":"places_index","version":"1.0",
        "places":[{"name":p,"record_ids":sorted(ids),"count":len(ids)}
                  for p,ids in sorted(by_place.items(), key=lambda x:x[0].lower())]
    })

def parse_year(value):
    if not value: return None
    m = re.search(r"(?<!\d)(1[0-9]{3}|20[0-9]{2})(?!\d)", str(value))
    return int(m.group(1)) if m else None

def events(rs):
    items = []
    for rid,o in rs.items():
        cat = str(o.get("category","")).lower()
        title = str(o.get("title","")).lower()
        explicit = any(k in o for k in ("event_date","event_type","start_date","end_date"))
        eventish = explicit or "event" in cat or "wyda" in cat or "grand prix" in title or "championship" in title
        if eventish:
            items.append({"id":rid,"title":o.get("title",""),"date":o.get("date"),
                           "year":parse_year(o.get("date")) or parse_year(o.get("title")),
                           "category":o.get("category",""),"relations":o.get("relations",[])})
    items.sort(key=lambda x: (x["year"] is None, x["year"] or 9999, x["id"]))
    return save("events.json", {"type":"events_index","version":"1.0","count":len(items),"events":items})

def sources(rs):
    items = []
    domains = Counter()
    for rid,o in rs.items():
        srcs = o.get("sources", [])
        if not isinstance(srcs,list): srcs=[]
        for s in srcs:
            s = str(s)
            m = re.search(r"(?:https?://)?(?:www\.)?([^/\s]+)", s)
            domain = m.group(1).lower() if m else "non-url"
            domains[domain] += 1
            items.append({"record_id":rid,"source":s,"domain":domain})
    return save("sources.json", {"type":"sources_index","version":"1.0",
        "source_count":len(items),"domains":dict(domains),
        "sources":items})

def timeline(rs):
    rows=[]
    for rid,o in rs.items():
        y=parse_year(o.get("date")) or parse_year(o.get("title"))
        if y is not None:
            rows.append({"year":y,"id":rid,"title":o.get("title",""),
                         "date":o.get("date"),"category":o.get("category","")})
    rows.sort(key=lambda x:(x["year"],x["id"]))
    years=Counter(r["year"] for r in rows)
    return save("timeline.json", {"type":"timeline_index","version":"1.0",
        "min_year":min(years) if years else None,"max_year":max(years) if years else None,
        "years":[{"year":y,"count":years[y]} for y in sorted(years)],
        "records":rows})

def gap_detector(rs):
    years=sorted({parse_year(o.get("date")) or parse_year(o.get("title")) for o in rs.values()})
    years=[y for y in years if y]
    gaps=[]
    for a,b in zip(years,years[1:]):
        if b-a >= 3:
            gaps.append({"from_year":a,"to_year":b,"missing_years":b-a-1})
    weak=[]
    for rid,o in rs.items():
        issues=[]
        if not o.get("summary"): issues.append("missing_summary")
        if not isinstance(o.get("sources"),list) or not o.get("sources"): issues.append("missing_sources")
        if not isinstance(o.get("relations"),list) or not o.get("relations"): issues.append("missing_relations")
        if issues: weak.append({"id":rid,"title":o.get("title",""),"issues":issues})
    return save("gaps.json", {"type":"gap_detector","version":"1.0",
        "chronological_gaps":gaps,"weak_records":weak,
        "summary":{"chronological_gap_count":len(gaps),"weak_record_count":len(weak)}})

def series(rs):
    groups=defaultdict(list)
    for rid,o in rs.items():
        corpus=o.get("corpus","unknown") or "unknown"
        category=o.get("category","unknown") or "unknown"
        groups[(corpus,category)].append(rid)
    rows=[]
    for (corpus,category),ids in sorted(groups.items()):
        years=[parse_year(rs[r].get("date")) or parse_year(rs[r].get("title")) for r in ids]
        years=[y for y in years if y]
        rows.append({"series_id":re.sub(r"[^A-Z0-9]+","-",f"{corpus}-{category}".upper()).strip("-"),
                     "corpus":corpus,"category":category,"count":len(ids),
                     "min_year":min(years) if years else None,"max_year":max(years) if years else None,
                     "record_ids":sorted(ids)})
    return save("series.json", {"type":"series_index","version":"1.0","count":len(rows),"series":rows})

def command_center(rs):
    outputs={}
    for fn,name in ((relations,"relations"),(places,"places"),(events,"events"),
                    (sources,"sources"),(timeline,"timeline"),(gap_detector,"gaps"),(series,"series")):
        p=fn(rs); outputs[name]=str(p.relative_to(ROOT))
    return save("command_center.json", {
        "type":"command_center","version":"1.0","generated":"derived",
        "records":len(rs),"layers":outputs,
        "health":{
            "records":len(rs),
            "with_sources":sum(bool(o.get("sources")) for o in rs.values()),
            "with_relations":sum(bool(o.get("relations")) for o in rs.values()),
            "dated":sum(bool(parse_year(o.get("date")) or parse_year(o.get("title"))) for o in rs.values()),
        }
    })

def main():
    rs=load_records()
    cmd=sys.argv[1].lower() if len(sys.argv)>1 else "command-center"
    funcs={"relations":relations,"places":places,"events":events,"sources":sources,
           "timeline":timeline,"gaps":gap_detector,"gap-detector":gap_detector,
           "series":series,"command-center":command_center}
    if cmd == "all":
        command_center(rs)
        print(f"OK: all layers built for {len(rs)} records")
        return 0
    if cmd not in funcs:
        print("Użycie: layers.py [relations|places|events|sources|timeline|gaps|series|command-center|all]")
        return 1
    p=funcs[cmd](rs)
    print(f"OK: {p.relative_to(ROOT)}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
