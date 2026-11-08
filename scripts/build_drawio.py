"""Generate reusable Draw.io SLD templates from the relational model. Stdlib only.

python scripts/build_drawio.py [--db build/bess.sqlite] [--output assets/drawio/bess-sld-templates.drawio]

Pages: A grid-tied (AC-coupled), B backup (hybrid PCS + critical load panel), Legend (every class).
Every vertex is an <object> carrying class_id / symbol_id / tag attributes so the file can be parsed
back into the model or mapped to QET elements. Values are {{PLACEHOLDERS}}, never project numbers.
Only stencils present in drawio_shape are used; the build fails otherwise.
"""
import argparse, sqlite3, sys
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parents[1]
LAYERS = ['Frame', 'Power', 'Grounding', 'Sense-Control', 'Annotation']
EDGE = {
    'ac': 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeWidth=2;',
    'dc': 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeWidth=2;',
    'pe': 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeWidth=1;dashed=1;dashPattern=1 4 4 4;',
    'sense': 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeWidth=1;dashed=1;dashPattern=4 4;',
    'control': 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=open;endSize=6;strokeWidth=1;dashed=1;dashPattern=8 4;',
}
LAYER_OF = {'ac': 'Power', 'dc': 'Power', 'pe': 'Grounding', 'sense': 'Sense-Control', 'control': 'Sense-Control'}
TEXT = 'text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=9;spacing=0;'


