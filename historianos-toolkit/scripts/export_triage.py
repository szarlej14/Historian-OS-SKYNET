import argparse,sqlite3
from pathlib import Path
def export_one(c,cid,root=Path('Triage')):
 r=c.execute("SELECT conflict_id,entity_id,attribute,source_a_val,source_b_val FROM conflict_ledger WHERE conflict_id=? AND status='OPEN'",(cid,)).fetchone()
 if not r:return
 root.mkdir(parents=True,exist_ok=True); (root/'Archiwum').mkdir(exist_ok=True); (root/(cid+'.md')).write_text('---\nconflict_id: "'+r[0]+'"\nentity: "'+r[1]+'"\nissue: "'+r[2]+'"\nstatus: open\ngolden_value: ""\nsource_A: "'+r[3]+'"\nsource_B: "'+r[4]+'"\ndecision_note: ""\n---\n\n# Researcher Decision\nWpisz golden_value, decision_note i status: resolved.\n',encoding='utf-8'); c.execute("UPDATE conflict_ledger SET status='EXPORTED' WHERE conflict_id=? AND status='OPEN'",(cid,)); c.commit()
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('db',nargs='?',default='historianos.sqlite3'); p.add_argument('triage',nargs='?',default='Triage'); a=p.parse_args(); c=sqlite3.connect(a.db); [export_one(c,x,Path(a.triage)) for x, in c.execute("SELECT conflict_id FROM conflict_ledger WHERE status='OPEN'")]
