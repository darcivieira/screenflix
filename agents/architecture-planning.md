# Architecture Planning Guide

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Current Architecture](#current-architecture)
2. [Layer Model](#layer-model)
3. [Module Responsibilities](#module-responsibilities)
4. [Dependency Rules](#dependency-rules)
5. [Change Planning Rules](#change-planning-rules)
6. [AI Integration Context](#ai-integration-context)

## Current Architecture
The codebase is a **modular monolith** implemented in FastAPI. The catalog domain follows a layered style close to Clean/Hexagonal principles:
- `domain`: entities and domain semantics.
- `application`: use case orchestration.
- `infrastructure`: repositories and integration implementations.
- `presentation`: HTTP API and schemas.

## Layer Model
- Entry point: `screenflix.main`.
- Shared framework/core concerns in `screenflix.core`.
- Business feature module in `screenflix.modules.catalog`.
- Cross-layer flow: request -> endpoint -> use case -> adapters/repositories -> database/external APIs.

## Module Responsibilities
- `core/`: settings, async DB session factory, generic repository base, structured logging middleware.
- `modules/catalog/domain/entities`: SQLAlchemy entities (`Media`, `Episode`).
- `modules/catalog/application/use_cases`: orchestration (`RegisterDataWorkflow`).
- `modules/catalog/adapters`: OMDb and OpenAI API clients.
- `modules/catalog/infrastructure/repositories`: persistence operations.
- `modules/catalog/presentation/api/v1`: routes and response/request models.

## Dependency Rules
- `domain` should not import `presentation`.
- `presentation` should not implement business logic beyond request/response concerns.
- `application` coordinates domain + adapters/repositories.
- `infrastructure` and `adapters` may depend on `core`, never on `presentation`.
- Shared utilities belong in `core`, not feature modules.

## Change Planning Rules
- Preserve async boundaries; do not introduce blocking I/O in request paths.
- Keep endpoint handlers thin; place orchestration in use cases.
- For major structure changes, add an ADR section in the PR description:
  - Context
  - Decision
  - Consequences
- When introducing new modules, replicate existing layer folders for consistency.

## AI Integration Context
Agents must classify every requested change by layer first, then apply modifications only inside the proper layer(s). If a proposed change crosses boundaries (for example direct DB calls in endpoints), agents must refactor toward layer compliance before merging.