class Page:
    def __init__(self, cx, name, pid):
        self.cx, self.name, self.pid, self.cells, self.n = cx, name, pid, [], 0
        self.layer = {l: f'{pid}-L{i}' for i, l in enumerate(LAYERS)}

    def nid(self, p):
        self.n += 1
        return f'{self.pid}-{p}{self.n}'

    def symbol(self, sid):
        r = self.cx.execute('SELECT id,drawio_kind,drawio_shape,drawio_style,w,h FROM symbol WHERE id=?', (sid,)).fetchone()
        if not r: raise SystemExit(f'unknown symbol {sid}')
        return dict(zip(['id', 'kind', 'shape', 'style', 'w', 'h'], r))

    def vertex(self, style, x, y, w, h, value='', layer='Power', parent=None, attrs=None):
        cid = self.nid('v')
        par = parent or self.layer[layer]
        geo = f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        cell = f'<mxCell style={quoteattr(style)} vertex="1" parent="{par}">{geo}</mxCell>'
        if attrs:
            a = ''.join(f' {k}={quoteattr(str(v))}' for k, v in attrs.items())
            self.cells.append(f'<object id="{cid}" label={quoteattr(value)}{a}>{cell}</object>')
        else:
            self.cells.append(cell.replace('<mxCell ', f'<mxCell id="{cid}" value={quoteattr(value)} ', 1))
        return cid

    def text(self, x, y, w, h, value, size=9, bold=False):
        return self.vertex(TEXT + f'fontSize={size};' + ('fontStyle=1;' if bold else ''), x, y, w, h, value, 'Annotation')

    def place(self, cls, x, y, tag, rating='', sym=None, glyph='', label_pos='below', w=None, h=None, scope='new'):
        """Place one equipment occurrence (center-left anchored at x, vertically centered on y)."""
        if sym is None:
            sym = self.cx.execute('SELECT symbol_id FROM equipment_class WHERE id=?', (cls,)).fetchone()[0]
        s = self.symbol(sym)
        w, h = w or s['w'], h or s['h']
        top = y - h / 2
        attrs = {'class_id': cls, 'symbol_id': sym, 'tag': tag, 'scope': scope}
        if s['kind'] == 'composite' and sym in ('power_conversion_system', 'pv_inverter', 'hybrid_inverter'):
            cid = self.vertex(s['style'], x, top, w, h, '', 'Power', attrs=attrs)
            self.diagonal(x, top, w, h, sym)
        else:
            cid = self.vertex(s['style'], x, top, w, h, glyph, 'Power', attrs=attrs)
        lab = f'<b>{escape(tag)}</b>' + (f'<br>{rating}' if rating else '')
        if label_pos == 'below':
            self.text(x - 10, top + h + 4, max(w + 30, 90), 34, lab)
        elif label_pos == 'above':
            self.text(x - 10, top - 36, max(w + 30, 90), 34, lab)
        elif label_pos == 'side':
            self.text(x + w + 6, top, 120, 46, lab)
        return cid

    def diagonal(self, x, y, w, h, sym):
        e = self.nid('e')
        self.cells.append(f'<mxCell id="{e}" style="endArrow=none;html=1;strokeWidth=1;" edge="1" parent="{self.layer["Power"]}">'
                          f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x}" y="{y + h}" as="sourcePoint"/>'
                          f'<mxPoint x="{x + w}" y="{y}" as="targetPoint"/></mxGeometry></mxCell>')
        top, bot = ('AC', 'DC') if sym != 'pv_inverter' else ('DC', 'AC')
        st = 'text;html=1;fontSize=8;align=center;verticalAlign=middle;'
        self.vertex(st, x + 2, y + 2, 20, 12, top, 'Power')
        self.vertex(st, x + w - 22, y + h - 14, 20, 12, bot, 'Power')

    def edge(self, src, dst, domain, sx=None, sy=None, tx=None, ty=None, points=None, label=''):
        st = EDGE[domain]
        if sx is not None: st += f'exitX={sx};exitY={sy};exitDx=0;exitDy=0;'
        if tx is not None: st += f'entryX={tx};entryY={ty};entryDx=0;entryDy=0;'
        pts = ''
        if points:
            pts = '<Array as="points">' + ''.join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in points) + '</Array>'
        if label: st += 'fontSize=8;labelBackgroundColor=#ffffff;'
        e = self.nid('e')
        self.cells.append(f'<object id="{e}" label={quoteattr(label)} domain="{domain}"><mxCell style={quoteattr(st)} edge="1" '
                          f'parent="{self.layer[LAYER_OF[domain]]}" source="{src}" target="{dst}">'
                          f'<mxGeometry relative="1" as="geometry">{pts}</mxGeometry></mxCell></object>')
        return e

    def frame(self, title, mode_note, notes):
        self.vertex('rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeWidth=2;', 10, 10, 1200, 990, '', 'Frame')
        self.vertex('rounded=0;whiteSpace=wrap;html=1;fillColor=none;', 930, 890, 280, 110, '', 'Frame')
        self.text(938, 896, 265, 100, '<b>{{PROJECT_NAME}}</b><br>{{SITE_ADDRESS}}<br>' + escape(title) +
                  '<br>Sheet {{SHEET}} &nbsp; Rev {{REV}} &nbsp; {{DATE}}<br><b>PRELIMINARY: NOT FOR CONSTRUCTION</b><br>Seal area intentionally blank', 8)
        self.text(30, 20, 900, 20, f'<b>{escape(title)}</b> &nbsp; (NTS) &nbsp; {escape(mode_note)}', 12)
        body = '<b>KEYED NOTES</b> (templates; resolve placeholders and cite the clause of the selected edition)<br>' + \
               '<br>'.join(f'<b>{i}.</b> [{nid}] {escape(t)}' for i, (nid, t) in enumerate(notes, 1))
        self.text(30, 845, 890, 150, body, 8)
        self.text(30, 815, 700, 20, 'LINES: power solid &nbsp; sense dashed 4-4 &nbsp; control dashed 8-4 (arrow = command) &nbsp; grounding dash-dot', 8)

    def xml(self):
        layers = ''.join(f'<mxCell id="{lid}" value="{l}" parent="0"/>' for l, lid in self.layer.items())
        return (f'<diagram id="{self.pid}" name={quoteattr(self.name)}><mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" '
                f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1220" pageHeight="1010" math="0" shadow="0">'
                f'<root><mxCell id="0"/>{layers}{"".join(self.cells)}</root></mxGraphModel></diagram>')


def notes(cx, ids):
    return [cx.execute('SELECT id, template FROM note_template WHERE id=?', (i,)).fetchone() for i in ids]


