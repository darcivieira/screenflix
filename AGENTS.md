# AI Agents Entry Guide

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Purpose](#purpose)
2. [Context Loading Order](#context-loading-order)
3. [Document Map](#document-map)
4. [Execution Rules for AI Tools](#execution-rules-for-ai-tools)
5. [Component Unit Test Coverage Policy](#component-unit-test-coverage-policy)
6. [AI Integration Context](#ai-integration-context)

## Purpose
This file is the root entry point for machine and human contributors using AI-assisted workflows. It explains how `/agents` must be used as the canonical engineering context layer for this repository.

## Context Loading Order
1. Read `/agents/README.md`.
2. Read `/agents/architecture-planning.md`.
3. Read domain-specific guides based on task type:
   - Backend/API: `/agents/backend-development.md`
   - Database: `/agents/database-development.md`
   - AI/LLM: `/agents/ai-ml-development.md`
   - Security/operations/testing: corresponding guides in `/agents`
4. Apply root policies from `CONTRIBUTING.md` and runtime rules from `AI-CONFIG.json`.

## Document Map
- `/agents/architecture-planning.md`: architecture boundaries and design principles.
- `/agents/security-check.md`: security controls and release gates.
- `/agents/devops-guidelines.md`: container, CI/CD, deployment, observability.
- `/agents/qa-guidelines.md`: testing strategy and review quality bar.
- `/agents/backend-development.md`: FastAPI async development standards.
- `/agents/database-development.md`: SQLAlchemy/PostgreSQL conventions.
- `/agents/ai-ml-development.md`: OpenAI adapter and schema-normalized output rules.

## Execution Rules for AI Tools
- Do not bypass mandatory lint/type/test/security gates.
- Keep changes aligned with current modular layered architecture.
- Prioritize minimal, verifiable changes with explicit assumptions.
- Update `/agents` docs whenever architectural or policy behavior changes.
- Treat missing unit tests for new components as a blocking issue.

## Component Unit Test Coverage Policy
- Every new component must ship with unit tests in the same PR.
- Component means any new endpoint, use case, repository, adapter, entity helper, or utility module.
- Unit tests must cover at least:
  - Main success path.
  - Input validation/normalization behavior.
  - Failure path (exceptions, fallback, or rollback behavior).
- PRs that add components without unit tests must not be considered ready for merge.

## AI Integration Context
All AI systems (Codex CLI, Junie AI, Cursor, MCP agents, CI bots) must treat `/agents` as the authoritative context source before writing code, reviewing code, or proposing refactors. If context conflicts are found, architecture and security guides take precedence, then `CONTRIBUTING.md`, then task-specific instructions.
