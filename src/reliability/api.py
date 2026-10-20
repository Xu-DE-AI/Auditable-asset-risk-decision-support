from uuid import uuid4
from fastapi import FastAPI, HTTPException, Header
from .config import get_settings
from .repository import InMemoryRepository
from .service import RiskScorer, create_work_order, decide_work_order
from .agent import investigate
from .schemas import InvestigationRequest, InvestigationResult, RiskScore, WorkOrderProposal, WorkOrderDecision, WorkOrderRecord

settings=get_settings()
app=FastAPI(title="Industrial Reliability Copilot API",version="1.0.0")
repository=InMemoryRepository()
repository.seed_asset("PUMP-104",{"observed_at":"2026-01-10T10:00:00Z","vibration_rms":8.2,
 "temperature_c":91.0,"pressure_bar":8.9,"motor_current_a":46.0,"operating_hours":28400.0},
 ["2025-11-02: seal inspection","2026-01-02: vibration check"])
scorer=RiskScorer(settings.model_path)

@app.middleware("http")
async def request_id(request,call_next):
    rid=request.headers.get("x-request-id",str(uuid4()))
    response=await call_next(request); response.headers["x-request-id"]=rid
    return response

@app.get("/health")
def health(): return {"status":"ok","service":"industrial-reliability-copilot"}

@app.get("/assets/{asset_id}/risk",response_model=RiskScore)
def risk(asset_id:str):
    try: return scorer(asset_id,repository.get_asset_evidence(asset_id)["telemetry"])
    except KeyError as e: raise HTTPException(404,"Asset not found") from e

@app.post("/copilot/investigate",response_model=InvestigationResult)
def copilot(req:InvestigationRequest):
    try: return investigate(repository,scorer,req.asset_id,req.question,settings.max_agent_steps)
    except KeyError as e: raise HTTPException(404,"Asset not found") from e

@app.post("/work-orders",response_model=WorkOrderRecord,status_code=201)
def propose(p:WorkOrderProposal):
    try: return create_work_order(repository,p)
    except KeyError as e: raise HTTPException(404,"Asset not found") from e

@app.post("/work-orders/{order_id}/decision",response_model=WorkOrderRecord)
def decide(order_id:str,d:WorkOrderDecision,x_reviewer_role:str=Header(default="viewer")):
    # Illustrative role header only; replace with verified identity/RBAC before deployment.
    if x_reviewer_role.lower() not in {"maintenance_approver","admin"}:
        raise HTTPException(403,"Reviewer role is not authorized")
    try: return decide_work_order(repository,order_id,d.decision,d.reviewer_id,d.reason)
    except KeyError as e: raise HTTPException(404,"Work order not found") from e
    except ValueError as e: raise HTTPException(409,str(e)) from e