BUSX, CBX, D1, D2, D3, D4, LINE_Y, BUS_TOP = 480, 520, 650, 780, 900, 1010, 130, 80


def service_and_bus(p, bus_h):
    """Utility -> utility transformer -> revenue meter -> main -> MS bus; CTs clamp the service conductors."""
    y = LINE_Y
    u = p.place('utility', 40, y, '{{UTILITY}}', 'Service {{SERVICE_V}}<br>{{PHASES}}PH {{WIRES}}W')
    t = p.place('utility_transformer', 130, y, 'Utility XFMR', '{{XFMR_KVA}} kVA (utility)')
    m = p.place('utility_meter', 230, y, 'M', 'Utility meter<br>#{{METER_NO}}', glyph='M')
    mb = p.place('main_breaker', 370, y, 'MAIN', '{{MAIN_A}}A/{{MAIN_P}}P')
    ct = p.place('ct', 316, y, 'CT-1', 'Service CTs', label_pos='above')
    bus = p.place('service_switchboard', BUSX, BUS_TOP + bus_h / 2, '{{MS_TAG}}', '{{MS_BUS}}A bus<br>{{MS_V}}<br>{{MS_AIC}} kAIC', h=bus_h, label_pos='side')
    p.edge(u, t, 'ac', 1, 0.5, 0, 0.5); p.edge(t, m, 'ac', 1, 0.5, 0, 0.5)
    p.edge(m, mb, 'ac', 1, 0.5, 0, 0.5)
    p.edge(mb, bus, 'ac', 1, 0.5, 0, (y - BUS_TOP) / bus_h)
    g = p.place('grounding_electrode', BUSX - 7, BUS_TOP + bus_h + 40, 'GEC', '{{GEC_SIZE}} to electrode', label_pos='side')
    p.edge(bus, g, 'pe', 0.5, 1, 0.5, 0)
    return ct, bus


def feeder(p, bus, bus_h, y, tag, rating):
    cb = p.place('breaker', CBX, y, tag, rating)
    p.edge(bus, cb, 'ac', 1, (y - BUS_TOP) / bus_h, 0, 0.5)
    return cb


def loads(p, bus, bus_h):
    cb1 = feeder(p, bus, bus_h, 180, 'CB-L', '{{FEEDER_A}}A/3P')
    pnl = p.place('branch_panel', D1, 180, '{{BRANCH_PANELS}}', 'MLO panels, not backed up', w=130, glyph='PANELS')
    p.edge(cb1, pnl, 'ac', 1, 0.5, 0, 0.5)
    cb2 = feeder(p, bus, bus_h, 270, 'CB-AUX', '{{AUX_A}}A/{{AUX_P}}P')
    aux = p.place('aux_switchboard', D1, 270, 'AUX', '{{AUX_V}}', glyph='AUX')
    ups = p.place('ups', D2, 270, 'UPS', '{{UPS_KVA}} kVA', sym='aux_box', glyph='UPS')
    ems = p.place('ems', D3, 270, 'EMS', '{{EMS_MODEL}}', glyph='EMS')
    das = p.place('das_meter', 200, 240, 'DAS', '{{DAS_MODEL}}<br>monitoring only', glyph='DAS')
    p.edge(cb2, aux, 'ac', 1, 0.5, 0, 0.5); p.edge(aux, ups, 'ac', 1, 0.5, 0, 0.5); p.edge(ups, ems, 'ac', 1, 0.5, 0, 0.5)
    return ems, das


def sensing(p, ct, ems, das):
    p.edge(ct, ems, 'sense', 0.5, 0, 0.5, 0, points=[(320, 62), (D3 + 35, 62)])
    p.edge(ct, das, 'sense', 0.5, 1, 1, 0.5, points=[(320, 253)])


