# Security Check Guide

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Current Security Posture](#current-security-posture)
2. [Authentication and Authorization](#authentication-and-authorization)
3. [Secrets and Configuration](#secrets-and-configuration)
4. [API and Data Protection Controls](#api-and-data-protection-controls)
5. [CI/CD Security Gates](#cicd-security-gates)
6. [Release Security Checklist](#release-security-checklist)
7. [AI Integration Context](#ai-integration-context)

## Current Security Posture
- No OAuth2/JWT authentication is currently implemented.
- No RBAC authorization layer is present.
- API exposure relies on network boundaries and deployment controls.
- External integrations exist (OMDb and OpenAI) and must be treated as untrusted inputs.

## Authentication and Authorization
Target standard for future implementation:
- Use OAuth2 Bearer tokens with JWT validation in FastAPI dependencies.
- Enforce RBAC by role claims (`viewer`, `editor`, `admin`) at endpoint or use-case boundary.
- Deny by default for routes handling write or sensitive operations.

Until implemented, do not claim protected endpoints in docs or clients.

## Secrets and Configuration
- Secrets must come from environment variables (`SCREENFLIX_OPENAI_API_KEY`, `SCREENFLIX_OMDB_API_KEY`, DB credentials).
- `.env` remains local-only and gitignored.
- Never log secret values or full upstream payloads that may include sensitive content.

## API and Data Protection Controls
- Keep strict schema validation on inbound/outbound payloads (Pydantic + JSON schema for LLM output).
- Preserve request timeouts and explicit HTTP error handling in adapters.
- Sanitize and normalize third-party data before persistence.
- Add rate limiting and auth middleware before public exposure.

## CI/CD Security Gates
Required pipeline checks (implement when CI is added):
- Lint, type, unit/integration tests.
- Secret scanning.
- Dependency vulnerability scan.
- Container image scan before deployment.

## Release Security Checklist
- No hardcoded secrets or tokens.
- New endpoints reviewed for auth/RBAC impact.
- External API error paths tested.
- Logging reviewed for sensitive data leakage.

## AI Integration Context
Agents must fail closed on security ambiguity: if auth, RBAC, or secret handling is unclear, mark as blocking and require explicit implementation or policy approval. AI-generated code must never bypass schema validation or introduce credential exposure patterns.
