import pytest
from pydantic import ValidationError
from opengrid.schema import Project, ensure_simulation_ready
from opengrid.io import save_project, load_project


def test_sample_model_valid(example):
    assert len(example.buses) == 6
    ensure_simulation_ready(example)


def test_reject_unknown_load_bus(example):
    data = example.model_dump(mode='json')
    data['loads'][0]['bus'] = 'MISSING'
    with pytest.raises(ValidationError, match='unknown bus'):
        Project.model_validate(data)


def test_reject_cycle(example):
    data = example.model_dump(mode='json')
    data['feeders'].append(dict(id='F_LOOP', from_bus='PV_BUS', to_bus='BESS_BUS',
                                length_km=0.1))
    with pytest.raises(ValidationError, match='radial'):
        Project.model_validate(data)


def test_unknown_impedance_blocks_simulation(example):
    example.feeders[0].r1_ohm_per_km = None
    with pytest.raises(ValueError, match='Simulation blocked'):
        ensure_simulation_ready(example)


def test_reject_duplicate_id(example):
    data = example.model_dump(mode='json')
    data['loads'][0]['id'] = 'MSB'
    with pytest.raises(ValidationError, match='globally unique'):
        Project.model_validate(data)


def test_json_roundtrip(example, tmp_path):
    path = tmp_path / 'model.json'
    save_project(example, path)
    assert load_project(path) == example
