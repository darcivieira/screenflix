# QA Guidelines

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Current Testing State](#current-testing-state)
2. [Testing Strategy](#testing-strategy)
3. [Test Types and Scope](#test-types-and-scope)
4. [Mandatory Unit Tests Per Component](#mandatory-unit-tests-per-component)
5. [Coverage and Quality Thresholds](#coverage-and-quality-thresholds)
6. [Code Review Process](#code-review-process)
7. [AI Integration Context](#ai-integration-context)

## Current Testing State
- `pytest` and `pytest-asyncio` are configured in `pyproject.toml`.
- Markers are defined: `integration`, `slow`.
- `tests/` exists but currently has no committed test files.

## Testing Strategy
Adopt a practical pyramid for this backend:
- Unit tests for normalization and parsing logic.
- Service/use-case tests for orchestration behavior.
- Integration tests for repository and database flows.
- Endpoint tests for route contracts and status semantics.

## Test Types and Scope
- Unit focus:
  - `RegisterDataWorkflow` normalization helpers.
  - OpenAI response normalization parsing logic.
- Integration focus:
  - SQLAlchemy repositories with PostgreSQL.
  - End-to-end register flow (with upstream adapters mocked).
- Use markers:
  - `@pytest.mark.integration` for container-dependent tests.
  - `@pytest.mark.slow` for long-running scenarios.

## Mandatory Unit Tests Per Component
- Every newly developed component must include unit tests in the same change set.
- Components covered by this rule:
  - API endpoint handlers.
  - Use cases and orchestration services.
  - Repositories and query helpers.
  - Adapters/integration-normalization logic.
  - Shared utility functions.
- Minimum required scenarios per component:
  - Happy path.
  - Validation/normalization path.
  - Error path with expected failure behavior.
- A PR is blocked if a new component is introduced without corresponding unit tests.

## Coverage and Quality Thresholds
- Repository target: >= 80% line coverage over modified modules.
- Critical parsing/normalization branches: >= 90%.
- For every new component, target >= 85% line coverage in the component module.
- Required checks before merge:
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run pytest`

## Code Review Process
Reviewers verify:
- Layer boundaries are preserved.
- Async and error-handling behavior remains deterministic.
- New/changed behavior is covered by tests.
- Every new component has explicit unit tests and coverage evidence in the PR.
- API response models remain consistent with documented schemas.

## AI Integration Context
Agents must not open PR-ready changes without test impact analysis. Missing unit tests for a new component are blocking and must be resolved before merge readiness. Any change in parsing, persistence, or API contracts requires corresponding automated test updates.