def pv(p, bus, bus_h, y, note):
    cb = feeder(p, bus, bus_h, y, 'CB-PV', '{{PV_A}}A/3P')
    d = p.place('pv_ac_disconnect', D1, y, 'PVD', '{{PVD_A}}A NF, lockable')
    inv = p.place('pv_inverter', D2, y, 'INV-PV', '{{PV_INV_MODEL}} {{PV_AC_KW}} kW')
    arr = p.place('pv_array', D3, y, 'PV', '{{PV_KWDC}} kWdc STC<br>' + note, label_pos='side')
    p.edge(cb, d, 'ac', 1, 0.5, 0, 0.5); p.edge(d, inv, 'ac', 1, 0.5, 0, 0.5); p.edge(inv, arr, 'dc', 1, 0.5, 0, 0.5)


def page_a(cx):
    p, bus_h = Page(cx, 'A Grid-tied AC-coupled BESS', 'A'), 620
    ct, bus = service_and_bus(p, bus_h)
    ems, das = loads(p, bus, bus_h)
    sensing(p, ct, ems, das)
    pv(p, bus, bus_h, 420, 'RSD per 690.12')
    y = 630
    cb = feeder(p, bus, bus_h, y, 'CB-BESS', '{{BESS_A}}A/3P')
    acd = p.place('ac_disconnect', D1, y, 'BESS-ACD', '{{ACD_A}}A NF, lockable')
    p.vertex(p.symbol('bess_cabinet')['style'], 765, 518, 330, 200,
             '<b>{{BESS_TAG}}</b> listed ESS: {{BESS_MODEL}}<br>{{BESS_KWH}} kWh / {{BESS_KW}} kW, {{CHEM}}, {{ENCL}}',
             'Power', attrs={'class_id': 'bess_cabinet', 'symbol_id': 'bess_cabinet', 'tag': '{{BESS_TAG}}', 'scope': 'new'})
    pcs = p.place('pcs_conversion', D2, y, 'PCS', '{{PCS_MODEL}} {{PCS_KW}} kW')
    dcd = p.place('battery_dc_disconnect', D3, y, 'DCD', '{{DCD_A}}A {{DC_VMAX}}Vdc')
    bat = p.place('battery_rack', D4, y, 'BATT', '{{RACKS}} x {{MODULE}}')
    bms = p.place('bms', D4 + 10, 585, 'BMS', '', glyph='BMS', label_pos='none')
    p.edge(cb, acd, 'ac', 1, 0.5, 0, 0.5); p.edge(acd, pcs, 'ac', 1, 0.5, 0, 0.5)
    p.edge(pcs, dcd, 'dc', 1, 0.5, 0, 0.5); p.edge(dcd, bat, 'dc', 1, 0.5, 0, 0.5)
    p.edge(bms, pcs, 'control', 0, 0.5, 0.3, 0, points=[(D2 + 18, 585)])
    est = p.place('estop', 1115, 630, 'ESD', 'Emergency<br>shutdown', label_pos='above')
    p.edge(est, pcs, 'control', 0.5, 1, 0.5, 1, points=[(1140, 708), (D2 + 30, 708)])
    p.edge(ems, pcs, 'control', 1, 0.5, 0.75, 0, points=[(1185, 270), (1185, 566), (D2 + 45, 566)])
    gb = p.place('grounding_electrode', D4 + 20, 740, 'GND-BESS', 'EGC/GEC per manual', label_pos='side')
    p.edge(bat, gb, 'pe', 0.5, 1, 0.5, 0)
    p.text(30, 700, 420, 60, '<b>MODE:</b> grid-parallel only. No isolation device and no backed-up panel; the BESS stops on grid loss. '
           'Source breakers sit at the bus end opposite the main (120 percent method layout).', 9)
    p.frame('SLD-A: Grid-tied AC-coupled PV + BESS', 'Operating mode: grid-parallel',
            notes(cx, ['N-SERVICE', 'N-OCP', 'N-CONDUCTOR', 'N-ESS-LISTING', 'N-ISOLATION', 'N-PCS-SETTING', 'N-UTILITY', 'N-T24', 'N-GROUND']))
    return p


