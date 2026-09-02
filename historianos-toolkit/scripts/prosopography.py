#!/usr/bin/env python3
from pathlib import Path
import sys,re
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
for p in root.rglob('*.md'):
 t=p.read_text(encoding='utf-8',errors='ignore')
 if 'type: relacja' in t:
  a=re.search(r'(?m)^from:\s*["\']?(.+?)["\']?$',t); b=re.search(r'(?m)^to:\s*["\']?(.+?)["\']?$',t)
  if a and b: print(a.group(1),' -> ',b.group(1))
