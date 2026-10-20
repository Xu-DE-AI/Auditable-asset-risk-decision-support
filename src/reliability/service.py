from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from .features import build_features
from .model import load_model
from .policies import classify_risk, authorize_decision
from .schemas import RiskScore, WorkOrderProposal

class RiskScorer:
    def __init__(self, model_path=None):
        self.bundle=load_model(model_path) if model_path and Path(model_path).exists() else None
    def __call__(self, asset_id, telemetry):
        if self.bundle:
            X=build_features(pd.DataFrame([{"asset_id":asset_id,**telemetry}]))
            p=float(self.bundle["model"].predict_proba(X)[:,1][0]); version=self.bundle["model_version"]
            evidence={"source":"model","threshold":float(self.bundle["threshold"])}
        else:
            v=float(telemetry["vibration_rms"]); t=float(telemetry["temperature_c"])
            c=float(telemetry["motor_current_a"]); z=-5+.15*v+.02*max(t-65,0)+.015*max(c-38,0)
            p=float(1/(1+np.exp(-z))); version="fallback-rule-v1"
            evidence={"source":"deterministic_fallback","vibration_rms":v,"temperature_c":t,
                      "motor_current_a":c}
        return RiskScore(asset_id=asset_id,probability=p,risk_band=classify_risk(p),
                         model_version=version,scored_at=datetime.now(timezone.utc),evidence=evidence)

def create_work_order(repository, proposal: WorkOrderProposal):
    return repository.create_proposal(proposal)

def decide_work_order(repository, order_id, decision, reviewer_id, reason):
    authorize_decision(decision,reviewer_id,reason)
    return repository.decide(order_id,decision,reviewer_id,reason)
