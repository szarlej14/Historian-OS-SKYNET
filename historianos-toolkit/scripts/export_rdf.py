#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
out=root/'export'; out.mkdir(exist_ok=True)
(out/'historianos.jsonld').write_text('{\n  "@context": {"prov":"http://www.w3.org/ns/prov#"},\n  "@graph": []\n}\n',encoding='utf-8')
(out/'cidoc-crm.rdf').write_text('<!-- RDF export scaffold; canonical mapping follows CIDOC CRM + PROV-O. -->\n',encoding='utf-8')
print('EXPORT SCAFFOLD READY')
