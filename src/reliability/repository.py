from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4
from .schemas import WorkOrderProposal, WorkOrderRecord

class InMemoryRepository:
    # Replace this adapter with PostgreSQL/SQLAlchemy and migrations before deployment.
    def __init__(self):
        self.lock=RLock(); self.assets={}; self.history={}; self.orders={}; self.keys={}; self.audit=[]
    def seed_asset(self, asset_id, telemetry, history=None):
        with self.lock:
            self.assets[asset_id]=dict(telemetry); self.history[asset_id]=list(history or [])
    def get_asset_evidence(self, asset_id):
        with self.lock:
            if asset_id not in self.assets: raise KeyError(asset_id)
            return {"asset_id":asset_id,"telemetry":dict(self.assets[asset_id]),
                    "maintenance_history":list(self.history.get(asset_id,[]))}
    def create_proposal(self, p: WorkOrderProposal):
        with self.lock:
            if p.idempotency_key in self.keys: return self.orders[self.keys[p.idempotency_key]]
            if p.asset_id not in self.assets: raise KeyError(p.asset_id)
            record=WorkOrderRecord(work_order_id="WO-"+uuid4().hex[:12].upper(),
              asset_id=p.asset_id,title=p.title,rationale=p.rationale,priority=p.priority,
              status="pending_review",created_at=datetime.now(timezone.utc))
            self.orders[record.work_order_id]=record; self.keys[p.idempotency_key]=record.work_order_id
            self.audit.append({"event":"work_order_proposed","id":record.work_order_id})
            return record
    def decide(self, order_id, decision, reviewer_id, reason):
        with self.lock:
            record=self.orders[order_id]
            if record.status!="pending_review": raise ValueError("Only pending work orders can be decided")
            updated=record.model_copy(update={"status":"approved" if decision=="approve" else "rejected",
                "reviewer_id":reviewer_id,"decision_reason":reason})
            self.orders[order_id]=updated
            self.audit.append({"event":"work_order_decision","id":order_id,"decision":decision,
                               "reviewer_id":reviewer_id,"reason":reason})
            return updated
