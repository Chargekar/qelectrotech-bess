"""Build the relational model (SQLite) from schema + seeds + existing skill assets. Stdlib only.

python scripts/build_db.py [--output build/bess.sqlite]

Loads, in order: schema.sql, source register (references/sources.md + truth_seed sources),
truth layer (truth_seed.json), verified Draw.io stencil inventory, glossary (glossary_seed.json),
catalog symbols, note templates, raceway types. Then runs integrity checks and prints counts.
"""
import argparse, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / 'assets/db'


def j(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_sources(cx, truth):
    md = (ROOT / 'references/sources.md').read_text(encoding='utf-8')
    for row in re.finditer(r'^\|\s*([A-Z0-9][A-Z0-9-]+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$', md, re.M):
        sid, cell, use = row.groups()
        if sid in ('ID',):
            continue
        link = re.search(r'\[([^\]]+)\]\(([^)]+)\)', cell)
        title, url = (link.group(1), link.group(2)) if link else (cell, None)
        kind = 'drawing-corpus' if sid.startswith(('LAUSD', 'SDUSD', 'PUSD', 'MJUSD')) else \
               'tooling' if sid.startswith('QET') else \
               'owner-requirement' if sid == 'OWNER-REQUIREMENT' else 'reference'
        cx.execute('INSERT OR IGNORE INTO source(id,title,url,kind,accessed) VALUES (?,?,?,?,?)',
                   (sid, title, url, kind, '2026-11-06'))
    for s in truth['sources']:
        cx.execute('INSERT OR IGNORE INTO source(id,title,issuer,url,kind) VALUES (?,?,?,?,?)',
                   (s['id'], s['title'], s.get('issuer'), s.get('url'), s['kind']))


def load_truth(cx, t):
    for s in t['standards']:
        cx.execute('INSERT INTO standard VALUES (?,?,?,?)', (s['id'], s['body'], s['title'], s['kind']))
    for e in t['editions']:
        cx.execute('INSERT INTO edition(id,standard_id,label,year,model_basis_id,jurisdiction,effective_from,effective_to,source_id,verification) '
                   'VALUES (?,?,?,?,?,?,?,?,?,?)',
                   (e['id'], e['standard_id'], e['label'], e.get('year'), e.get('model_basis_id'), e.get('jurisdiction'),
                    e.get('effective_from'), e.get('effective_to'), e.get('source_id'), e.get('verification', 'needs-verification')))
    applies = []
    for c in t['clauses']:
        for ed in c['editions']:
            physics = ed == 'PHYSICS-0'
            ver = 'definition' if physics else 'needs-verification'
            cid = f"{ed}:{c['locator']}"
            cx.execute('INSERT INTO clause(id,edition_id,locator,title,topic,intent,applicability,verification) VALUES (?,?,?,?,?,?,?,?)',
                       (cid, ed, c['locator'], c['title'], c['topic'], c['intent'], c.get('applicability'), ver))
            const_ids = {}
            for k in c.get('constants', []):
                kid = f"K-{ed}-{c['locator']}-{k['key']}"
                const_ids[k['key']] = kid
                cx.execute('INSERT INTO constant VALUES (?,?,?,?,?,?,?)',
                           (kid, cid, k['symbol'], k['value'], k['unit'], k['meaning'], ver))
            table_ids = {}
            for tb in c.get('tables', []):
                tid = f"T-{ed}-{tb['key']}"
                table_ids[tb['key']] = tid
                cx.execute('INSERT INTO code_table VALUES (?,?,?,?,?)',
                           (tid, cid, tb['name'], json.dumps(tb['key_schema']), tb['value_unit']))
            for f in c.get('formulas', []):
                fid = f"F-{ed}-{c['locator']}-{f['key']}"
                cx.execute('INSERT INTO formula(id,clause_id,name,form,expression,output_symbol,output_unit,note,verification) VALUES (?,?,?,?,?,?,?,?,?)',
                           (fid, cid, f['name'], f['form'], f['expression'], f['output_symbol'], f['output_unit'], f.get('note'), ver))
                for term in f['terms']:
                    cx.execute('INSERT INTO formula_term VALUES (?,?,?,?,?,?,?,?)',
                               (fid, term['symbol'], term['meaning'], term['unit'], term['role'],
                                const_ids.get(term.get('constant')), table_ids.get(term.get('table')), term.get('param')))
            for cls in c.get('applies_to', []):
                applies.append((cid, cls))
    for r in t['table_rows']:
        tid = f"T-{r['edition']}-{r['table']}"
        if 'values' in r:
            for v in r['values']:
                cx.execute('INSERT INTO code_table_row(table_id,row_key,value_name,value) VALUES (?,?,?,?)',
                           (tid, json.dumps({'rating_a': v}, sort_keys=True), 'rating', v))
        for key, val in r.get('rows', []):
            cx.execute('INSERT INTO code_table_row(table_id,row_key,value_name,value) VALUES (?,?,?,?)',
                       (tid, json.dumps(key, sort_keys=True), 'value', val))
    for v in t.get('verifications', []):  # promote rows checked against the adopted text
        for table in ('clause', 'formula'):
            cx.execute(f"UPDATE {table} SET verification='verified', verified_by=?, verified_on=? WHERE id=?", (v['by'], v['on'], v['row']))
        cx.execute("UPDATE constant SET verification='verified' WHERE id=?", (v['row'],))
        cx.execute("UPDATE code_table_row SET verification='verified' WHERE table_id=?", (v['row'],))
    for ln in t['lineage']:
        cx.execute('INSERT INTO clause_lineage VALUES (?,?,?,?)', (ln['from'], ln['to'], ln['relation'], ln.get('note')))
    return applies


def load_vocab(cx, g, applies):
    inv = j(ROOT / 'assets/drawio/stencil_inventory.json')
    for s in inv['shapes']:
        cx.execute('INSERT INTO drawio_shape VALUES (?,?,?,?,?)',
                   (s['shape'], '; '.join(s['titles']), s['w'], s['h'], inv['commit']))
    for fid, label in g['families']:
        cx.execute('INSERT INTO equipment_family VALUES (?,?)', (fid, label))
    catalog = {s['id']: s for s in j(ROOT / 'assets/catalog.json')['symbols']}
    base = g['drawio_base']
    for s in g['symbols']:
        cx.execute('INSERT INTO symbol VALUES (?,?,?,?,?,?,?,?)',
                   (s['id'], s.get('qet'), s['kind'], s.get('shape'), s['style'].replace('{B}', base), s['w'], s['h'], s.get('note')))
    missing = set(catalog) - {s['id'] for s in g['symbols']}
    if missing:
        raise SystemExit(f'catalog symbols without a Draw.io mapping: {sorted(missing)}')
    for pid, label, unit, kind in g['params']:
        cx.execute('INSERT INTO rating_param VALUES (?,?,?,?)', (pid, label, unit, kind))
    for c in g['classes']:
        cx.execute('INSERT INTO equipment_class VALUES (?,?,?,?,?,?,?,?,?,?)',
                   (c['id'], c['term'], c.get('abbrev'), c['family'], None, c['definition'], c.get('bess_role'),
                    c.get('symbol'), json.dumps([{'id': p, 'domain': d} for p, d in c['ports']]), c.get('pitfall')))
    for c in g['classes']:  # parents after all rows exist
        if c.get('parent'):
            cx.execute('UPDATE equipment_class SET parent_id=? WHERE id=?', (c['parent'], c['id']))
        for a in c.get('aliases', []):
            cx.execute('INSERT OR IGNORE INTO class_alias(alias,class_id) VALUES (?,?)', (a, c['id']))
        for p in c.get('params', []):
            cx.execute('INSERT INTO class_param(class_id,param_id) VALUES (?,?)', (c['id'], p))
    cx.execute("""UPDATE class_alias SET ambiguous=1 WHERE alias IN
                  (SELECT alias FROM class_alias GROUP BY alias HAVING count(*)>1)""")
    for cid, cls in applies:
        cx.execute('INSERT INTO clause_applies_to VALUES (?,?)', (cid, cls))
    for lk in g['location_kinds']:
        cx.execute('INSERT INTO location_kind VALUES (?,?,?)', lk)
    for lc in g['layout_conventions']:
        cx.execute('INSERT INTO layout_convention VALUES (?,?,?,?)', lc)
    notes = j(ROOT / 'assets/notes/compliance-notes.json')['templates'] + g['extra_notes']
    for n in notes:
        cx.execute('INSERT INTO note_template VALUES (?,?,?,?,?)',
                   (n['id'], n['topic'], n.get('applicability_scope', n.get('scope', 'all')), n['template'], n.get('starting_source_id')))
    for nid, topics in g['note_topics'].items():
        for tp in topics:
            cx.execute('INSERT INTO note_clause VALUES (?,?)', (nid, tp))
    for r in j(ROOT / 'assets/raceways/types.json')['types']:
        cx.execute('INSERT INTO raceway_type VALUES (?,?)', (r['id'], r['name']))


def checks(cx):
    errors = []
    q = lambda sql: cx.execute(sql).fetchall()
    for (s,) in q("SELECT drawio_shape FROM symbol WHERE drawio_shape IS NOT NULL AND drawio_shape NOT IN (SELECT shape FROM drawio_shape)"):
        errors.append(f'unverified Draw.io shape: {s}')
    for (fid, sym) in q("""SELECT t.formula_id, t.symbol FROM formula_term t JOIN formula f ON f.id=t.formula_id
                           WHERE instr(f.expression, t.symbol)=0"""):
        errors.append(f'term not used in expression: {fid}.{sym}')
    for (pid,) in q("SELECT DISTINCT param_id FROM formula_term WHERE param_id IS NOT NULL AND param_id NOT IN (SELECT id FROM rating_param)"):
        errors.append(f'formula references unknown rating param: {pid}')
    for row in q("PRAGMA foreign_key_check"):
        errors.append(f'foreign key violation: {row}')
    try:
        cx.execute("UPDATE constant SET value=value+1 WHERE rowid=1")
        errors.append('truth immutability trigger did not fire')
    except sqlite3.DatabaseError:
        pass
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default=str(ROOT / 'build/bess.sqlite'))
    a = ap.parse_args()
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    cx = sqlite3.connect(out)
    cx.execute('PRAGMA foreign_keys=ON')
    cx.executescript((DB_DIR / 'schema.sql').read_text(encoding='utf-8'))
    truth, gloss = j(DB_DIR / 'truth_seed.json'), j(DB_DIR / 'glossary_seed.json')
    cx.execute('PRAGMA defer_foreign_keys=ON')  # truth terms reference rating params loaded later
    with cx:
        load_sources(cx, truth)
        applies = load_truth(cx, truth)
        load_vocab(cx, gloss, applies)
    errors = checks(cx)
    counts = {t: cx.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in
              ['source', 'standard', 'edition', 'clause', 'formula', 'constant', 'code_table_row', 'equipment_class',
               'class_alias', 'symbol', 'drawio_shape', 'note_template', 'layout_convention']}
    unverified = cx.execute('SELECT count(*) FROM v_unverified_truth').fetchone()[0]
    cx.close()
    print(json.dumps({'db': str(out), 'counts': counts, 'truth_rows_needing_verification': unverified}, indent=1))
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
