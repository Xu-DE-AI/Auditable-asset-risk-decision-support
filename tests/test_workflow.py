import pytest
from reliability.repository import InMemoryRepository
from reliability.schemas import WorkOrderProposal
from reliability.service import decide_work_order

def test_proposal_is_idempotent_and_requires_review():
    r=InMemoryRepository(); r.seed_asset("PUMP-104",{"vibration_rms":8})
    p=WorkOrderProposal(asset_id="PUMP-104",title="Inspect pump bearing",
      rationale="Vibration trend is elevated and needs engineering review.",priority=2,
      idempotency_key="pump104-bearing-001")
    a=r.create_proposal(p); b=r.create_proposal(p)
    assert a.work_order_id==b.work_order_id and a.status=="pending_review"

def test_decision_cannot_be_repeated():
    r=InMemoryRepository(); r.seed_asset("PUMP-104",{"vibration_rms":8})
    p=WorkOrderProposal(asset_id="PUMP-104",title="Inspect pump bearing",
      rationale="Vibration trend is elevated and needs engineering review.",priority=2,
      idempotency_key="pump104-bearing-002")
    w=r.create_proposal(p)
    decide_work_order(r,w.work_order_id,"reject","reviewer-1","Insufficient evidence.")
    with pytest.raises(ValueError):
      decide_work_order(r,w.work_order_id,"approve","reviewer-2","Second decision.")
