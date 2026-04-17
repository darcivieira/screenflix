# AI/ML Development Guide

- Version: 1.0.0
- Last Review Date: 2026-04-15
- Maintainer: CTO – Darci João Vieira Junior

## Table of Contents
1. [Current AI Scope](#current-ai-scope)
2. [Model Integration Pattern](#model-integration-pattern)
3. [Prompt and Schema Governance](#prompt-and-schema-governance)
4. [Reliability and Error Handling](#reliability-and-error-handling)
5. [Data Safety and Cost Controls](#data-safety-and-cost-controls)
6. [Testing Requirements for AI Paths](#testing-requirements-for-ai-paths)
7. [AI Integration Context](#ai-integration-context)

## Current AI Scope
The project uses OpenAI Responses API to normalize media and episode payloads before persistence. Core implementation lives in `modules/catalog/adapters/openai_analyzer.py` and is invoked by `RegisterDataWorkflow`.

## Model Integration Pattern
- Adapter encapsulates API calls and response parsing.
- Prompt selection depends on payload type (`media` or `episode`).
- Output is constrained by JSON schema loaded from `schemas.json`.
- Normalization retries up to 3 attempts on malformed model output.

## Prompt and Schema Governance
- Treat prompts and schema as versioned behavior contracts.
- Any field addition/removal requires synchronized updates in:
  - `schemas.json`
  - prompt mapping rules
  - domain entities/schemas/repositories as needed
- Keep prompts factual, deterministic, and non-promotional.

## Reliability and Error Handling
- Preserve timeout and structured error handling in adapter calls.
- Keep parse fallback sequence: direct parse -> fenced block cleanup -> object extraction.
- Fail with explicit exceptions when JSON cannot be normalized.

## Data Safety and Cost Controls
- Do not include secrets in prompts.
- Send only data required for transformation.
- Keep token limits and retry counts bounded (`max_output_tokens`, retry loops).
- Log failures with metadata, not sensitive payload contents.

## Testing Requirements for AI Paths
When AI behavior changes, validate:
- Prompt payload construction.
- JSON extraction and parsing robustness.
- Retry behavior and terminal failure path.
- Schema compliance of normalized output.

## AI Integration Context
Agents must treat AI output as untrusted until schema-validated and normalized. Any AI-related patch must include deterministic fallback/error behavior and a clear compatibility statement with `schemas.json` and persistence models.
