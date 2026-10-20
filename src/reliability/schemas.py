from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class RiskBand(str, Enum):
    LOW="low"
    ELEVATED="elevated"
    HIGH="high"
    CRITICAL="critical"

class InvestigationRequest(BaseModel):
    asset_id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    question: str = Field(min_length=3, max_length=1000)

class RiskScore(BaseModel):
    asset_id: str
    probability: float = Field(ge=0, le=1)
    risk_band: RiskBand
    model_version: str
    scored_at: datetime
    evidence: dict[str, float | str]

class InvestigationResult(BaseModel):
    investigation_id: str
    asset_id: str
    summary: str
    risk: RiskScore
    evidence: list[str]
    recommended_action: str
    requires_human_review: bool = True
    agent_mode: str

class WorkOrderProposal(BaseModel):
    asset_id: str = Field(min_length=2, max_length=64)
    title: str = Field(min_length=5, max_length=160)
    rationale: str = Field(min_length=10, max_length=2000)
    priority: int = Field(ge=1, le=5)
    idempotency_key: str = Field(min_length=8, max_length=128)

class WorkOrderDecision(BaseModel):
    decision: str = Field(pattern=r"^(approve|reject)$")
    reviewer_id: str = Field(min_length=2, max_length=128)
    reason: str = Field(min_length=5, max_length=1000)

class WorkOrderRecord(BaseModel):
    work_order_id: str
    asset_id: str
    title: str
    rationale: str
    priority: int
    status: str
    created_at: datetime
    reviewer_id: str | None = None
    decision_reason: str | None = None
