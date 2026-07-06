# Dia 1 — Infra & Containers

> **Duração:** 90 min · **Tema:** Docker nas aplicações, Dockerfile, docker-compose, comandos e Makefile
> **Repositório de referência:** ScreenFlix (FastAPI + PostgreSQL)

---

## 🎯 Objetivos de aprendizagem

Ao final do dia, o participante será capaz de:

1. Explicar **por que** usamos containers em aplicações modernas (paridade dev/prod, isolamento, reprodutibilidade).
2. Ler e escrever um **Dockerfile multi-stage** otimizado (imagem enxuta, non-root, healthcheck).
3. Orquestrar múltiplos serviços com **docker-compose** (app + banco + cache).
4. Dominar os **comandos** essenciais do dia a dia (`build`, `up`, `logs`, `exec`, `down`).
5. Encapsular esses comandos em um **Makefile** para padronizar o fluxo do time.

## ✅ Pré-requisitos

- Docker + Docker Compose instalados (`docker --version`, `docker compose version`).
- `uv` instalado (para rodar a app fora do container e comparar).
- Repositório clonado e terminal aberto na raiz.
- Editor com o projeto aberto para navegar nos arquivos.

---

## 🕐 Cronograma (90 min)

| Bloco | Tempo | Conteúdo |
|-------|-------|----------|
| 1 | 0–10 min | Abertura: por que containers? O problema que resolvem |
| 2 | 10–30 min | Dockerfile do ScreenFlix (multi-stage, dissecado linha a linha) |
| 3 | 30–50 min | docker-compose: subindo o Postgres + ativando `api`/`redis` |
| 4 | 50–70 min | Comandos essenciais na prática (build, logs, exec, healthcheck) |
| 5 | 70–88 min | **Hands-on:** criar um Makefile para o projeto |
| 6 | 88–90 min | Fechamento e gancho para o Dia 2 |

---

## Bloco 1 — Por que containers? (0–10 min)

**Narrativa de abertura.** O ScreenFlix depende de: Python 3.13, PostgreSQL 18, variáveis de ambiente, `libpq`, um virtualenv. Sem containers, cada dev precisa reproduzir isso manualmente ("na minha máquina funciona"). Com containers:

- **Reprodutibilidade** — a mesma imagem roda igual em qualquer lugar.
- **Isolamento** — o Postgres do projeto não conflita com outro instalado localmente.
- **Paridade dev/prod** — a imagem que testo é a que vai para produção.

**Ponto de ancoragem no repo:** mostrar o `.python-version` (`3.13`) e o `pyproject.toml` (dependências como `asyncpg`, `psycopg[binary]`, que exigem libs de sistema). É exatamente isso que o Dockerfile encapsula.

---

## Bloco 2 — O Dockerfile do ScreenFlix (10–30 min)

**Arquivo:** [`Dockerfile`](../../Dockerfile)

Este é um **build multi-stage** — um padrão de produção. Percorra ao vivo:

```dockerfile
# ── Stage 1: builder ─────────────────────────────
FROM python:3.13-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev --compile-bytecode --no-install-project
COPY src/ src/

# ── Stage 2: runtime ─────────────────────────────
FROM python:3.13-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r screenflix && useradd -r -g screenflix -d /app screenflix
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY --from=builder /app/src src/
COPY schemas.json .
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
USER screenflix
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/healthz || exit 1
EXPOSE 8000
CMD ["uvicorn", "screenflix.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Pontos a destacar (por que cada decisão importa):**

| Técnica | Onde | Por quê |
|---------|------|---------|
| **Multi-stage** | `builder` vs `runtime` | O `build-essential`/`libpq-dev` (pesados) ficam só no builder. O runtime só recebe o `.venv` já compilado → imagem final menor e mais segura. |
| **`--no-install-recommends` + `rm -rf .../apt/lists`** | ambos stages | Reduz o tamanho e a superfície de ataque. |
| **Ordem de `COPY`** | `pyproject.toml`+`uv.lock` antes de `src/` | Cache de camadas: mudar código não invalida a camada de dependências. |
| **`uv sync --frozen --no-dev`** | builder | Instala exatamente o lockfile, sem deps de desenvolvimento. |
| **Usuário non-root** (`screenflix`) | runtime | Boa prática de segurança — o container não roda como root. |
| **`HEALTHCHECK` em `/healthz`** | runtime | O orquestrador sabe se o container está saudável (endpoint real em [`src/screenflix/main.py`](../../src/screenflix/main.py)). |
| **`PYTHONPATH=/app/src`** | runtime | Alinha com o layout `src/` do projeto. |

> **Demonstração ao vivo:**
> ```bash
> docker build -t screenflix:latest .
> docker images screenflix           # observar o tamanho da imagem final
> docker history screenflix:latest   # ver as camadas
> ```

**Discussão:** o `HEALTHCHECK` aponta para `GET /healthz`, definido no `main.py`:
```python
@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```
Mudar essa rota quebraria o healthcheck — é um contrato de infra, não só de código.

---

## Bloco 3 — docker-compose: orquestrando serviços (30–50 min)

**Arquivo:** [`docker-compose.yml`](../../docker-compose.yml)

**Estado atual do repo (importante!):** hoje **só o serviço `db` está ativo**. Os serviços `api` e `redis`, e os volumes nomeados, estão **comentados**. Isso é ótimo material didático: começamos com o mínimo e vamos *ativando* serviços ao vivo.

```yaml
services:
  db:
    image: postgres:18-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5532:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 3
