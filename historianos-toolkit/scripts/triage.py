import argparse,sqlite3
p=argparse.ArgumentParser(); p.add_argument('db',nargs='?',default='historianos.sqlite3'); a=p.parse_args(); c=sqlite3.connect(a.db)
for cid,e,attr,A,B in c.execute("SELECT conflict_id,entity_id,attribute,source_a_val,source_b_val FROM conflict_ledger WHERE status='OPEN'"):
 print(f'\n[{cid}] {e} :: {attr}\n A: {A}\n B: {B}'); x=input('[1] A [2] B [3] własna [4] Obsidian [q] pomiń: ').strip()
 if x in ('1','2','3'):
  v=A if x=='1' else B if x=='2' else input('Golden value: ').strip(); note=input('Uzasadnienie: ').strip()
  if v: c.execute("UPDATE conflict_ledger SET status='RESOLVED',golden_value=?,decision_note=?,resolved_at=CURRENT_TIMESTAMP WHERE conflict_id=? AND status='OPEN'",(v,note,cid)); c.commit()
 elif x=='q': break
