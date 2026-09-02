#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
for p in root.rglob('*.md'):
 t=p.read_text(encoding='utf-8',errors='ignore')
 if 'type: miejsce' in t and ('wspolrzedne:' in t or 'coordinates:' in t): print(p)
