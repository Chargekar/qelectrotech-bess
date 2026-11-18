"""Deterministic concept single-line output from canonical graph.

SVG/PDF/DXF exported here are REVIEW DRAFTS, not permit-ready drawings.
"""
from __future__ import annotations

from collections import defaultdict
from html import escape
from pathlib import Path

import networkx as nx

from .schema import Project


def geometry(project: Project):
    graph = nx.Graph()
    graph.add_nodes_from(b.id for b in project.buses)
    graph.add_edges_from((f.from_bus, f.to_bus) for f in project.feeders)
    root = project.source.bus
    tree = nx.bfs_tree(graph, root)
    depth = nx.single_source_shortest_path_length(graph, root)
    leaves = [node for node in tree.nodes if tree.out_degree(node) == 0]
    leaf_y = {leaf: 125 + i * 152 for i, leaf in enumerate(leaves)}
    ys = {}

    def y_of(node):
        if node in ys:
            return ys[node]
        children = list(tree.successors(node))
        ys[node] = sum(y_of(child) for child in children) / len(children) if children else leaf_y[node]
        return ys[node]

    y_of(root)
    return {node: (110 + depth[node] * 370, ys[node]) for node in graph.nodes}, tree


def _devices(project: Project, bus: str) -> list[str]:
    details = []
    for load in project.loads:
        if load.bus == bus:
            details.append(f"{load.id}: {load.p_kw:g} kW load")
    for pv in project.pv:
        if pv.bus == bus:
            details.append(f"{pv.id}: {pv.ac_kw:g} kW PV")
    for b in project.batteries:
        if b.bus == bus:
            details.append(f"{b.id}: {b.pcs_kw:g} kW / {b.energy_kwh:g} kWh")
    for wind in project.wind:
        if wind.bus == bus:
            details.append(f"{wind.id}: {wind.rated_kw:g} kW wind")
    return details


