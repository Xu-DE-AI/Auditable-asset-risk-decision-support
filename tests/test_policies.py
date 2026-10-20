import pytest
from reliability.policies import classify_risk, authorize_decision
from reliability.schemas import RiskBand

def test_risk_thresholds():
    assert classify_risk(.1) is RiskBand.LOW
    assert classify_risk(.7) is RiskBand.HIGH

def test_invalid_probability_fails_closed():
    with pytest.raises(ValueError): classify_risk(1.2)

def test_reviewer_identity_is_required():
    with pytest.raises(ValueError): authorize_decision("approve","","approved")
