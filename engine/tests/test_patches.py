import pytest
from opengrid.patches import propose_changes


def test_proposed_change_is_isolated(example):
    proposal, audit = propose_changes(example, [{
        'op':'update','collection':'pv','id':'PV_250','changes':{'ac_kw':200}
    }])
    assert proposal.pv[0].ac_kw == 200
    assert example.pv[0].ac_kw == 250
    assert audit[0]['before']['ac_kw'] == 250


def test_existing_load_cannot_be_changed(example):
    with pytest.raises(ValueError, match='immutable'):
        propose_changes(example, [{
            'op':'update','collection':'loads','id':'HVAC','changes':{'p_kw':200}
        }])


def test_invalid_proposal_rejected(example):
    with pytest.raises(ValueError):
        propose_changes(example, [{
            'op':'update','collection':'pv','id':'PV_250','changes':{'ac_kw':400}
        }])


def test_agent_cannot_change_evidence(example):
    with pytest.raises(ValueError, match='protected'):
        propose_changes(example, [{
            'op':'update','collection':'pv','id':'PV_250','changes':{'evidence':['fake']}
        }])
