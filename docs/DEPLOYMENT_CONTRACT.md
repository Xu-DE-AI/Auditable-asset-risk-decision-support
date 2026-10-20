# Deployment contract

The current repository is an executable reference implementation for the application and safety boundaries. It is not ready to connect directly to production OT, CMMS, ERP, or insurer policy systems.

Included and executable:
- FastAPI request boundary and typed Pydantic contracts.
- LangGraph workflow with a bounded graph and deterministic fallback.
- Optional OpenAI-backed evidence synthesis, disabled by default.
- MCP stdio server with read tools and a proposal-only work-order tool.
- Chronological model evaluation, baseline comparison, artifact hash, and metadata.
- Idempotent proposal semantics, reviewer decision checks, and unit tests.
- Container build, CI workflow, and local operations guidance.

Required before a real deployment:
- Replace the in-memory repository with PostgreSQL/SQLAlchemy transactions and Alembic migrations.
- Replace the illustrative reviewer-role header with verified OIDC/OAuth identity and server-side RBAC.
- Add MCP authorization and TLS for remote transports; keep local stdio private.
- Configure OTLP exporters and the organization's metrics/logging backend.
- Pin dependencies with a generated lock file, scan dependencies/images, and sign model artifacts.
- Add real, reviewed asset data and time/group-based validation; set alert thresholds with maintenance stakeholders.
- Integrate a CMMS through a separate authenticated service, with idempotency, approval, retries, reconciliation, and audit logging.
- Run security, performance, recovery, and operational acceptance tests.

The synthetic dataset is solely for smoke testing. Reported metrics from it are not industrial performance evidence.
