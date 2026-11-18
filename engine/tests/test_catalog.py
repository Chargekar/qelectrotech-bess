import json
from pathlib import Path
import pytest
from opengrid.catalog import read_catalog, audit_catalog
from typer.testing import CliRunner
from opengrid.cli import app
from conftest import EXAMPLE

CATALOG = Path(__file__).resolve().parents[2] / "assets" / "catalog.json"


def test_repository_catalog_exists():
    assert CATALOG.is_file(), "Repository asset library should be checked out"
    symbols = read_catalog(CATALOG)
    assert "pv_inverter" in symbols
    assert "power_conversion_system" in symbols
    assert "utility" in symbols


def test_model_maps_existing_qet_assets(example):
    report = audit_catalog(example, CATALOG)
    assert report["catalog_symbols"] > 50
    assert {x["equipment_id"] for x in report["mapped"]} >= {"GRID", "PV_250", "BESS_500"}
    assert report["unmapped"] == [{"kind": "wind_turbine", "count": 1}]


def test_catalog_rejects_duplicate_symbol(tmp_path):
    file = tmp_path / "bad.json"
    file.write_text(json.dumps({"symbols": [{"id": "bus"}, {"id": "bus"}]}))
    with pytest.raises(ValueError, match="Duplicate"):
        read_catalog(file)


def test_cli_catalog_audit():
    r = CliRunner().invoke(app, ["validate", str(EXAMPLE), "--catalog", str(CATALOG)])
    assert r.exit_code == 0, r.output
    report = json.loads(r.output)
    assert report["catalog_audit"]["mapped"]


def test_cli_symbols():
    r = CliRunner().invoke(app, ["symbols", str(CATALOG), "--id", "pv_inverter"])
    assert r.exit_code == 0, r.output
    assert json.loads(r.output)["symbol"]["id"] == "pv_inverter"
