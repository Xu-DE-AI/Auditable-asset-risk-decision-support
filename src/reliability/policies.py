from .schemas import RiskBand

def classify_risk(p: float) -> RiskBand:
    if not 0 <= p <= 1: raise ValueError("probability must be in [0,1]")
    if p >= .85: return RiskBand.CRITICAL
    if p >= .65: return RiskBand.HIGH
    if p >= .35: return RiskBand.ELEVATED
    return RiskBand.LOW

def maintenance_recommendation(band: RiskBand) -> tuple[str,int]:
    return {
        RiskBand.CRITICAL:("Urgent engineering review; verify sensor quality and inspect safely.",1),
        RiskBand.HIGH:("Prioritize maintenance planning and validate the observed condition.",2),
        RiskBand.ELEVATED:("Review trends at the next maintenance planning checkpoint.",3),
        RiskBand.LOW:("Continue routine monitoring under the approved maintenance plan.",4),
    }[band]

def authorize_decision(decision: str, reviewer_id: str, reason: str) -> None:
    if decision not in {"approve","reject"}: raise ValueError("decision must be approve or reject")
    if not reviewer_id.strip() or not reason.strip():
        raise ValueError("reviewer identity and rationale are required")
