#!/usr/bin/env python3
from pathlib import Path
import sys,re
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
rows=[]
for p in root.rglob('*.md'):
 t=p.read_text(encoding='utf-8',errors='ignore')
 if 'type: wydarzenie' in t:
  m=re.search(r'(?m)^tpq:\s*(.+)$',t); rows.append((m.group(1).strip() if m else '',str(p)))
for d,p in sorted(rows): print(d,p)