```

**Conceitos a extrair deste bloco:**

- **`image` vs `build`** — `db` usa imagem pronta; o serviço `api` (comentado) usa `build: { context: ., dockerfile: Dockerfile, target: runtime }`.
- **Variáveis de ambiente** — vêm de `${POSTGRES_USER}` etc. → precisam de um `.env`.
- **Volume de bootstrap** — `./scripts/init.sql` é montado em `/docker-entrypoint-initdb.d/`, e o Postgres executa esse SQL na **primeira** inicialização. Abrir o [`scripts/init.sql`](../../scripts/init.sql) e mostrar a criação das tabelas `media` e `episode` (com índices, CHECK constraint e FK `ON DELETE CASCADE`).
- **Port mapping** — `5532:5432` (host:container) — escolhido para não conflitar com um Postgres local na 5432.
- **`healthcheck` com `pg_isready`** — e o `depends_on: { db: { condition: service_healthy } }` do serviço `api` (comentado) garante ordem de subida.

**Criar o `.env` (ao vivo):**
```bash
# .env na raiz — NÃO versionar (já está no .gitignore)
POSTGRES_USER=screenflix
POSTGRES_PASSWORD=screenflix
POSTGRES_DB=screenflix

SCREENFLIX_APP_NAME=ScreenFlix
SCREENFLIX_APP_DESCRIPTION="Catálogo de filmes e séries"
SCREENFLIX_DATABASE_URL=postgresql+asyncpg://screenflix:screenflix@db:5432/screenflix
SCREENFLIX_OPENAI_API_KEY=sk-...        # placeholder no workshop
SCREENFLIX_OMDB_API_KEY=...             # placeholder no workshop
```

> **Demonstração ao vivo — subir só o banco:**
> ```bash
> docker compose up -d db
> docker compose ps
> docker compose logs -f db          # ver o init.sql rodando
> docker compose exec db psql -U screenflix -d screenflix -c "\dt"   # listar tabelas
> ```

### Mini-exercício guiado: ativar `api` e `redis`

Descomentar os blocos `api` e `redis` no `docker-compose.yml` e subir o stack completo:

```bash
docker compose up --build
# api em :8000, db em :5532, redis em :6679
curl http://localhost:8000/healthz
```

**Discussão:** o serviço `api` comentado usa `volumes: - ./src:/app/src` + `--reload` para hot-reload em dev. Contraste: **imagem imutável (prod)** vs **bind-mount com reload (dev)** — o mesmo Dockerfile serve aos dois modos.

---

## Bloco 4 — Comandos essenciais na prática (50–70 min)

Tabela de referência (rodar cada um ao vivo):

| Objetivo | Comando |
|----------|---------|
| Build da imagem | `docker build -t screenflix:latest .` |
| Subir stack (background) | `docker compose up -d` |
| Subir com rebuild | `docker compose up --build` |
| Ver serviços/estado | `docker compose ps` |
| Logs (seguir) | `docker compose logs -f api` |
| Shell dentro do container | `docker compose exec api bash` |
| Rodar comando pontual | `docker compose exec db psql -U screenflix -d screenflix` |
| Parar tudo | `docker compose down` |
| Parar e apagar volumes | `docker compose down -v` |
| Ver uso de recursos | `docker stats` |
| Limpar imagens órfãs | `docker image prune` |

**Comparação didática — rodar a app SEM Docker** (para o participante sentir a diferença):
```bash
uv sync --dev
uv run uvicorn screenflix.main:app --reload --reload-dir src --host 0.0.0.0 --port 8000
```
Discutir: aqui você precisa do Python 3.13 e de um Postgres acessível na máquina. No compose, tudo já vem junto.

**Verificando o healthcheck do container:**
```bash
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

