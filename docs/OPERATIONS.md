# Operations

Before production: replace the in-memory repository with PostgreSQL/SQLAlchemy and reviewed migrations; configure identity-backed RBAC, secrets, TLS, OTLP export, dependency/image scanning, artifact signing and registry, SLOs, backup/restore, load/security/failure-injection tests, and a real CMMS adapter behind a separate approval boundary.

## Evaluation loop
Maintain a versioned set of engineer-reviewed cases. Evaluate evidence retrieval, recommendation quality, unsupported claims, tool selection, policy violations, latency, and cost after every model/prompt/tool-schema change. Block releases on critical policy violations.

## Model loop
Monitor sensor freshness, schema drift, score distributions, alert rate, and delayed-label performance by site and asset family. Recalibrate only on reviewed data. Roll back on failed gates. Never let an agent alter its own policies.
