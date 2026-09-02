#!/usr/bin/env python3
import argparse
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(prog='historianos')
    sub=ap.add_subparsers(dest='cmd',required=True)
    for name in ['stats','gap']:
        p=sub.add_parser(name); p.add_argument('vault'); p.add_argument('--all',action='store_true')
    d=sub.add_parser('dashboard'); ds=d.add_subparsers(dest='action',required=True); s=ds.add_parser('serve'); s.add_argument('--port',type=int,default=8080)
    a=ap.parse_args(); print(f'{a.cmd}: {getattr(a,"vault","")}')
if __name__=='__main__': main()
