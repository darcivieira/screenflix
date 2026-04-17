# Agents Knowledge Base

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Purpose](#purpose)
2. [Repository Snapshot](#repository-snapshot)
3. [Document Index](#document-index)
4. [How Documents Interact](#how-documents-interact)
5. [Usage Workflow for AI Tools](#usage-workflow-for-ai-tools)
6. [AI Integration Context](#ai-integration-context)

## Purpose
This directory centralizes AI-operational context for the Screenflix backend. It translates architecture, quality, security, and delivery standards into actionable guidance for autonomous and assisted engineering agents.

## Repository Snapshot
- Stack: Python 3.13, FastAPI, SQLAlchemy async, Pydantic, Structlog.
- Architecture: modular monolith with layered module structure.
- Data: PostgreSQL as primary store (`media`, `episode`), Redis declared in local stack.
- Integrations: OMDb ingestion and OpenAI schema-driven normalization.
- Delivery: Dockerfile + `docker-compose.yml`; CI workflow files are not yet present.

## Document Index
- `architecture-planning.md`: layer boundaries and structural decisions.
- `backend-development.md`: FastAPI async coding standards.
- `database-development.md`: entity/repository/schema persistence rules.
- `ai-ml-development.md`: LLM integration and structured-output guardrails.
- `security-check.md`: security controls and release criteria.
- `devops-guidelines.md`: containerization and CI/CD standards.
- `qa-guidelines.md`: test strategy and review process.

## How Documents Interact
1. Architecture defines allowable dependencies.
2. Backend and database guides operationalize architecture.
3. Security and QA guides define merge/release gates.
4. DevOps guide defines build and deploy expectations.
5. AI/ML guide constrains model-facing behavior and data safety.

## Usage Workflow for AI Tools
1. Read this file and `architecture-planning.md` first.
2. Load task-specific documents.
3. Execute required checks defined in `CONTRIBUTING.md` and `AI-CONFIG.json`.
4. If changing behavior or standards, update corresponding `/agents` files in the same change set.

## AI Integration Context
AI systems must treat this directory as authoritative operational context. When conflict exists between local assumptions and `/agents` documents, prefer `/agents`; when conflict exists inside `/agents`, prefer `architecture-planning.md` for design decisions and `security-check.md` for enforcement decisions.