---

## Bloco 5 — Hands-on: criar um Makefile (70–88 min)

> **Observação:** o repositório **ainda não tem um Makefile**. Este é o exercício
> central do dia — encapsular os comandos repetitivos em alvos (`targets`) claros.
> As fontes canônicas dos comandos são o `AI-CONFIG.json` (seção `runbooks`) e o
> `agents/devops-guidelines.md`.

**Motivação:** ninguém decora `uv run uvicorn screenflix.main:app --reload --reload-dir src --host 0.0.0.0 --port 8000`. Com Makefile, vira `make dev`.

**Exercício — criar `Makefile` na raiz** (construir junto com a turma):

```makefile
.PHONY: help install dev run up up-build down logs ps shell db-shell \
        format lint type test check build clean

help:            ## Lista os alvos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:         ## Instala dependências (incluindo dev)
	uv sync --dev

dev:             ## Roda a API localmente com hot-reload
	uv run uvicorn screenflix.main:app --reload --reload-dir src --host 0.0.0.0 --port 8000

up:              ## Sobe o stack em background
	docker compose up -d

up-build:        ## Sobe o stack reconstruindo as imagens
	docker compose up --build

down:            ## Derruba o stack
	docker compose down

logs:            ## Segue os logs do serviço api
	docker compose logs -f api

ps:              ## Estado dos serviços
	docker compose ps

db-shell:        ## Abre o psql no banco
	docker compose exec db psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

format:          ## Formata o código
	uv run ruff format .

lint:            ## Lint
	uv run ruff check .

type:            ## Checagem de tipos
	uv run mypy src

test:            ## Testes
	uv run pytest

check: format lint type test   ## Roda todos os quality gates (bloqueantes)

build:           ## Build da imagem de produção
	docker build -t screenflix:latest .

clean:           ## Remove containers, volumes e imagens órfãs
	docker compose down -v
	docker image prune -f
```

**Testar ao vivo:**
```bash
make help
make up
make check      # espelha os quality gates do AI-CONFIG.json
```

**Discussão — por que Makefile importa:**
- **Interface única** — dev, CI e IA (Dia 3) usam os mesmos alvos.
- **Documentação executável** — `make help` mostra o que o projeto sabe fazer.
- **Alinhamento com os gates** — `make check` reflete exatamente as `quality_checks.commands` do `AI-CONFIG.json` (`ruff format`, `ruff check`, `mypy src`, `pytest`), que são **bloqueantes** no fluxo do projeto.

> **Detalhe técnico do Make:** variáveis de shell precisam de `$$` (ex.: `$${POSTGRES_USER}`)
> para não serem interpoladas pelo Make. Bom ponto de armadilha para comentar.

---

## Bloco 6 — Fechamento e gancho (88–90 min)

**Resumo do dia:**
- Container = ambiente reproduzível; **Dockerfile multi-stage** entrega imagem enxuta, non-root e com healthcheck.
- **docker-compose** orquestra app + banco + cache; `init.sql` faz o bootstrap do schema.
- **Makefile** padroniza os comandos e espelha os quality gates.

**Gancho para o Dia 2:** "Hoje empacotamos a aplicação. Amanhã vamos *abrir a caixa*
e ver **como o código está organizado por dentro** — ambientes modulares e Clean
Architecture — usando o mesmo ScreenFlix."

---

## 📌 Apêndice — o que existe hoje vs. o que criamos em sala

| Item | Estado no repo | Ação no workshop |
|------|----------------|------------------|
| `Dockerfile` | ✅ Existe (multi-stage, non-root, healthcheck) | Dissecar |
| `docker-compose.yml` | ⚠️ Só `db` ativo; `api`/`redis` comentados | Ativar ao vivo |
| `scripts/init.sql` | ✅ Existe (tabelas `media`/`episode`) | Mostrar bootstrap |
| `.env` | ❌ Não versionado (`.gitignore`) | Criar em sala |
| **Makefile** | ❌ **Não existe** | **Criar como hands-on** |
| Volume persistente do db | ⚠️ Comentado no compose | Discutir persistência |
| CI (`.github/workflows`) | ❌ Não existe | Mencionar (gancho futuro) |
