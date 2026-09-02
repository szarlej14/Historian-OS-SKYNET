#!/usr/bin/env python3
from pathlib import Path
import datetime,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
print('Release candidate:',datetime.datetime.now(datetime.timezone.utc).isoformat())
print('Decision Log review required before release.')
