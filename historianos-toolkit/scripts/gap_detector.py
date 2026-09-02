#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
kind=sys.argv[3] if len(sys.argv)>3 and sys.argv[2]=='--type' else None
for p in root.rglob('*.md'):
    t=p.read_text(encoding='utf-8',errors='ignore')
    if ('type: fakt' in t and not any(k in t for k in ('zrodlo:','źródło:','zrodla:','sources:'))) and (kind in (None,'ORPHAN_FACT')): print('ORPHAN_FACT',p)
