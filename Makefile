
# ══════════════════════════════════════════════════════════════
# ScreenFlix — Makefile
# ══════════════════════════════════════════════════════════════

# Usa bash e falha cedo em erros de pipeline
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

COMPOSE := docker compose
FRONTEND_DIR := frontend

.DEFAULT_GOAL := help

# ── Help ────────────────────────────────────────────────────
.PHONY: help
help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Setup ───────────────────────────────────────────────────
.PHONY: install
install: ## Instala as dependências Python (incl. dev) via uv
	uv sync

.PHONY: lock
lock: ## Atualiza o uv.lock a partir do pyproject.toml
	uv lock

# ── Dev ─────────────────────────────────────────────────────
.PHONY: dev
dev: ## Sobe a API localmente com reload (uvicorn)
	uv run uvicorn screenflix.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir src

.PHONY: shell
shell: ## Abre um shell Python no ambiente do projeto
	uv run python

# ── Qualidade ───────────────────────────────────────────────
.PHONY: lint
lint: ## Roda o linter (ruff check)
	uv run ruff check src tests

.PHONY: format
format: ## Formata o código e corrige o que o linter puder (ruff)
	uv run ruff format src tests
	uv run ruff check --fix src tests

.PHONY: format-check
format-check: ## Verifica formatação sem alterar arquivos
	uv run ruff format --check src tests

.PHONY: typecheck
typecheck: ## Roda a checagem de tipos (mypy)
	uv run mypy src

.PHONY: test
test: ## Roda toda a suíte de testes
	uv run pytest

.PHONY: test-unit
test-unit: ## Roda apenas os testes unitários (exclui integration)
	uv run pytest -m "not integration"

.PHONY: test-integration
test-integration: ## Roda apenas os testes de integração (containers)
	uv run pytest -m integration

.PHONY: check
check: lint typecheck test ## Roda lint + typecheck + testes (CI local)

# ── Docker ──────────────────────────────────────────────────
.PHONY: up
up: ## Sobe todos os serviços em background (docker compose)
	$(COMPOSE) up -d

.PHONY: up-build
up-build: ## Sobe os serviços reconstruindo as imagens
	$(COMPOSE) up -d --build

.PHONY: down
down: ## Derruba os serviços
	$(COMPOSE) down

.PHONY: build
build: ## Constrói as imagens dos serviços
	$(COMPOSE) build

.PHONY: logs
logs: ## Segue os logs dos serviços
	$(COMPOSE) logs -f

.PHONY: ps
ps: ## Lista o status dos serviços
	$(COMPOSE) ps

.PHONY: restart
restart: ## Reinicia os serviços
	$(COMPOSE) restart

# ── Frontend ────────────────────────────────────────────────
.PHONY: front-install
front-install: ## Instala as dependências do frontend
	cd $(FRONTEND_DIR) && npm install

.PHONY: front-dev
front-dev: ## Sobe o frontend em modo dev (Vite)
	cd $(FRONTEND_DIR) && npm run dev

.PHONY: front-build
front-build: ## Gera o build de produção do frontend
	cd $(FRONTEND_DIR) && npm run build

.PHONY: front-preview
front-preview: ## Serve o build de produção do frontend
	cd $(FRONTEND_DIR) && npm run preview

# ── Limpeza ─────────────────────────────────────────────────
.PHONY: clean
clean: ## Remove caches (pytest, mypy, ruff, __pycache__)
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -not -path './.venv/*' -not -path './frontend/*' -exec rm -rf {} +
