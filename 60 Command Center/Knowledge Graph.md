# HISTORIAN OS · KNOWLEDGE GRAPH

> [!abstract] GRAPH CONTROL
> Graf pokazuje **relacje między rekordami**, nie rozstrzyga ich prawdziwości.

## RELATIONS

```dataviewjs
const pages=dv.pages().where(p=>p.type);
const rows=[];
for(const p of pages){
  const fields=["from","to","miejsce","zrodlo","źródło","poprzedza","nastepuje_po","uczestnicy"];
  for(const f of fields){
    const v=p[f];
    if(Array.isArray(v)) for(const x of v) rows.push([p.file.link,f,String(x)]);
    else if(v) rows.push([p.file.link,f,String(v)]);
  }
}
dv.table(["REKORD","RELACJA","CEL"],rows);
```

## TIMELINE

```dataview
TABLE data_narracyjna AS Data, tpq AS TPQ, taq AS TAQ, precyzja AS Precyzja, miejsce AS Miejsce
FROM "20 Wydarzenia"
WHERE type = "wydarzenie"
SORT tpq ASC
```

## PLACES

```dataview
TABLE file.link AS Miejsce, wspolrzedne AS Współrzędne
FROM "10 Miejsca"
WHERE type = "miejsce"
SORT file.name ASC
```

## SERIES

```dataview
TABLE file.link AS Seria, typ AS Typ, data AS Zakres, opis AS Opis
FROM "50 Serie"
WHERE type = "seria"
SORT data ASC
```

## LOCAL GRAPH

> Otwórz dowolną osobę, miejsce lub wydarzenie i użyj **Graph view → Local graph**, aby zobaczyć jego bezpośrednie powiązania.

### SEMANTIC LEGEND

- **Osoba ↔ Osoba/Instytucja** → relacja
- **Osoba → Wydarzenie** → uczestnictwo
- **Wydarzenie → Miejsce** → lokalizacja
- **Wydarzenie → Źródło** → provenance
- **Wydarzenie → Wydarzenie** → następstwo chronologiczne
- **Fakt → Źródło** → evidence
- **Seria → Wydarzenia** → interpretacja longue durée