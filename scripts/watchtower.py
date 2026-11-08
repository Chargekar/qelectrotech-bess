"""Watchtower for the compliance-truth seed (assets/db/truth_seed.json). Stdlib only.

It never edits truth_seed.json. It records, classifies and flags.

  python scripts/watchtower.py stats
  python scripts/watchtower.py diff  [--base REF|FILE]          # show classified changes vs git ref (default HEAD)
  python scripts/watchtower.py log   [--base REF|FILE] [--by NAME] [--note TEXT]   # append to TRUTH_CHANGELOG
  python scripts/watchtower.py check [--base REF|FILE]          # CI: fail on violations or missing changelog entry
  python scripts/watchtower.py observe --source ID --seen TEXT [--url URL] [--date YYYY-MM-DD] [--note TEXT]
  python scripts/watchtower.py rotation [--n 5]                 # truth rows due for spot review
  python scripts/watchtower.py finding --row ID --result consistent|discrepancy|unable --evidence URL [--note TEXT]
  python scripts/watchtower.py report [--write]                 # weekly status report

Change classes
  addition    new row (always allowed: new edition, clause, formula, constant, table row, lineage, source)
  promotion   a verification record added (row checked against adopted text by a named reviewer)
  metadata    non-normative field changed (edition effective_to/source/verification, formula name/note,
              constant meaning, clause applies_to mapping, source register details)
  demotion    a verification record removed or altered
  violation   normative content edited or a truth row deleted. Fix: restore the row, then add a new
              edition/clause/formula row plus a clause_lineage entry.
"""
import argparse, datetime as dt, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / 'assets/db/truth_seed.json'
SEED_REL = 'assets/db/truth_seed.json'
CHANGELOG = ROOT / 'assets/db/TRUTH_CHANGELOG.md'
WT = ROOT / 'watchtower'
JSONL = WT / 'changelog.jsonl'
SOURCES = WT / 'sources.json'
STATE = WT / 'state.json'
QUEUE = WT / 'REVIEW_QUEUE.md'
LEDGER = WT / 'ledger.jsonl'
REPORTS = WT / 'reports'

NORMATIVE = {
    'standard': {'body', 'title', 'kind'},
    'edition': {'standard_id', 'label', 'year', 'model_basis_id', 'jurisdiction', 'effective_from'},
    'clause': {'title', 'topic', 'intent', 'applicability'},
    'constant': {'symbol', 'value', 'unit'},
    'formula': {'form', 'expression', 'output_symbol', 'output_unit', 'terms'},
    'table': {'key_schema', 'value_unit'},
    'table_row': {'value'},
    'lineage': {'relation'},
}


def today():
    return dt.date.today().isoformat()


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def load_text(base):
    """Return seed text for a git ref or a file path; None if absent at that ref."""
    if base is None:
        return SEED.read_text(encoding='utf-8')
    p = Path(base)
    if p.exists() and p.is_file():
        return p.read_text(encoding='utf-8')
    git = lambda *args: subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    if git('rev-parse', '--verify', '--quiet', base).returncode != 0:
        raise SystemExit(f'base {base!r} is neither a file nor a git ref this repo can read '
                         f'(git: {git("rev-parse", "--verify", base).stderr.strip()})')
    shown = git('show', f'{base}:{SEED_REL}')
    if shown.returncode == 0:
        return shown.stdout
    if 'does not exist' in shown.stderr or 'exists on disk, but not in' in shown.stderr:
        return None
    raise SystemExit(f'git could not read {SEED_REL} at {base}: {shown.stderr.strip()}')