def page_b(cx):
    p, bus_h = Page(cx, 'B Backup hybrid PCS + CLP', 'B'), 600
    ct, bus = service_and_bus(p, bus_h)
    ems, das = loads(p, bus, bus_h)
    sensing(p, ct, ems, das)
    pv(p, bus, bus_h, 360, 'AC-coupled on MS: NOT backed up')
    y = 540
    cb = feeder(p, bus, bus_h, y, 'CB-BESS', '{{BESS_A}}A/3P grid port')
    acd = p.place('ac_disconnect', D1, y, 'BESS-ACD', '{{ACD_A}}A NF, lockable')
    p.vertex(p.symbol('bess_cabinet')['style'], 765, 482, 110, 128, 'Listed hybrid,<br>integral MID', 'Power',
             attrs={'class_id': 'mid', 'symbol_id': 'bess_cabinet', 'tag': 'MID (integral)', 'scope': 'new'})
    hy = p.place('hybrid_inverter', D2 + 5, y + 10, 'HINV', '{{PCS_MODEL}}', label_pos='none')
    p.text(885, 600, 150, 30, '<b>HINV</b> {{PCS_MODEL}}<br>grid {{PCS_KW}} kW, backup {{BACKUP_KW}} kW', 9)
    cbb = feeder(p, bus, bus_h, 650, 'CB-BYP', '{{BYP_A}}A/3P bypass')
    mbp = p.place('maintenance_bypass', 920, 527, 'MBP', 'Interlocked bypass {{MBP_A}}A', label_pos='above')
    clp = p.place('critical_load_panel', 1040, 527, '{{CLP_TAG}}', '{{CLP_BUS}}A bus, {{CLP_MAIN}}A<br>backed-up loads only', w=110, glyph='CLP')
    p.edge(cb, acd, 'ac', 1, 0.5, 0, 0.5); p.edge(acd, hy, 'ac', 1, 0.5, 0, 0.32, label='grid')
    p.edge(hy, mbp, 'ac', 1, 0.32, 0, 0.5, label='backup')
    p.edge(cbb, mbp, 'ac', 1, 0.5, 0.5, 1, points=[(950, 650)])
    p.edge(mbp, clp, 'ac', 1, 0.5, 0, 0.5)
    dcd = p.place('battery_dc_disconnect', 840, 740, 'DCD', '{{DCD_A}}A {{DC_VMAX}}Vdc')
    bat = p.place('battery_rack', 980, 740, '{{BESS_TAG}}', '{{BESS_MODEL}}<br>{{BESS_KWH}} kWh {{CHEM}}', label_pos='side')
    p.edge(hy, dcd, 'dc', 0.5, 1, 0, 0.5, points=[(D2 + 40, 740)])
    p.edge(dcd, bat, 'dc', 1, 0.5, 0, 0.5)
    est = p.place('estop', 1115, 440, 'ESD', 'Emergency shutdown', label_pos='above')
    p.edge(est, hy, 'control', 0, 0.5, 0.75, 0, points=[(D2 + 57, 440)])
    p.edge(ems, hy, 'control', 1, 0.5, 0.25, 0, points=[(1185, 270), (1185, 472), (D2 + 22, 472)])
    gb = p.place('grounding_electrode', 1000, 800, 'GND-BESS', 'EGC/GEC; neutral bond per manual', label_pos='side')
    p.edge(bat, gb, 'pe', 0.5, 1, 0.5, 0)
    p.text(30, 720, 420, 70, '<b>MODES:</b> grid-parallel, islanded (MID open, HINV grid-forming), bypass (MBP on grid). '
           'Only {{CLP_TAG}} is backed up. To back up PV, move it to the CLP side or DC-couple it to HINV.', 9)
    p.frame('SLD-B: Backup option, hybrid PCS with critical load panel', 'Operating modes: grid-parallel / islanded / bypass',
            notes(cx, ['N-SERVICE', 'N-OCP', 'N-CONDUCTOR', 'N-ESS-LISTING', 'N-ISOLATION', 'N-BACKUP-BOUNDARY', 'N-PCS-SETTING', 'N-UTILITY', 'N-GROUND']))
    return p


