# Workshop ScreenFlix — Roteiros dos 3 Dias

Este material usa o repositório **ScreenFlix** como estudo de caso vivo para um
workshop de **3 dias**, com **1h30 (90 min) por dia**.

- **Maintainer / Instrutor:** Darci João Vieira Junior
- **Stack de referência:** Python 3.13 · FastAPI · SQLAlchemy async · Pydantic ·
  PostgreSQL · Docker · Vue 3 + Pinia + Vite

## Visão geral

| Dia | Tema | Foco | Roteiro |
|-----|------|------|---------|
| **1** | Infra & Containers | Docker, Dockerfile, docker-compose, comandos, Makefile | [`dia-1-infra-containers.md`](./dia-1-infra-containers.md) |
| **2** | Programação Pragmática | Ambientes modulares, Clean Architecture | [`dia-2-programacao-pragmatica.md`](./dia-2-programacao-pragmatica.md) |
| **3** | IA no Desenvolvimento | Claude Code, Skills, Subagents, Agent Teams | [`dia-3-ia-no-desenvolvimento.md`](./dia-3-ia-no-desenvolvimento.md) |

## Como cada roteiro é organizado

Cada dia segue a mesma estrutura para facilitar a condução:

1. **Objetivos de aprendizagem** — o que o participante sai sabendo.
2. **Pré-requisitos** — o que precisa estar instalado/aberto.
3. **Cronograma minuto a minuto** — blocos somando 90 min (com folga para dúvidas).
4. **Demonstrações ao vivo** — passos e comandos exatos, sempre apontando para
   arquivos reais do repositório.
5. **Mãos à obra (hands-on)** — exercícios que os participantes executam.
6. **Pontos de discussão** — trade-offs e decisões de arquitetura para debater.
7. **Encerramento e ganchos** — como o dia conecta com o próximo.

## Preparação geral (fazer antes do Dia 1)

```bash
# 1. Clonar o repositório
git clone <url-do-repo> screenflix && cd screenflix

# 2. Ferramentas necessárias
#    - Docker + Docker Compose
#    - uv (gerenciador de pacotes Python)   → https://docs.astral.sh/uv/
#    - Node.js 20+ (para o frontend, Dia 2)
#    - Claude Code CLI (Dia 3)

# 3. Criar o arquivo .env na raiz (ver Dia 1 para o conteúdo)
cp .env.example .env   # se existir; senão, criar conforme o roteiro do Dia 1
```

> **Observação honesta sobre o repo:** alguns itens do cronograma (ex.: persistência
> do banco no compose, migrations Alembic, CI) **ainda não existem** no repositório — e
> isso é proposital. Eles viram **exercícios ao vivo** durante o workshop. (O serviço
> `api` já está ativo no compose, o `redis` foi removido por falta de uso — exemplo de
> YAGNI — e o **Makefile** já existe: no Dia 1 nós o lemos, usamos e estendemos.)
> Cada roteiro sinaliza claramente o que existe hoje versus o que será criado em sala.

## Mapa de arquivos-chave usados nos roteiros

```
screenflix/
├── Dockerfile                 # Dia 1 — build multi-stage, non-root, healthcheck
├── docker-compose.yml         # Dia 1 — db (Postgres) + api ativos; sem redis
├── Makefile                   # Dia 1 — interface única: dev, qualidade, docker, frontend
├── scripts/init.sql           # Dia 1 — bootstrap do schema (media, episode)
├── pyproject.toml             # Dia 1/2 — deps, dependency-groups, ruff, mypy, pytest
├── src/screenflix/            # Dia 2 — Clean Architecture (core + modules/catalog)
├── frontend/                  # Dia 2 — Vue 3 + Pinia (ambiente modular via VITE_API_BASE)
├── AGENTS.md                  # Dia 3 — ponto de entrada de contexto para IA
├── AI-CONFIG.json             # Dia 3 — regras de runtime, guardrails, quality gates
└── agents/                    # Dia 3 — base de conhecimento por domínio
```
