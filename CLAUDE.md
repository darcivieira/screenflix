# ScreenFlix — Contexto para Claude Code

Este projeto mantém uma camada de contexto de engenharia. Carregue-a antes de agir:

@AGENTS.md
@AI-CONFIG.json
@agents/architecture-planning.md

## Regras rápidas
- Arquitetura: monólito modular em camadas (domain → application → infrastructure → presentation).
  **Nunca** acesse o banco a partir da camada de presentation — sempre service → repository.
- Rode os quality gates antes de concluir uma mudança: `make check`
  (lint + typecheck + testes). Formatação: `make format`.
- Todo componente novo (endpoint, use case, service, repository, adapter) exige testes
  no mesmo change set: caminho feliz, validação e erro (ver `agents/qa-guidelines.md`).
- Segredos vêm sempre do ambiente (`SCREENFLIX_*`). Nunca commite `.env`.

## Comandos
- Dev local (API com reload): `make dev`
- Stack completo (db + api): `make up-build`
- Qualidade (CI local): `make check`
- Banco (psql): `make db-shell`
