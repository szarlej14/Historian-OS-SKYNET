#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
errors=[]
for p in root.rglob('*.md'):
    text=p.read_text(encoding='utf-8',errors='ignore')
    if 'type: fakt' in text and not any(k in text for k in ('zrodlo:','źródło:','zrodla:','sources:')):
        errors.append(f'ORPHAN_FACT: {p}')
print('\n'.join(errors) if errors else 'VALIDATION OK')
raise SystemExit(1 if errors else 0)
