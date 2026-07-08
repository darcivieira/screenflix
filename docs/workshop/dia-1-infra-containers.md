# Dia 1 — Infra & Containers

> **Duração:** 90 min · **Tema:** Docker nas aplicações, Dockerfile, docker-compose, comandos e Makefile
> **Repositório de referência:** ScreenFlix (FastAPI + PostgreSQL)

---

## 🎯 Objetivos de aprendizagem

Ao final do dia, o participante será capaz de:

1. Explicar **por que** usamos containers em aplicações modernas (paridade dev/prod, isolamento, reprodutibilidade).
2. Ler e escrever um **Dockerfile multi-stage** otimizado (imagem enxuta, non-root, healthcheck).
3. Orquestrar múltiplos serviços com **docker-compose** (app + banco).
4. Dominar os **comandos** essenciais do dia a dia (`build`, `up`, `logs`, `exec`, `down`).
5. Entender e usar o **Makefile** do projeto (e estendê-lo) para padronizar o fluxo do time.

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
| 3 | 30–50 min | docker-compose: subindo o stack (`db` + `api`) e persistência |
| 4 | 50–70 min | Comandos essenciais na prática (build, logs, exec, healthcheck) |
| 5 | 70–88 min | Makefile do projeto: ler, entender e **estender** (hands-on) |
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

**Estado atual do repo:** o compose tem **dois serviços ativos** — `db` (Postgres) e `api` (a aplicação, construída do `Dockerfile`). O volume nomeado de persistência do banco (`db-data`) ainda está **comentado** — bom gancho para o exercício de persistência mais adiante.

> **Nota histórica (bom ponto de discussão):** originalmente o compose reservava um serviço
> `redis` para cache/fila. Ele foi **removido** do projeto (serviço, volume e a dependência
> `redis[hiredis]` no `pyproject.toml`) por ainda não ter uso real — um exemplo prático de
> **YAGNI** ("You Aren't Gonna Need It"): não carregue infraestrutura que você não usa.

```yaml
services:
  db:
    image: postgres:18-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
#      - db-data:/var/lib/postgresql/data      # persistência (comentado — exercício!)
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5532:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 3

  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./src:/app/src                # bind-mount → hot-reload em dev
      - ./schemas.json:/app/schemas.json
    depends_on:
      db:
        condition: service_healthy    # espera o banco ficar saudável
    command: uvicorn screenflix.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir src
```

**Conceitos a extrair deste bloco:**

- **`image` vs `build`** — `db` usa imagem pronta; o `api` usa `build: { context: ., dockerfile: Dockerfile, target: runtime }` (reaproveita o Dockerfile do Bloco 2).
- **Variáveis de ambiente** — vêm de `${POSTGRES_USER}` e do `env_file: .env` → precisam de um `.env`.
- **Volume de bootstrap** — `./scripts/init.sql` é montado em `/docker-entrypoint-initdb.d/`, e o Postgres executa esse SQL na **primeira** inicialização. Abrir o [`scripts/init.sql`](../../scripts/init.sql) e mostrar a criação das tabelas `media` e `episode` (com índices, CHECK constraint e FK `ON DELETE CASCADE`).
- **Port mapping** — `5532:5432` (host:container) — escolhido para não conflitar com um Postgres local na 5432.
- **`healthcheck` + `depends_on ... service_healthy`** — o `api` só sobe depois que o `pg_isready` do banco passa. Ordem de subida garantida.
- **Bind-mount + `--reload`** — o `api` monta `./src` e roda com `--reload`: código editado no host recarrega no container (fluxo de dev).

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

> **Demonstração ao vivo — subir só o banco primeiro:**
> ```bash
> docker compose up -d db
> docker compose ps
> docker compose logs -f db          # ver o init.sql rodando
> docker compose exec db psql -U screenflix -d screenflix -c "\dt"   # listar tabelas
> ```

### Mini-exercício guiado: stack completo + persistência

Subir o stack completo (db + api já vêm ativos) e validar a API:

```bash
docker compose up --build
# api em :8000, db em :5532
curl http://localhost:8000/healthz
```

Depois, **habilitar a persistência do banco** (hoje desligada): descomentar
`db-data:` no topo do arquivo e a linha `- db-data:/var/lib/postgresql/data` no
serviço `db`. Subir, registrar uma mídia, `docker compose down` (sem `-v`) e
confirmar que os dados sobrevivem ao reiniciar.

**Discussão:** o serviço `api` usa `volumes: - ./src:/app/src` + `--reload` para
hot-reload em dev. Contraste: **imagem imutável (prod)** vs **bind-mount com reload
(dev)** — o mesmo Dockerfile serve aos dois modos. E sem o volume `db-data`, os dados
do Postgres vivem só dentro do container — some ao recriá-lo.

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
uv sync                # ou: make install
uv run uvicorn screenflix.main:app --reload --reload-dir src --host 0.0.0.0 --port 8000
# atalho equivalente do projeto:  make dev
```
Discutir: aqui você precisa do Python 3.13 e de um Postgres acessível na máquina. No compose, tudo já vem junto. (No Bloco 5 vemos como o `Makefile` encapsula esses comandos.)

**Verificando o healthcheck do container:**
```bash
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

---

## Bloco 5 — Makefile: ler, entender e estender (70–88 min)

> **Arquivo:** [`Makefile`](../../Makefile) — o projeto **já traz** um Makefile completo.
> O foco do bloco não é criá-lo do zero, e sim **entender por que ele existe**, dominar
> seus alvos e **estendê-lo** com um novo target.

