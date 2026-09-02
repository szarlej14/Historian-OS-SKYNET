#!/usr/bin/env python3
from pathlib import Path
import sys,collections
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
c=collections.Counter()
for p in root.rglob('*.md'):
    t=p.read_text(encoding='utf-8',errors='ignore')
    for k in ('fakt','wydarzenie','miejsce','relacja','seria','zrodlo'): c[k]+=t.count('type: '+k)
for k,v in c.items(): print(f'{k}: {v}')
