# DevOps Guidelines

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Runtime Topology](#runtime-topology)
2. [Containerization Standards](#containerization-standards)
3. [Local Environment Workflow](#local-environment-workflow)
4. [CI/CD Baseline](#cicd-baseline)
5. [GitOps and Deployment Strategy](#gitops-and-deployment-strategy)
6. [Observability Requirements](#observability-requirements)
7. [AI Integration Context](#ai-integration-context)

## Runtime Topology
Current local stack (`docker-compose.yml`):
- `api`: FastAPI app (`uvicorn`) running on `:8000`.
- `db`: PostgreSQL 18 (`:5532` host mapping).
- `redis`: Redis 8 (`:6679` host mapping), reserved for future caching/queue use.

## Containerization Standards
- Use the existing multi-stage `Dockerfile` (`builder` + `runtime`).
- Runtime image must stay minimal and non-root (`screenflix` user).
- Keep `PYTHONPATH=/app/src` and virtualenv path strategy intact.
- Health check endpoint is `/healthz`; changes to this path require synchronized updates.

## Local Environment Workflow
- Install dependencies: `uv sync --dev`.
- API only: `uv run uvicorn screenflix.main:app --reload --reload-dir src --host 0.0.0.0 --port 8000`.
- Full stack: `docker compose up --build`.
- Schema bootstrap currently uses `scripts/init.sql` mounted into PostgreSQL init directory.

## CI/CD Baseline
No `.github/workflows` currently exist. Required minimum pipeline:
1. Lint + format check.
2. Type check.
3. Test execution with coverage.
4. Security scans.
5. Docker build validation.

Deployment promotion should require all checks passing and reviewer approval.

## GitOps and Deployment Strategy
- ArgoCD manifests are not present today.
- If GitOps is introduced, maintain environment-specific overlays and immutable image tags.
- Keep deployment config outside application source folders.

## Observability Requirements
- Keep structured logs from `structlog` middleware.
- Include request-level context and trace IDs in logs.
- Add metrics and tracing (OpenTelemetry/Prometheus) before production scale rollout.

## AI Integration Context
Agents must treat build/deploy safety as mandatory: any change affecting container startup, health checks, dependency locks, or runtime env vars requires explicit validation steps in the change output and PR notes.
