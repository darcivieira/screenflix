# Database Development Guide

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Current Data Stack](#current-data-stack)
2. [Schema and Entity Conventions](#schema-and-entity-conventions)
3. [Repository and Query Rules](#repository-and-query-rules)
4. [Migration Strategy](#migration-strategy)
5. [Data Integrity and Performance](#data-integrity-and-performance)
6. [AI Integration Context](#ai-integration-context)

## Current Data Stack
- Database: PostgreSQL.
- ORM: SQLAlchemy 2.x async.
- Session lifecycle: centralized in `screenflix.core.database`.
- Bootstrap: `scripts/init.sql` initializes `media` and `episode` tables.
- Alembic dependency exists, but migration scripts are not yet in the repository.

## Schema and Entity Conventions
- Keep table names singular and lowercase (`media`, `episode`) for consistency with existing schema.
- Use integer primary keys (`BIGSERIAL` in SQL, `Mapped[int]` in ORM).
- Keep timestamps via `TimestampMixin` (`created_at`, `updated_at`).
- Use explicit relationship configuration and avoid uncontrolled lazy loading.

## Repository and Query Rules
- Repositories extend `BaseRepository` for standard CRUD/query behavior.
- Domain-specific lookup queries belong in module repositories (for example episode by media/season/episode).
- Keep filtering and ordering deterministic.
- Do not query DB directly from presentation layer.

## Migration Strategy
Current state is SQL bootstrap first. Target state:
1. Add Alembic configuration and migration folder.
2. Convert schema changes into versioned migrations.
3. Keep `init.sql` only for first-run local bootstrap, not production drift control.

## Data Integrity and Performance
- Validate normalized input before persistence (already done in use-case workflow).
- Keep indexes aligned with query patterns (`title`, `media_type`, season/episode composite lookups).
- For high-volume ingestion, batch writes and review transaction scope.

## AI Integration Context
Agents must model DB changes as schema + ORM + repository updates in one coherent patch. If a change touches persistence, agents must document migration impact and add/update tests covering new query behavior.
