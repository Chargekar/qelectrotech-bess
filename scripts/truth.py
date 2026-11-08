"""Query and evaluate the compliance-truth layer. Stdlib only.

python scripts/truth.py editions --date 2026-03-01 [--jurisdiction US-CA]
python scripts/truth.py clauses --topic interconnection [--edition NEC-2023]
python scripts/truth.py formulas [--topic ocpd]
python scripts/truth.py eval <formula_id> SYMBOL=value ... [--key building_type=School --key climate_zone=4]
python scripts/truth.py lineage <clause_id>
python scripts/truth.py sql "SELECT ..."

eval fills constants from the truth layer, looks up code-table terms when --key values are given,
and always prints the verification status of every truth row it used. It never writes to the DB.
"""
import argparse, ast, json, math, operator, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / 'build/bess.sqlite'
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
       ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos,
       ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge, ast.Eq: operator.eq}


def safe_eval(expr, env, funcs):
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
        if isinstance(n, ast.Name):
            if n.id not in env: raise KeyError(f'missing input: {n.id}')
            return env[n.id]
        if isinstance(n, ast.BinOp) and type(n.op) in OPS: return OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPS: return OPS[type(n.op)](ev(n.operand))
        if isinstance(n, ast.Compare) and len(n.ops) == 1 and type(n.ops[0]) in OPS:
            return OPS[type(n.ops[0])](ev(n.left), ev(n.comparators[0]))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in funcs and not n.keywords:
            return funcs[n.func.id](*[ev(a) for a in n.args])
        raise ValueError(f'expression element not allowed: {ast.dump(n)[:60]}')
    return ev(ast.parse(expr, mode='eval'))


def rows(cx, sql, args=()):
    cur = cx.execute(sql, args)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def cmd_eval(cx, fid, assigns, keys):
    f = rows(cx, 'SELECT f.*, c.edition_id, c.locator FROM formula f JOIN clause c ON c.id=f.clause_id WHERE f.id=?', (fid,))
    if not f: raise SystemExit(f'unknown formula {fid}; run: truth.py formulas')
    f = f[0]
    env, used = {}, [{'row': f['id'], 'verification': f['verification']}]
    for a in assigns:
        k, v = a.split('=', 1); env[k] = float(v)
    key = {k: v for k, v in (x.split('=', 1) for x in keys)}
    for t in rows(cx, 'SELECT * FROM formula_term WHERE formula_id=?', (fid,)):
        if t['role'] == 'constant':
            c = rows(cx, 'SELECT * FROM constant WHERE id=?', (t['constant_id'],))[0]
            env[t['symbol']] = c['value']; used.append({'row': c['id'], 'value': c['value'], 'verification': c['verification']})
        elif t['role'] == 'table' and t['symbol'] not in env:
            if not key: raise SystemExit(f"{t['symbol']} comes from {t['table_id']}: pass --key values or {t['symbol']}=<value> from the adopted table")
            r = rows(cx, 'SELECT * FROM code_table_row WHERE table_id=? AND row_key=?', (t['table_id'], json.dumps(key, sort_keys=True)))
            if not r: raise SystemExit(f"no transcribed row in {t['table_id']} for {key}; transcribe it from the adopted text first")
            env[t['symbol']] = r[0]['value']; used.append({'row': t['table_id'], 'key': key, 'verification': r[0]['verification']})
    std_table = f"T-{f['edition_id']}-T2406"
    model = rows(cx, 'SELECT model_basis_id FROM edition WHERE id=?', (f['edition_id'],))
    def next_std(x):
        vals = [r['value'] for r in rows(cx, 'SELECT value FROM code_table_row WHERE table_id IN (?,?) ORDER BY value',
                                         (std_table, f"T-{(model[0]['model_basis_id'] if model else '')}-T2406"))]
        if not vals: raise SystemExit(f'no 240.6(A) table for {f["edition_id"]}')
        return next(v for v in vals if v >= x - 1e-9)
    funcs = {'sqrt': math.sqrt, 'max': max, 'min': min, 'next_std': next_std}
    result = safe_eval(f['expression'], env, funcs)
    out = {'formula': f['id'], 'clause': f"{f['edition_id']} {f['locator']}", 'expression': f"{f['output_symbol']} = {f['expression']}",
           'inputs': {k: v for k, v in env.items()}, 'result': result, 'unit': f['output_unit'], 'truth_rows_used': used,
           'status': 'VERIFIED-TRUTH' if all(u['verification'] in ('verified', 'definition') for u in used)
                     else 'PRELIMINARY: one or more truth rows need verification against the adopted text'}
    print(json.dumps(out, indent=1, default=str))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=str(DEFAULT_DB))
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('editions'); e.add_argument('--date'); e.add_argument('--jurisdiction')
    c = sub.add_parser('clauses'); c.add_argument('--topic'); c.add_argument('--edition')
    fo = sub.add_parser('formulas'); fo.add_argument('--topic')
    ev = sub.add_parser('eval'); ev.add_argument('formula_id'); ev.add_argument('assign', nargs='*'); ev.add_argument('--key', action='append', default=[])
    ln = sub.add_parser('lineage'); ln.add_argument('clause_id')
    sq = sub.add_parser('sql'); sq.add_argument('query')
    a = ap.parse_args()
    if not Path(a.db).exists(): raise SystemExit('database missing: run python scripts/build_db.py')
    cx = sqlite3.connect(f'file:{a.db}?mode=ro', uri=True)
    if a.cmd == 'editions':
        sql, args = 'SELECT id,label,jurisdiction,effective_from,effective_to,model_basis_id,verification FROM edition WHERE 1=1', []
        if a.date: sql += ' AND (effective_from IS NULL OR effective_from<=?) AND (effective_to IS NULL OR effective_to>=?)'; args += [a.date, a.date]
        if a.jurisdiction: sql += ' AND (jurisdiction=? OR jurisdiction IS NULL)'; args.append(a.jurisdiction)
        res = rows(cx, sql, args)
    elif a.cmd == 'clauses':
        sql, args = 'SELECT id,title,topic,intent,applicability,verification FROM clause WHERE 1=1', []
        if a.topic: sql += ' AND topic=?'; args.append(a.topic)
        if a.edition: sql += ' AND edition_id=?'; args.append(a.edition)
        res = rows(cx, sql, args)
    elif a.cmd == 'formulas':
        sql = 'SELECT v.* FROM v_formula_catalog v JOIN formula f ON f.id=v.formula_id JOIN clause c ON c.id=f.clause_id'
        res = rows(cx, sql + (' WHERE c.topic=?' if a.topic else ''), (a.topic,) if a.topic else ())
    elif a.cmd == 'eval':
        return cmd_eval(cx, a.formula_id, a.assign, a.key)
    elif a.cmd == 'lineage':
        res = rows(cx, 'SELECT * FROM clause_lineage WHERE from_clause_id=? OR to_clause_id=?', (a.clause_id, a.clause_id))
    else:
        if not a.query.lstrip().lower().startswith(('select', 'with')): raise SystemExit('read-only: SELECT/WITH only')
        res = rows(cx, a.query)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
