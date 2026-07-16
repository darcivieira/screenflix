---
name: quality-gate
description: Roda os quality gates bloqueantes do ScreenFlix (format, lint, tipos, testes). Use antes de concluir qualquer mudança de código.
invocation: both
---

Execute, nesta ordem, e pare no primeiro que falhar, reportando a saída:

1. `uv run ruff format src tests`
2. `uv run ruff check src tests`
3. `uv run mypy src`
4. `uv run pytest`

Atalho equivalente do projeto: `make check` (lint + typecheck + test — a formatação
fica no alvo `make format`).

Se algum passo falhar, resuma o erro e proponha a correção mínima antes de repetir.
Não considere a tarefa concluída enquanto os quatro passos não passarem.
