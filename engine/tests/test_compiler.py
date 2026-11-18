from opengrid.opendss import render_dss, compile_dss, SCENARIOS


def test_scenario_injections(example):
    baseline = render_dss(example, 'baseline')
    maximum = render_dss(example, 'max-solar')
    charging = render_dss(example, 'bess-charging')
    assert 'New Circuit.ExampleBuilding' in baseline
    assert 'PVSystem.PV_250' in baseline
    assert 'Irradiance=1 Enabled=No' in baseline
    assert 'Irradiance=1 Enabled=Yes' in maximum
    assert 'State=CHARGING' in charging
    assert 'Generator.WIND_50' in baseline


def test_deterministic_compilation(example, tmp_path):
    p = tmp_path / 'model.dss'
    meta = compile_dss(example, p, 'baseline')
    assert meta['sha256'] == compile_dss(example, p, 'baseline')['sha256']
    assert p.read_text().endswith('Solve\n')


def test_scenarios_nonempty():
    assert len(SCENARIOS) >= 4
