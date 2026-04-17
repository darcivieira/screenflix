# Backend Development Guide (FastAPI)

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Backend Stack](#backend-stack)
2. [API Layer Conventions](#api-layer-conventions)
3. [Application and Domain Rules](#application-and-domain-rules)
4. [External Adapter Rules](#external-adapter-rules)
5. [Typing, Validation, and Logging](#typing-validation-and-logging)
6. [Background and Async Execution](#background-and-async-execution)
7. [AI Integration Context](#ai-integration-context)

## Backend Stack
- FastAPI + Uvicorn.
- Async SQLAlchemy session management.
- Pydantic for request/response schemas.
- Structlog for structured request and error logging.

## API Layer Conventions
- Keep route handlers in `modules/*/presentation/api/v1/enpoints`.
- Endpoints should:
  - Validate input via Pydantic schemas.
  - Delegate orchestration to use cases.
  - Return explicit HTTP errors only for transport concerns.
- Preserve `/api/v1` prefix strategy.

## Application and Domain Rules
- Application use cases orchestrate multi-step workflows.
- Domain entities represent persisted business objects.
- Avoid embedding transport logic (HTTP details) in use cases or entities.
- Prefer deterministic normalization methods for external payload cleanup.

## External Adapter Rules
- Integrations (`omdb_request`, `openai_analyzer`) must remain isolated in adapters.
- Use explicit timeouts and status handling from `BaseHttpRequest`.
- Normalize third-party responses before persistence.
- Keep prompt/schema logic versioned and testable when changed.

## Typing, Validation, and Logging
- Mypy strict mode is required (`pyproject.toml`).
- Add type hints to all new public functions and methods.
- Keep Pydantic schemas aligned with entity and API contracts.
- Preserve middleware request context (`trace_id`, route path, method, optional headers).

## Background and Async Execution
- Current register flow launches asynchronous background execution from endpoint.
- Maintain non-blocking behavior (`asyncio.create_task`, `asyncio.gather`, semaphores).
- If durable background processing is needed, introduce a queue worker (Celery/RQ) explicitly; none is currently implemented.

## AI Integration Context
Agents must produce backend changes that remain async-safe, typed, and layer-compliant. Any endpoint change must include validation/model updates; any use-case change must include failure-path and rollback considerations.
