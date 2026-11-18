import json
from typer.testing import CliRunner
from opengrid.cli import app
from conftest import EXAMPLE

runner = CliRunner()


def test_cli_validate():
    r = runner.invoke(app, ['validate', str(EXAMPLE), '--study-ready'])
    assert r.exit_code == 0, r.output
    assert json.loads(r.output)['ok'] is True


def test_cli_compile(tmp_path):
    target=tmp_path/'out.dss'
    r=runner.invoke(app, ['compile', str(EXAMPLE), '--scenario', 'max-solar', '--out', str(target)])
    assert r.exit_code == 0, r.output
    assert target.is_file()


def test_cli_bad_scenario(tmp_path):
    r=runner.invoke(app, ['compile', str(EXAMPLE), '--scenario', 'typo', '--out', str(tmp_path/'bad.dss')])
    assert r.exit_code != 0
    assert json.loads(r.output)['ok'] is False
