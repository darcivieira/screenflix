# Contributing Guide

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Purpose](#purpose)
2. [Branching Strategy](#branching-strategy)
3. [Commit and Pull Request Standards](#commit-and-pull-request-standards)
4. [Quality Gates](#quality-gates)
5. [Security Gates](#security-gates)
6. [Coding Principles](#coding-principles)
7. [AI Integration Context](#ai-integration-context)

## Purpose
This repository is a Python 3.13 FastAPI backend with a modular layered design (`domain`, `application`, `infrastructure`, `presentation`). Contributions must preserve asynchronous behavior, strict typing, and clear layer boundaries.

## Branching Strategy
- `main`: protected, deployable branch.
- `feature/<scope>`: new functionality.
- `bugfix/<scope>`: functional fixes.
- `hotfix/<scope>`: urgent production fixes.
- `chore/<scope>`: tooling, docs, and maintenance.

Rebase feature branches on `main` before opening a PR.

## Commit and Pull Request Standards
- Use imperative commit titles aligned with current history style (for example: `Integrate catalog repository abstraction`).
- Keep subject lines concise (target <= 72 chars) and focused on one logical change.
- PRs must include:
  - Objective and scope.
  - Architectural impact (if any).
  - Validation evidence (commands + results).
  - API contract impact (request/response examples when applicable).
  - Linked issue or task reference.

## Quality Gates
Run locally before opening or updating a PR:
- `uv sync --dev`
- `uv run ruff format .`
- `uv run ruff check .`
- `uv run mypy src`
- `uv run pytest`

Coverage policy:
- Minimum 80% line coverage for changed modules.
- Every new component must include unit tests in the same PR (happy path, validation path, and failure path).
- 100% coverage for critical normalization/AI parsing paths when modified.

## Security Gates
- Never commit `.env`, secrets, tokens, or credential-like payload snapshots.
- New external integrations must use settings from `screenflix.core.settings`.
- Input/output contracts must remain schema-validated (Pydantic + JSON schema where applicable).
- For security-sensitive changes, include threat notes in PR description (auth, data exposure, secret handling).

## Coding Principles
- Maintain layered dependency direction:
  - `presentation` -> `application` -> `domain`.
  - `infrastructure` may depend on `domain` and shared `core`.
- Keep API endpoints thin; place orchestration in use cases.
- Preserve strict typing and avoid untyped public interfaces.
- Prefer explicit failures with actionable logs over silent fallbacks.

## AI Integration Context
AI assistants (Codex CLI, Junie AI, Cursor, CI bots) must:
- Load [AGENTS.md](AGENTS.md) first, then `/agents` documents relevant to the task.
- Propose or apply only changes that satisfy all quality and security gates.
- Respect architecture boundaries and avoid cross-layer shortcuts.
- Document assumptions in PR descriptions when code behavior is inferred.
- Reject tasks that require exposing secrets or bypassing required checks.