def render_svg(project: Project) -> str:
    pos, _ = geometry(project)
    bus_map = {b.id: b for b in project.buses}
    width = max(x for x, _ in pos.values()) + 390
    height = max(y for _, y in pos.values()) + 170
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17243a}.label{font-weight:bold;font-size:14px}.tiny{font-size:12px;fill:#526477}.watermark{fill:#ad2333;font-weight:bold;font-size:16px}</style>',
        f'<text x="35" y="35" font-size="22" font-weight="bold">{escape(project.title)}</text>',
        '<text x="35" y="62" class="watermark">CONCEPT / ENGINEER REVIEW REQUIRED — NOT FOR CONSTRUCTION</text>',
    ]
    # Draw electrical paths first; component blocks later to keep them legible.
    for f in sorted(project.feeders, key=lambda x: x.id):
        a, b = pos[f.from_bus], pos[f.to_bus]
        # Either from_bus or to_bus can be parent in the radial tree.
        if a[0] > b[0]:
            a, b = b, a
        x0, y0 = a[0] + 245, a[1]
        x1, y1 = b[0], b[1]
        mid = (x0 + x1) / 2
        stroke = "#226db4" if f.status.value == "proposed" else "#23364b"
        elements.append(f'<polyline points="{x0},{y0} {mid},{y0} {mid},{y1} {x1},{y1}" fill="none" stroke="{stroke}" stroke-width="3"/>')
        elements.append(f'<text class="tiny" x="{x1-8}" y="{y1-52}" text-anchor="end">{escape(f.id)}</text>')
    for bus in sorted(project.buses, key=lambda b: pos[b.id][0]):
        x, y = pos[bus.id]
        proposed = bus.status.value == "proposed"
        fill = "#e7f2ff" if proposed else "#eef1f5"
        stroke = "#226db4" if proposed else "#455668"
        elements.append(f'<rect x="{x}" y="{y-46}" width="245" height="92" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        elements.append(f'<text x="{x+12}" y="{y-10}" class="label">{escape(bus.id)} ({bus.voltage_ll_kv*1000:g} V)</text>')
        elements.append(f'<text x="{x+12}" y="{y+8}" class="tiny">{escape(bus.label or bus.id)}</text>')
        details = _devices(project, bus.id)
        if details:
            # Two rows, each capped for readability in PDF; full text remains in title.
            for i, detail in enumerate(details[:2]):
                shown = detail[:33] + ('…' if len(detail)>33 else '')
                elements.append(f'<text x="{x+12}" y="{y+25+i*16}" class="tiny"><title>{escape(detail)}</title>{escape(shown)}</text>')
            if len(details)>2:
                elements.append(f'<text x="{x+175}" y="{y+41}" class="tiny">+{len(details)-2} more</text>')
    elements.append(f'<text x="35" y="{height-30}" class="tiny">Existing: slate | Proposed: blue | Graph topology only; protective devices and construction details not modeled</text>')
    elements.append('</svg>')
    return "\n".join(elements)


def render_dxf(project: Project, target: Path) -> None:
    try:
        import ezdxf
    except ImportError as exc:
        raise RuntimeError('DXF export requires: pip install ".[draw]"') from exc
    pos, _ = geometry(project)
    doc = ezdxf.new('R2013')
    doc.layers.add('EXISTING', color=7)
    doc.layers.add('PROPOSED', color=5)
    doc.layers.add('ANNOTATIONS', color=2)
    ms = doc.modelspace()
    ms.add_text("CONCEPT / ENGINEER REVIEW REQUIRED - NOT FOR CONSTRUCTION",
                dxfattribs={'height': 17, 'insert': (25, 30), 'layer': 'ANNOTATIONS'})
    for f in project.feeders:
        a, b = pos[f.from_bus], pos[f.to_bus]
        if a[0] > b[0]:
            a, b = b, a
        p0 = (a[0]+245, a[1]); p1 = (b[0], b[1]); mid = (p0[0]+p1[0])/2
        ms.add_lwpolyline([p0, (mid,p0[1]), (mid,p1[1]), p1],
                          dxfattribs={'layer': 'PROPOSED' if f.status.value=='proposed' else 'EXISTING'})
        ms.add_text(f.id, dxfattribs={'height': 11, 'insert': (mid+4, min(p0[1],p1[1])+9), 'layer': 'ANNOTATIONS'})
    for bus in project.buses:
        x,y=pos[bus.id]
        layer='PROPOSED' if bus.status.value=='proposed' else 'EXISTING'
        ms.add_lwpolyline([(x,y-46),(x+245,y-46),(x+245,y+46),(x,y+46),(x,y-46)],dxfattribs={'layer':layer})
        ms.add_text(f'{bus.id} - {bus.voltage_ll_kv*1000:g}V',dxfattribs={'height':14,'insert':(x+10,y+4),'layer':'ANNOTATIONS'})
        text='; '.join(_devices(project, bus.id)) or bus.label
        ms.add_text(text[:65],dxfattribs={'height':10,'insert':(x+10,y-17),'layer':'ANNOTATIONS'})
    target.parent.mkdir(parents=True,exist_ok=True)
    doc.saveas(str(target))


def export_drawing(project: Project, target: Path) -> dict:
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    suffix = target.suffix.lower()
    if suffix == '.dxf':
        render_dxf(project, target)
    elif suffix == '.svg':
        target.write_text(render_svg(project), encoding='utf-8')
    elif suffix == '.pdf':
        try:
            import cairosvg
        except ImportError as exc:
            raise RuntimeError('PDF drawing export requires: pip install ".[draw]"') from exc
        cairosvg.svg2pdf(bytestring=render_svg(project).encode(), write_to=str(target))
    else:
        raise ValueError('Output extension must be .svg, .pdf, or .dxf')
    return {"output": str(target), "status": "concept_drawing_only", "approved": False}