def page_legend(cx):
    p = Page(cx, 'Legend: symbol map', 'G')
    rows = cx.execute("""SELECT ec.id, ec.term, ec.abbrev, s.id, s.drawio_kind, s.drawio_shape, s.qet_elmt
                         FROM equipment_class ec JOIN symbol s ON s.id = ec.symbol_id ORDER BY ec.family_id, ec.id""").fetchall()
    p.text(30, 24, 1100, 20, '<b>Symbol map</b>: class, Draw.io realization (stencil = verified palette shape; composite/basic = drawn), QET element', 12)
    cols, cw, rh = 6, 190, 104
    glyphs = {'meter': 'M', 'relay': '27/59', 'das': 'DAS', 'aux_box': 'BOX', 'bms': 'BMS', 'controller': 'CTRL', 'dc_combiner': 'CMB'}
    for i, (cid, term, ab, sid, kind, shape, qet) in enumerate(rows):
        x, y = 30 + (i % cols) * cw, 60 + (i // cols) * rh
        s = p.symbol(sid)
        w, h = min(s['w'], 70), min(s['h'], 44)
        if sid == 'bus': w, h = 6, 44
        if sid in ('power_conversion_system', 'pv_inverter', 'hybrid_inverter'):
            p.vertex(s['style'], x, y, 44, 44, '', 'Power', attrs={'class_id': cid, 'symbol_id': sid, 'tag': ab or cid, 'scope': 'legend'})
            p.diagonal(x, y, 44, 44, sid)
        else:
            g = glyphs.get(sid, '') if sid not in ('aux_box', 'load_panel', 'controller') else (ab or '')
            p.vertex(s['style'], x, y, w, h, g, 'Power', attrs={'class_id': cid, 'symbol_id': sid, 'tag': ab or cid, 'scope': 'legend'})
        p.text(x, y + 50, cw - 10, 50, f'<b>{escape(term)}</b> ({escape(ab or "")})<br>{kind}: {escape((shape or "").replace("mxgraph.electrical.", ""))}'
               f'<br>QET: {escape(qet or "to author")}', 7)
    return p


def validate(xml, cx):
    import re, xml.etree.ElementTree as ET
    root = ET.fromstring(xml)
    ok = {r[0] for r in cx.execute('SELECT shape FROM drawio_shape')}
    errs = []
    for d in root.iter('diagram'):
        ids = set()
        for el in d.iter():
            if el.get('id'): ids.add(el.get('id'))
        for c in d.iter('mxCell'):
            m = re.search(r'shape=(mxgraph\.electrical\.[\w.\-]+)', c.get('style') or '')
            if m and m.group(1) not in ok: errs.append(f'{d.get("name")}: unverified shape {m.group(1)}')
            for k in ('parent', 'source', 'target'):
                if c.get(k) and c.get(k) not in ids: errs.append(f'{d.get("name")}: dangling {k} {c.get(k)}')
            if c.get('edge') == '1' and c.get('source') is None and 'sourcePoint' not in ET.tostring(c, encoding='unicode'):
                errs.append(f'{d.get("name")}: unbound edge')
            if c.get('parent') == '0' and c.get('vertex') == '1': errs.append(f'{d.get("name")}: vertex parented to root')
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=str(ROOT / 'build/bess.sqlite'))
    ap.add_argument('--output', default=str(ROOT / 'assets/drawio/bess-sld-templates.drawio'))
    a = ap.parse_args()
    cx = sqlite3.connect(a.db)
    pages = [page_a(cx), page_b(cx), page_legend(cx)]
    xml = '<mxfile host="qelectrotech-bess" type="device" version="24.0.0">' + ''.join(p.xml() for p in pages) + '</mxfile>'
    errs = validate(xml, cx)
    if errs:
        print('\n'.join(errs), file=sys.stderr); sys.exit(1)
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(xml, encoding='utf-8')
    print(f'{out} pages={len(pages)} cells={sum(len(p.cells) for p in pages)} (all stencils verified, all edges bound)')


if __name__ == '__main__':
    main()
