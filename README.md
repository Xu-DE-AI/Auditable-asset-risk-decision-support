# Industrial Reliability Copilot

Auditable asset-risk decision support for industrial operations. Combines a time-aware scikit-learn model, a bounded LangGraph investigation workflow, typed Model Context Protocol (MCP) tools, policy checks, and a human-reviewed work-order lifecycle.

## Technology
Python 3.11+, FastAPI, Pydantic, scikit-learn, LangGraph, MCP Python SDK, pytest, Ruff, Docker, GitHub Actions, OpenTelemetry APIs. PostgreSQL is the intended persistence target; the included repository is an in-memory adapter for local execution.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m reliability.cli demo --output artifacts
uvicorn reliability.api:app --reload
```
In a second terminal, run `reliability-mcp` to expose the tools over local stdio transport.

## API
- `GET /health`
- `GET /assets/{asset_id}/risk`
- `POST /copilot/investigate` with `{"asset_id":"PUMP-104","question":"Why is this asset prioritized?"}`
- `POST /work-orders` creates a proposal, not an executed maintenance action.
- `POST /work-orders/{id}/decision` records reviewer approval/rejection.

## Harness and loop engineering
- Contract-first Pydantic schemas and allow-listed MCP tools.
- Explicit agent graph, finite step budget, request limits, and deterministic fallback.
- Chronological train/validation/test split; threshold chosen on validation only.
- Baseline comparison, finite-metric checks, artifact metadata, and regression tests.
- Human approval, idempotent work-order proposals, and audit events.
- Model monitoring loop: validate freshness, monitor score/alert distributions, evaluate when delayed labels mature, and roll back on failed gates.

## Production hardening required
The included app is a strong implementation baseline, not a certified or production-validated system. The demo dataset is synthetic. Before operational use, replace the in-memory repository with PostgreSQL/SQLAlchemy migrations; add enterprise identity/RBAC, secret management, TLS, OTLP export, image/dependency scanning, model registry/signing, SLOs, backups, restore tests, load tests, security review, and a real CMMS connector behind a separate approval boundary. Never expose the sample MCP server publicly as-is. No tool controls PLC/SCADA equipment.
