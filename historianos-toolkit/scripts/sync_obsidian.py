import argparse,re,sqlite3,shutil
from pathlib import Path
def f(t,k):
 m=re.search(r'^'+re.escape(k)+r':\s*["\']?(.*?)["\']?\s*$',t,re.M); return m.group(1).strip() if m else ''
p=argparse.ArgumentParser(); p.add_argument('db',nargs='?',default='historianos.sqlite3'); p.add_argument('triage',nargs='?',default='Triage'); a=p.parse_args(); c=sqlite3.connect(a.db); root=Path(a.triage); arch=root/'Archiwum'; arch.mkdir(parents=True,exist_ok=True)
for x in root.glob('*.md'):
 t=x.read_text(encoding='utf-8'); cid=f(t,'conflict_id'); status=f(t,'status'); golden=f(t,'golden_value'); note=f(t,'decision_note')
 if cid and status.lower()=='resolved' and golden:
  u=c.execute("UPDATE conflict_ledger SET status='RESOLVED',golden_value=?,decision_note=?,resolved_at=CURRENT_TIMESTAMP WHERE conflict_id=? AND status='EXPORTED'",(golden,note or 'Resolved in Obsidian',cid)); c.commit()
  if u.rowcount: shutil.move(str(x),str(arch/x.name)); print('RESOLVED',cid)
