#!/usr/bin/env python3
"""One-way SKYNET to Obsidian Markdown exporter."""
import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"
FOLDERS={"relacja":"00 Relacje","miejsce":"10 Miejsca","wydarzenie":"20 Wydarzenia","zrodlo":"30 Zrodla","źródło":"30 Zrodla","fakt":"40 Fakty","fact":"40 Fakty","seria":"50 Serie"}
def load_records():
    out=[]
    for p in DATA.glob("*.json"):
        try: o=json.loads(p.read_text(encoding="utf-8"))
        except Exception: continue
        if isinstance(o,dict) and str(o.get("id","")).startswith("HOS-"): out.append(o)
    return out
def safe(s): return re.sub(r'[\\/:*?"<>|#^\\[\\]]+',"-",str(s or "bez-nazwy")).strip()[:180] or "bez-nazwy"
def link(v):
    if isinstance(v,list): return ", ".join(link(x) for x in v)
    s=str(v or "")
    return s if s.startswith("[[") else ("[["+safe(s)+"]]" if s else "")
def markdown(o):
    typ=str(o.get("type","")).lower(); title=o.get("title") or o.get("nazwa") or o.get("id")
    lines=["---","id: "+str(o.get("id")),"type: "+typ,"skynet_source: true","---","","# "+str(title),""]
    keys={"miejsce","zrodlo","źródło","from","to","uczestnicy","poprzedza","nastepuje_po"}
    for k,v in o.items():
        if k in {"id","type","title","nazwa","content","description","body"}: continue
        if isinstance(v,(str,int,float,bool)): lines.append("**"+k+":** "+(link(v) if k in keys else str(v)))
        elif isinstance(v,list): lines.append("**"+k+":** "+", ".join(link(x) if isinstance(x,str) else str(x) for x in v))
        elif isinstance(v,dict): lines.append("**"+k+":** `"+json.dumps(v,ensure_ascii=False)+"`")
    return "\n".join(lines)+"\n"
def main():
    if len(sys.argv)!=2: raise SystemExit("Usage: python3 scripts/obsidian_bridge.py /path/to/vault")
    vault=Path(sys.argv[1]).expanduser().resolve()
    for folder in set(FOLDERS.values()): (vault/folder).mkdir(parents=True,exist_ok=True)
    count=0
    for o in load_records():
        folder=FOLDERS.get(str(o.get("type","")).lower())
        if not folder: continue
        title=o.get("title") or o.get("nazwa") or o.get("id")
        (vault/folder/safe(title)).with_suffix(".md").write_text(markdown(o),encoding="utf-8"); count+=1
    dash=vault/"60 Command Center"/"Dashboard.md"; source=ROOT/"Dashboard.md"
    if source.exists(): dash.write_text(source.read_text(encoding="utf-8"),encoding="utf-8")
    print("OK: exported "+str(count)+" records to "+str(vault))
if __name__=="__main__": main()