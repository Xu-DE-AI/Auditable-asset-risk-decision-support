from mcp.server.fastmcp import FastMCP
from .repository import InMemoryRepository
from .service import RiskScorer, create_work_order
from .schemas import WorkOrderProposal
from .config import get_settings

mcp=FastMCP("industrial-reliability")
settings=get_settings()
repository=InMemoryRepository()
repository.seed_asset("PUMP-104",{"observed_at":"2026-01-10T10:00:00Z","vibration_rms":8.2,
 "temperature_c":91.0,"pressure_bar":8.9,"motor_current_a":46.0,"operating_hours":28400.0},
 ["2025-11-02: seal inspection","2026-01-02: vibration check"])
scorer=RiskScorer(settings.model_path)

@mcp.tool()
def get_asset_evidence(asset_id:str)->dict:
    """Read the latest approved telemetry summary and maintenance history."""
    return repository.get_asset_evidence(asset_id)

@mcp.tool()
def score_asset_risk(asset_id:str)->dict:
    """Return risk score, model version, and score evidence."""
    e=repository.get_asset_evidence(asset_id)
    return scorer(asset_id,e["telemetry"]).model_dump(mode="json")

@mcp.tool()
def propose_maintenance_work_order(asset_id:str,title:str,rationale:str,priority:int,
                                   idempotency_key:str)->dict:
    """Create a proposal for human review; never execute maintenance."""
    p=WorkOrderProposal(asset_id=asset_id,title=title,rationale=rationale,priority=priority,
                        idempotency_key=idempotency_key)
    return create_work_order(repository,p).model_dump(mode="json")

def main():
    # Local stdio only. Remote deployment requires authenticated transport and authorization.
    mcp.run(transport="stdio")

if __name__=="__main__": main()
