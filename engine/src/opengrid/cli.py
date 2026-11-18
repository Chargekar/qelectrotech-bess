"""Agent-friendly CLI: JSON stdout, nonzero exit codes, no silent approval."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import typer

from .ingest import ingest_pdf
from .io import load_project
from .schema import ensure_simulation_ready
from .opendss import SCENARIOS, compile_dss, simulate
from .drawings import export_drawing
from .patches import propose_changes, load_operations
from .io import save_project
from .catalog import read_catalog, audit_catalog

app = typer.Typer(help='OpenGrid Engineer — CLI-first electrical model tools', no_args_is_help=True)


def emit(payload: dict) -> None:
    typer.echo(json.dumps(payload, indent=2, default=str))


def fail(exc: Exception, code: int = 2) -> None:
    emit({'ok': False, 'error': type(exc).__name__, 'message': str(exc)})
    raise typer.Exit(code=code)


@app.command()
def validate(model: Path = typer.Argument(..., help='Canonical YAML/JSON model'),
             study_ready: bool = typer.Option(False, '--study-ready', help='Require all feeder parameters'),
             catalog: Path | None = typer.Option(None, '--catalog', help='Check QET symbol catalog mapping')):
    """Validate schema and radial topology; optionally require study parameters."""
    try:
        project = load_project(model)
        if study_ready:
            ensure_simulation_ready(project)
        bridge = audit_catalog(project, catalog) if catalog else None
        emit({'ok': True, 'project': project.id, 'buses': len(project.buses),
              'feeders': len(project.feeders), 'loads': len(project.loads),
              'pv': len(project.pv), 'batteries': len(project.batteries),
              'wind': len(project.wind), 'study_ready': study_ready,
              'note': 'Schema/topology check is not engineering approval',
              'catalog_audit': bridge})
    except Exception as exc:
        fail(exc)


@app.command('compile')
def compile_cmd(model: Path, out: Path = typer.Option(Path('out/model.dss'), '--out'),
                scenario: str = typer.Option('baseline', '--scenario')):
    """Compile a model to OpenDSS text (no solver required)."""
    try:
        project = load_project(model)
        emit({'ok': True, **compile_dss(project, out, scenario)})
    except Exception as exc:
        fail(exc)


@app.command('draw')
def draw_cmd(model: Path, out: Path = typer.Option(Path('out/concept.svg'), '--out')):
    """Export concept-level SVG, DXF or PDF from verified topology."""
    try:
        project = load_project(model)
        emit({'ok': True, **export_drawing(project, out)})
    except Exception as exc:
        fail(exc)


@app.command('study')
def study_cmd(model: Path, scenario: str = typer.Option('baseline', '--scenario'),
              out: Path | None = typer.Option(None, '--out')):
    """Run OpenDSS steady-state study (requires optional dss-python backend)."""
    try:
        project = load_project(model)
        result = simulate(project, scenario)
        if out is not None:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        emit({'ok': True, **result})
    except Exception as exc:
        fail(exc, 3)


@app.command('ingest')
def ingest_cmd(pdf: Path, out: Path = typer.Option(Path('out/ingest.json'), '--out')):
    """Extract page text and candidate tags; requires human verification."""
    try:
        emit({'ok': True, **ingest_pdf(pdf, out)})
    except Exception as exc:
        fail(exc)


@app.command('propose')
def propose_cmd(model: Path, patch: Path,
                out: Path = typer.Option(Path('out/proposed.yaml'), '--out'),
                audit: Path = typer.Option(Path('out/change-audit.json'), '--audit')):
    """Apply agent patch to proposed equipment; preserve source, write change audit."""
    try:
        original = load_project(model)
        candidate, changes = propose_changes(original, load_operations(patch))
        if out.resolve() == model.resolve():
            raise ValueError('Refusing to overwrite the source model')
        out.parent.mkdir(parents=True, exist_ok=True)
        audit.parent.mkdir(parents=True, exist_ok=True)
        save_project(candidate, out)
        audit.write_text(json.dumps({'original_model': str(model), 'proposal': str(out),
                                     'approved': False, 'changes': changes},
                                    indent=2) + '\n', encoding='utf-8')
        emit({'ok': True, 'proposal': str(out), 'audit': str(audit),
              'changes': len(changes), 'approved': False})
    except Exception as exc:
        fail(exc)


@app.command('symbols')
def symbols_cmd(catalog: Path, symbol_id: str | None = typer.Option(None, '--id')):
    """Inspect the existing repository QET symbol inventory."""
    try:
        symbols = read_catalog(catalog)
        if symbol_id is not None:
            if symbol_id not in symbols:
                raise ValueError(f'Unknown symbol: {symbol_id}')
            emit({'ok': True, 'symbol': symbols[symbol_id]})
        else:
            emit({'ok': True, 'count': len(symbols),
                  'symbols': sorted(symbols.keys())})
    except Exception as exc:
        fail(exc)


@app.command('scenarios')
def scenarios_cmd():
    emit({'scenarios': list(SCENARIOS)})


if __name__ == '__main__':
    app()