def rows(doc):
    """Flatten the seed into {key: (kind, content)} with editions expanded."""
    out = {}
    for s in doc.get('sources', []):
        out[f"source:{s['id']}"] = ('source', s)
    for s in doc.get('standards', []):
        out[f"standard:{s['id']}"] = ('standard', s)
    for e in doc.get('editions', []):
        out[f"edition:{e['id']}"] = ('edition', e)
    for c in doc.get('clauses', []):
        for ed in c['editions']:
            cid = f"{ed}:{c['locator']}"
            out[f'clause:{cid}'] = ('clause', {k: c.get(k) for k in ('title', 'topic', 'intent', 'applicability', 'applies_to')})
            for k in c.get('constants', []):
                out[f"constant:{cid}:{k['key']}"] = ('constant', k)
            for t in c.get('tables', []):
                out[f"table:{cid}:{t['key']}"] = ('table', t)
            for f in c.get('formulas', []):
                out[f"formula:{cid}:{f['key']}"] = ('formula', f)
    for r in doc.get('table_rows', []):
        if 'values' in r:
            for v in r['values']:
                out[f"table_row:{r['edition']}:{r['table']}:rating_a={v}"] = ('table_row', {'value': v})
        for key, val in r.get('rows', []):
            k = ','.join(f'{a}={b}' for a, b in sorted(key.items()))
            out[f"table_row:{r['edition']}:{r['table']}:{k}"] = ('table_row', {'value': val})
    for ln in doc.get('lineage', []):
        out[f"lineage:{ln['from']}->{ln['to']}"] = ('lineage', ln)
    for v in doc.get('verifications', []):
        out[f"verification:{v['row']}"] = ('verification', v)
    out['policy'] = ('policy', {'policy': doc.get('policy', [])})
    return out


def stats(doc):
    r = rows(doc)
    count = lambda k: sum(1 for kind, _ in r.values() if kind == k)
    return {'standards': count('standard'), 'editions': count('edition'), 'clauses': count('clause'),
            'formulas': count('formula'), 'constants': count('constant'), 'code_tables': count('table'),
            'table_rows': count('table_row'), 'lineage': count('lineage'), 'verifications': count('verification'),
            'sources': count('source')}


def classify(old_doc, new_doc):
    old, new = rows(old_doc or {}), rows(new_doc)
    changes = []
    for key in sorted(set(old) | set(new)):
        if key not in old:
            kind = new[key][0]
            changes.append({'key': key, 'class': 'promotion' if kind == 'verification' else 'addition'})
        elif key not in new:
            kind = old[key][0]
            cls = 'demotion' if kind == 'verification' else 'metadata' if kind in ('source', 'policy') else 'violation'
            changes.append({'key': key, 'class': cls, 'detail': 'row deleted'})
        elif old[key][1] != new[key][1]:
            kind, a, b = old[key][0], old[key][1], new[key][1]
            fields = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
            if kind == 'verification':
                cls = 'demotion'
            elif kind in NORMATIVE and set(fields) & NORMATIVE[kind]:
                cls = 'violation'
            else:
                cls = 'metadata'
            changes.append({'key': key, 'class': cls, 'fields': fields,
                            'detail': '; '.join(f'{f}: {json.dumps(a.get(f))[:80]} -> {json.dumps(b.get(f))[:80]}' for f in fields)})
    return changes


def summarize(changes):
    s = {}
    for c in changes:
        s[c['class']] = s.get(c['class'], 0) + 1
    return s


def last_logged_sha():
    if not JSONL.exists():
        return None
    for line in reversed(JSONL.read_text(encoding='utf-8').splitlines()):
        e = json.loads(line)
        if e.get('type') == 'seed-change':
            return e['new_sha256']
    return None