**Motivação:** ninguém decora `uv run uvicorn screenflix.main:app --reload --reload-dir src --host 0.0.0.0 --port 8000`. Com o Makefile, vira `make dev`. O arquivo vira a **interface única** do projeto — para dev, CI e IA (Dia 3).

### Anatomia do Makefile (percorrer ao vivo)

O topo do arquivo traz configurações que valem discussão:

```makefile
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c   # falha cedo: erro em qualquer etapa aborta o alvo

COMPOSE := docker compose           # variável → um só lugar para trocar
FRONTEND_DIR := frontend

.DEFAULT_GOAL := help               # `make` sem argumento mostra a ajuda
```

O alvo `help` é **auto-documentado**: ele varre os comentários `## ...` do próprio arquivo
e imprime a lista de alvos. Por isso todo alvo tem um `## descrição`.

```makefile
help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
```

Os alvos estão organizados por seção. Mostrar os principais:

| Seção | Alvos | O que fazem |
|-------|-------|-------------|
| **Setup** | `install`, `lock` | `uv sync` · `uv lock` |
| **Dev** | `dev`, `shell` | sobe a API com reload · abre um REPL Python do projeto |
| **Qualidade** | `lint`, `format`, `format-check`, `typecheck`, `test`, `test-unit`, `test-integration`, `check` | ruff / mypy / pytest — ver abaixo |
| **Docker** | `up`, `up-build`, `down`, `build`, `logs`, `ps`, `restart` | encapsulam `docker compose ...` |
| **Frontend** | `front-install`, `front-dev`, `front-build`, `front-preview` | npm no diretório `frontend/` |
| **Limpeza** | `clean` | remove caches (`.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `__pycache__`) |

**Pontos a destacar na seção Qualidade:**

- `check: lint typecheck test` — é o **CI local**: roda lint + tipos + testes (repare que
  `format` fica de fora — formatação é um alvo à parte; para checar sem alterar arquivos há o `format-check`).
- Os testes são **fatiados pelos markers** definidos no `pyproject.toml`:
  - `test-unit` → `pytest -m "not integration"`
  - `test-integration` → `pytest -m integration`
  - Amarra direto com o Dia 1 (containers) e a estratégia de testes do `agents/qa-guidelines.md`.

**Testar ao vivo:**
```bash
make            # sem argumento → mostra o help (.DEFAULT_GOAL)
make install
make up-build   # docker compose up -d --build
make check      # lint + typecheck + test (CI local)
make front-dev  # sobe o Vite
```

**Discussão — por que Makefile importa:**
- **Interface única** — dev, CI e IA (Dia 3) usam os mesmos alvos; um comando trocado se ajusta num lugar só.
- **Documentação executável** — `make help` mostra o que o projeto sabe fazer.
- **Robustez** — `.SHELLFLAGS := -eu -o pipefail -c` faz um alvo abortar no primeiro erro, em vez de seguir mascarando falha.

### Mãos à obra — estender o Makefile

O Makefile atual **não tem** um atalho para abrir o `psql` no banco nem para logs de um
serviço específico. Adicione, na seção Docker, um alvo `db-shell`:

```makefile
.PHONY: db-shell
db-shell: ## Abre o psql no banco
	$(COMPOSE) exec db psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}
```

Rode `make help` e confirme que o novo alvo aparece **ordenado** na lista (graças ao `sort`).

> **Detalhe técnico do Make:** variáveis de shell precisam de `$$` (ex.: `$${POSTGRES_USER}`)
> para o Make não interpolá-las — quem resolve é o shell, em runtime. Bom ponto de armadilha para comentar.

**Ideias extras de extensão (se sobrar tempo):** um alvo `quality` que também rode
`format-check`; um `clean-docker` que faça `docker compose down -v` + `docker image prune -f`.

---

## Bloco 6 — Fechamento e gancho (88–90 min)

**Resumo do dia:**
- Container = ambiente reproduzível; **Dockerfile multi-stage** entrega imagem enxuta, non-root e com healthcheck.
- **docker-compose** orquestra app (`api`) + banco (`db`); `init.sql` faz o bootstrap do schema.
- O **Makefile** do projeto é a interface única (dev, qualidade, docker, frontend); `make check` é o CI local.

**Gancho para o Dia 2:** "Hoje empacotamos a aplicação. Amanhã vamos *abrir a caixa*
e ver **como o código está organizado por dentro** — ambientes modulares e Clean
Architecture — usando o mesmo ScreenFlix."

---

## 📌 Apêndice — o que existe hoje vs. o que criamos em sala

| Item | Estado no repo | Ação no workshop |
|------|----------------|------------------|
| `Dockerfile` | ✅ Existe (multi-stage, non-root, healthcheck) | Dissecar |
| `docker-compose.yml` | ✅ `db` + `api` ativos; `redis` removido (YAGNI); volume `db-data` comentado | Subir stack; ligar persistência |
| `scripts/init.sql` | ✅ Existe (tabelas `media`/`episode`) | Mostrar bootstrap |
| `.env` | ❌ Não versionado (`.gitignore`) | Criar em sala |
| **Makefile** | ✅ Existe (rico: setup, dev, qualidade, docker, frontend, limpeza) | Ler, usar e **estender** (add `db-shell`) |
| Volume persistente do db | ⚠️ Comentado no compose | Discutir persistência |
| CI (`.github/workflows`) | ❌ Não existe | Mencionar (gancho futuro) |