def append_jsonl(path, entry):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def cmd_diff(a, write=False):
    old_text, new_text = load_text(a.base), load_text(None)
    old_doc = json.loads(old_text) if old_text else None
    new_doc = json.loads(new_text)
    changes = classify(old_doc, new_doc)
    entry = {'type': 'seed-change', 'date': today(), 'base': a.base or 'HEAD',
             'old_sha256': sha(old_text) if old_text else None, 'new_sha256': sha(new_text),
             'by': getattr(a, 'by', None), 'note': getattr(a, 'note', None),
             'summary': summarize(changes), 'stats': stats(new_doc), 'changes': changes}
    if not write:
        print(json.dumps(entry, indent=1, ensure_ascii=False))
        return entry
    if not changes:
        print('no truth changes to log')
        return entry
    if last_logged_sha() == entry['new_sha256']:
        print('this seed version is already logged')
        return entry
    append_jsonl(JSONL, entry)
    st = entry['stats']
    lines = [f"## {entry['date']}  seed {entry['new_sha256'][:12]}" + (f"  by {entry['by']}" if entry['by'] else ''),
             '',
             f"Base `{entry['base']}` ({(entry['old_sha256'] or 'none')[:12]}). "
             f"Totals: {st['standards']} standards, {st['editions']} editions, {st['clauses']} clauses, "
             f"{st['formulas']} formulas, {st['constants']} constants, {st['code_tables']} code tables, "
             f"{st['table_rows']} table rows, {st['verifications']} verifications.",
             '', 'Summary: ' + ', '.join(f'{k} {v}' for k, v in sorted(entry['summary'].items())), '']
    if entry['note']:
        lines += [f"Note: {entry['note']}", '']
    for cls in ('violation', 'demotion', 'promotion', 'addition', 'metadata'):
        items = [c for c in changes if c['class'] == cls]
        if items:
            lines.append(f'**{cls}**')
            lines += [f"- `{c['key']}`" + (f" ({c['detail']})" if c.get('detail') else '') for c in items[:200]]
            if len(items) > 200:
                lines.append(f'- ... {len(items) - 200} more in watchtower/changelog.jsonl')
            lines.append('')
    header = '# Truth seed changelog\n\nAppend-only. Written by `scripts/watchtower.py log`; newest first.\n\n'
    body = CHANGELOG.read_text(encoding='utf-8')[len(header):] if CHANGELOG.exists() else ''
    CHANGELOG.write_text(header + '\n'.join(lines) + '\n' + body, encoding='utf-8')
    print(f"logged {sum(entry['summary'].values())} changes: {entry['summary']}")
    return entry


def cmd_check(a):
    old_text, new_text = load_text(a.base), load_text(None)
    changes = classify(json.loads(old_text) if old_text else None, json.loads(new_text))
    bad = [c for c in changes if c['class'] in ('violation', 'demotion')]
    errors = [f"{c['class']}: {c['key']} {c.get('detail', '')}" for c in bad]
    if changes and last_logged_sha() != sha(new_text):
        errors.append('truth_seed.json changed but has no changelog entry: run `python scripts/watchtower.py log --by <name>`')
    summary = summarize(changes)
    print(json.dumps({'summary': summary, 'errors': errors}, indent=1))
    sys.exit(1 if errors else 0)


def load_json(path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def affected_rows(doc, standard_ids):
    eds = {e['id'] for e in doc['editions'] if e['standard_id'] in standard_ids}
    return sorted(k for k, (kind, _) in rows(doc).items() if kind == 'clause' and k.split(':')[1] in eds)


def render_queue(state):
    items = state.get('queue', [])
    open_items = [i for i in items if i['status'] == 'open']
    lines = ['# Watchtower review queue', '',
             'Flags only. Nothing here changes truth_seed.json. Resolve an item by adding a new edition/clause/'
             'verification to the seed (then `watchtower.py log`), and set its status in watchtower/state.json to '
             '`resolved` or `dismissed` with a reason.', '',
             f'Open: {len(open_items)}  |  Total: {len(items)}  |  Updated: {today()}', '']
    for i in sorted(open_items, key=lambda x: x['raised'], reverse=True):
        lines += [f"## {i['id']}  {i['kind']}  ({i['raised']})", '', i['summary'], '']
        if i.get('evidence'):
            lines.append(f"Evidence: <{i['evidence']}>")
        if i.get('affects'):
            lines.append(f"Affects ({len(i['affects'])}): " + ', '.join(f'`{x}`' for x in i['affects'][:15]) +
                         (' ...' if len(i['affects']) > 15 else ''))
        lines.append('')
    QUEUE.write_text('\n'.join(lines), encoding='utf-8')


def raise_item(state, kind, summary, evidence=None, affects=None):
    n = len(state.setdefault('queue', [])) + 1
    item = {'id': f'WT-{n:04d}', 'kind': kind, 'raised': today(), 'status': 'open', 'summary': summary,
            'evidence': evidence, 'affects': affects or []}
    state['queue'].append(item)
    return item


def cmd_observe(a):
    sources = {s['id']: s for s in load_json(SOURCES, {'sources': []})['sources']}
    if a.source not in sources:
        raise SystemExit(f'unknown source {a.source}; see watchtower/sources.json')
    src = sources[a.source]
    state = load_json(STATE, {'sources': {}, 'queue': []})
    rec = state['sources'].setdefault(a.source, {})
    prev = rec.get('last_seen')
    rec.update(last_checked=a.date or today(), last_url=a.url or src.get('url'))
    entry = {'type': 'observation', 'date': a.date or today(), 'source': a.source, 'seen': a.seen,
             'previous': prev, 'url': a.url or src.get('url'), 'note': a.note}
    if prev is None:
        rec['last_seen'] = a.seen
        entry['result'] = 'baseline'
    elif prev != a.seen:
        rec['last_seen'] = a.seen
        doc = json.loads(SEED.read_text(encoding='utf-8'))
        item = raise_item(state, 'external-change',
                          f"{src['name']}: was \"{prev}\", now \"{a.seen}\". {a.note or ''}".strip(),
                          a.url or src.get('url'), affected_rows(doc, src.get('affects', [])))
        entry.update(result='changed', queue_item=item['id'])
    else:
        entry['result'] = 'unchanged'
    WT.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    append_jsonl(JSONL, entry)
    render_queue(state)
    print(json.dumps(entry, ensure_ascii=False))


def db_id(key):
    """Map a watchtower key to the build_db.py id used in `verifications` (clause, F-, K-, T- ids)."""
    kind, rest = key.split(':', 1)
    if kind == 'clause':
        return rest
    head, k = rest.rsplit(':', 1)
    ed, loc = head.split(':', 1)
    return {'formula': f'F-{ed}-{loc}-{k}', 'constant': f'K-{ed}-{loc}-{k}', 'table': f'T-{ed}-{k}'}.get(kind, rest)


def truth_row_ids(doc):
    return [k for k, (kind, _) in rows(doc).items() if kind in ('clause', 'formula', 'constant', 'table')]


def ledger():
    return [json.loads(l) for l in LEDGER.read_text(encoding='utf-8').splitlines()] if LEDGER.exists() else []


def cmd_rotation(a):
    doc = json.loads(SEED.read_text(encoding='utf-8'))
    verified = {v['row'] for v in doc.get('verifications', [])}
    last = {}
    for e in ledger():
        last[e['row']] = e['date']
    ids = [k for k in truth_row_ids(doc) if db_id(k) not in verified and 'PHYSICS-0' not in k]
    ids.sort(key=lambda k: (last.get(k, ''), k))
    print(json.dumps([{'row': k, 'db_id': db_id(k), 'last_reviewed': last.get(k)} for k in ids[:a.n]], indent=1))


def cmd_finding(a):
    doc = json.loads(SEED.read_text(encoding='utf-8'))
    if a.row not in rows(doc):
        raise SystemExit(f'unknown row {a.row}; use ids printed by `watchtower.py rotation`')
    entry = {'date': today(), 'row': a.row, 'result': a.result, 'evidence': a.evidence, 'note': a.note,
             'reviewer': a.reviewer}
    append_jsonl(LEDGER, entry)
    if a.result == 'discrepancy':
        state = load_json(STATE, {'sources': {}, 'queue': []})
        item = raise_item(state, 'discrepancy', f"{a.row}: {a.note or 'does not match the cited source'}", a.evidence, [a.row])
        STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        render_queue(state)
        entry['queue_item'] = item['id']
    print(json.dumps(entry, ensure_ascii=False))


def cmd_report(a):
    doc = json.loads(SEED.read_text(encoding='utf-8'))
    st = stats(doc)
    state = load_json(STATE, {'sources': {}, 'queue': []})
    srcs = load_json(SOURCES, {'sources': []})['sources']
    d = today()
    in_force = [e for e in doc['editions'] if (e.get('effective_from') or '0') <= d and (e.get('effective_to') or '9') >= d]
    lapsed_open = [e['id'] for e in doc['editions'] if e.get('effective_to') and e['effective_to'] < d]
    verified = {v['row'] for v in doc.get('verifications', [])}
    rows_all = truth_row_ids(doc)
    unverified = [k for k in rows_all if db_id(k) not in verified and 'PHYSICS-0' not in k]
    stale = [s['id'] for s in srcs if not state['sources'].get(s['id'], {}).get('last_checked') or
             (dt.date.fromisoformat(d) - dt.date.fromisoformat(state['sources'][s['id']]['last_checked'])).days > s.get('max_age_days', 14)]
    week = [e for e in ledger() if (dt.date.fromisoformat(d) - dt.date.fromisoformat(e['date'])).days <= 7]
    open_q = [i for i in state.get('queue', []) if i['status'] == 'open']
    lines = [f'# Watchtower report {d}', '',
             f"Seed {sha(SEED.read_text(encoding='utf-8'))[:12]}: {st['standards']} standards, {st['editions']} editions, "
             f"{st['clauses']} clauses, {st['formulas']} formulas, {st['constants']} constants, {st['code_tables']} code tables.", '',
             f'- Unverified truth rows: {len(unverified)} of {len(rows_all)} (physics excluded)',
             f'- Open review items: {len(open_q)}',
             f'- Rows spot-reviewed in the last 7 days: {len(week)} '
             f"({sum(1 for e in week if e['result'] == 'discrepancy')} discrepancies)",
             f'- Sources not checked within their window: {", ".join(stale) or "none"}',
             f'- Editions in force today: {", ".join(e["id"] for e in in_force if e.get("jurisdiction")) or "none"}',
             f'- Editions past effective_to (keep for old permits, do not delete): {", ".join(lapsed_open) or "none"}', '']
    if open_q:
        lines += ['## Open items', ''] + [f"- {i['id']} ({i['kind']}): {i['summary'][:160]}" for i in open_q[:20]] + ['']
    text = '\n'.join(lines)
    if a.write:
        REPORTS.mkdir(parents=True, exist_ok=True)
        (REPORTS / f'{d}.md').write_text(text, encoding='utf-8')
    print(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('stats')
    for name in ('diff', 'log', 'check'):
        p = sub.add_parser(name); p.add_argument('--base', default='HEAD')
        if name == 'log':
            p.add_argument('--by'); p.add_argument('--note')
    o = sub.add_parser('observe')
    o.add_argument('--source', required=True); o.add_argument('--seen', required=True)
    o.add_argument('--url'); o.add_argument('--date'); o.add_argument('--note')
    r = sub.add_parser('rotation'); r.add_argument('--n', type=int, default=5)
    f = sub.add_parser('finding')
    f.add_argument('--row', required=True); f.add_argument('--result', required=True, choices=['consistent', 'discrepancy', 'unable'])
    f.add_argument('--evidence', required=True); f.add_argument('--note'); f.add_argument('--reviewer', default='watchtower')
    rp = sub.add_parser('report'); rp.add_argument('--write', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'stats':
        print(json.dumps(stats(json.loads(SEED.read_text(encoding='utf-8'))), indent=1))
    elif a.cmd == 'diff':
        cmd_diff(a)
    elif a.cmd == 'log':
        cmd_diff(a, write=True)
    elif a.cmd == 'check':
        cmd_check(a)
    elif a.cmd == 'observe':
        cmd_observe(a)
    elif a.cmd == 'rotation':
        cmd_rotation(a)
    elif a.cmd == 'finding':
        cmd_finding(a)
    else:
        cmd_report(a)


if __name__ == '__main__':
    main()
