# Dia 2 — Programação Pragmática

> **Duração:** 90 min · **Tema:** Ambientes modulares e Clean Architecture
> **Repositório de referência:** ScreenFlix (backend FastAPI + frontend Vue 3)

---

## 🎯 Objetivos de aprendizagem

Ao final do dia, o participante será capaz de:

1. Configurar **ambientes modulares** com `pydantic-settings` + `.env` (backend) e
   variáveis de build do Vite (frontend), sem hardcode.
2. Identificar as **camadas da Clean Architecture** (domain, application, infrastructure, presentation) em um projeto real.
3. Explicar a **regra de dependência** (dependências apontam para dentro) e detectar violações.
4. Reconhecer os padrões: **BaseRepository genérico**, **services**, **use cases**, **adapters** e **injeção de dependência** via FastAPI `Depends`.
5. Discutir os **trade-offs pragmáticos** que o ScreenFlix fez (e onde a pureza foi flexibilizada).

## ✅ Pré-requisitos

- Stack do Dia 1 funcionando (`docker compose up` sobe o banco).
- `uv sync --dev` executado.
- Node.js 20+ para rodar o frontend.
- Projeto aberto no editor para navegar entre as pastas de `src/screenflix/`.

---

## 🕐 Cronograma (90 min)

| Bloco | Tempo | Conteúdo |
|-------|-------|----------|
| 1 | 0–8 min | O que é "programação pragmática" e por que arquitetura importa |
| 2 | 8–28 min | Ambientes modulares: settings, `.env`, config do frontend |
| 3 | 28–40 min | O mapa das camadas: `core/` vs `modules/catalog/` |
| 4 | 40–68 min | Clean Architecture em detalhe (domain → application → infra → presentation) |
| 5 | 68–82 min | **Hands-on:** rastrear um request de ponta a ponta / adicionar um endpoint |
| 6 | 82–90 min | Trade-offs pragmáticos e gancho para o Dia 3 |

---

## Bloco 1 — Programação pragmática (0–8 min)

**Tese do dia:** arquitetura não é enfeite — ela existe para tornar a mudança
**barata e segura**. "Pragmática" significa aplicar princípios (Clean Architecture,
modularidade) **na medida certa**, sem dogmatismo.

O ScreenFlix se descreve, no `AI-CONFIG.json`, como:
```json
"architecture": "modular_monolith_layered"
```
Um **monólito modular em camadas**: um único deploy (simples de operar), mas
internamente organizado em módulos e camadas (fácil de evoluir). É o ponto ideal
para a maioria dos times antes de partir para microsserviços.

---

## Bloco 2 — Ambientes modulares (8–28 min)

"Ambiente modular" = a aplicação **não sabe** em qual ambiente roda; ela apenas lê
configuração de fora. Isso permite o mesmo binário/imagem rodar em dev, teste e prod.

### 2.1 Backend — `pydantic-settings`

**Arquivo:** [`src/screenflix/core/settings.py`](../../src/screenflix/core/settings.py)

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SCREENFLIX_",
        env_file=".env",
        extra="ignore",
    )
    app_name: str                 # obrigatório (sem default)
    app_version: str = '0.1.0'    # com default
    log_level: str = 'INFO'
    database_url: str             # obrigatório
    database_echo: bool = False
    openai_api_url: str = 'https://api.openai.com/v1'
    openai_api_key: str           # obrigatório
    openai_model: str = 'gpt-4o-mini'
    omdb_api_url: str = 'http://www.omdbapi.com'
    omdb_api_key: str             # obrigatório

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()    # carregado uma vez, cacheado
    return _settings
```

**Conceitos a extrair:**

- **Prefixo `SCREENFLIX_`** — toda config vem de `SCREENFLIX_*` no ambiente/`.env`
  (ex.: `SCREENFLIX_DATABASE_URL`). Evita colisão de nomes.
- **Tipagem forte** — `database_echo: bool`, `openai_model: str`. Pydantic **valida e
  converte** na inicialização; erro de config = falha imediata (fail fast), não bug em runtime.
- **Obrigatório vs default** — campos sem valor default (`app_name`, `database_url`,
  `openai_api_key`, `omdb_api_key`) tornam a app **impossível de subir mal configurada**.
- **Singleton cacheado** — `get_settings()` garante uma única leitura.
- **Segurança** — segredos **nunca** no código; vêm do ambiente. O `.env` está no
  `.gitignore`. Isso é reforçado no `agents/security-check.md`.

> **Demonstração ao vivo:** apagar `SCREENFLIX_DATABASE_URL` do `.env` e tentar subir
> a app → ver o erro de validação do Pydantic. Config inválida falha na hora.

**Como os ambientes se diferenciam hoje (ponto de discussão honesto):**
o ScreenFlix **não** tem módulos `settings/dev.py`, `prod.py`, `test.py`. A
diferenciação acontece via:
- valores diferentes no `.env` por ambiente;
- o `log_level` alternando **console renderer** (dev) vs **JSON renderer** (prod) no
  [`core/logging/config.py`](../../src/screenflix/core/logging/config.py);
- **stages do Docker** (Dia 1) e **testcontainers** para o ambiente de teste
  (declarado no `pyproject.toml`).

Esse é um bom "estado *antes*" para discutir: *quando* vale a pena introduzir perfis
explícitos de settings? (Resposta pragmática: quando a divergência entre ambientes
cresce além de valores de env.)

### 2.2 Frontend — configuração por variável de build (Vite)

**Arquivo:** [`frontend/src/api/screenflix.js`](../../frontend/src/api/screenflix.js)

```js
export const API_BASE = import.meta.env.VITE_API_BASE || "";
```

O mesmo princípio no frontend: a URL da API vem de `VITE_API_BASE` (definida em
`.env` / `.env.example`). Detalhe elegante: **se estiver vazia, o app entra em
"Modo demonstração"** (offline) — a store [`frontend/src/stores/catalog.js`](../../frontend/src/stores/catalog.js)
detecta isso e marca `apiState = "offline"` sem quebrar a UI.

**Discussão:** backend e frontend compartilham a mesma filosofia — **configuração
injetada de fora, com fallback seguro**. Isso é modularidade de ambiente na prática.

---

## Bloco 3 — O mapa das camadas (28–40 min)

**Arquitetura geral:** um pacote `src/screenflix/` dividido em dois grandes blocos:

```
src/screenflix/
├── main.py            # entrypoint FastAPI (monta middleware, router, /healthz)
├── core/              # 🔧 preocupações transversais (compartilhadas por todos os módulos)
│   ├── settings.py         # configuração (pydantic-settings)
│   ├── database.py         # engine/session async, Base, mixins
│   ├── repository.py       # BaseRepository[T] genérico
│   ├── app/                # dependencies (DI) + middlewares
│   ├── logging/            # structlog: config, context (trace_id), logger
│   └── utils/              # shortcuts (ex.: loader de schemas.json)
└── modules/           # 📦 módulos de negócio (bounded contexts)
    └── catalog/            # o módulo de catálogo (único hoje)
        ├── domain/              # camada 1 — entidades
        ├── application/         # camada 2 — services, use cases, schemas (DTOs)
        ├── infrastructure/      # camada 3 — repositórios (persistência)
        ├── adapters/            # integrações externas (OMDb, OpenAI, HTTP base)
        └── presentation/        # camada 4 — API HTTP (FastAPI)
```

**Duas ideias-chave:**

1. **`core/` vs `modules/`** — o que é framework/infra compartilhada fica em `core/`;
   o que é regra de negócio fica em `modules/<contexto>/`. O `agents/architecture-planning.md`
   diz: *"Shared utilities belong in `core`, not feature modules."*
2. **Monólito modular** — para adicionar um novo contexto (ex.: `users`, `billing`),
   replica-se a estrutura de camadas dentro de `modules/users/`. O padrão é
   **repetível e previsível**.

> **Demonstração:** abrir o [`main.py`](../../src/screenflix/main.py) e mostrar como
> ele é fino — só monta logging, CORS, middleware e o router do catálogo sob `/api/v1`.
> Toda a lógica está nos módulos.

---

## Bloco 4 — Clean Architecture em detalhe (40–68 min)

Percorra as 4 camadas **de dentro para fora**, seguindo o fluxo real de um request.

### Camada 1 — Domain (entidades)

**Pasta:** `modules/catalog/domain/entities/` — [`media.py`](../../src/screenflix/modules/catalog/domain/entities/media.py), [`episode.py`](../../src/screenflix/modules/catalog/domain/entities/episode.py)

- `Media` e `Episode` são as entidades centrais; `MediaType(StrEnum)` = `movie`/`series`.
- Usam mixins de `core/database` (`IDMixin`, `TimestampMixin` com `created_at`/`updated_at`).
- Relação `Media → Episode` com `selectin` loading (evita N+1) e
  `UniqueConstraint(media_id, season, episode)` no episódio.

> **Ponto de discussão (pragmatismo!):** as entidades **são modelos SQLAlchemy** (herdam
> `Base`). Em Clean Architecture "pura", o domínio seria independente de framework
> (POPOs). Aqui houve uma **escolha pragmática**: acoplar domínio ao ORM para reduzir
> boilerplate. Vale debater o trade-off — simplicidade agora vs. portabilidade depois.

### Camada 2 — Application (services, use cases, schemas)

**Pasta:** `modules/catalog/application/`

**(a) Services — CRUD/consulta fina.** [`media_service.py`](../../src/screenflix/modules/catalog/application/services/media_service.py):
```python
class MediaService:
    def __init__(self, session: AsyncSession):
        self.repository = RepositoryFactor(session)

    async def top_five(self, media_type: str) -> list[Media]:
        return await self.repository.media.list_all(
            limit=5, media_type=media_type, order_by="rating", desc=True
        )
```

**(b) Use cases — orquestração de fluxos multi-passo.** [`register_data_workflow.py`](../../src/screenflix/modules/catalog/application/use_cases/register_data_workflow.py):
o `RegisterDataWorkflow.execute()` coordena um fluxo rico:
1. Busca a mídia na **OMDb** (adapter).
2. Normaliza/enriquece via **OpenAI** (adapter), com `asyncio.Semaphore(3)` limitando concorrência.
3. Persiste `Media`, depois os `Episode`s em paralelo (`asyncio.gather`), deduplicando.
4. `commit()` — ou `rollback()` + `logger.exception()` em caso de erro (transação única).

**(c) Schemas (DTOs) — Pydantic.** `application/schemas/` separa os contratos de
API (`MediaBaseSchema`, `MediaSchema`, `EpisodeSchema`, `RegisterBody`) das entidades
de domínio. **Nunca** exponha a entidade direto: o DTO é a fronteira do contrato.

> **Distinção didática — service vs use case:** *service* = operação simples e
> reutilizável (listar, contar); *use case* = **orquestração** de um objetivo de
> negócio ("registrar uma mídia") envolvendo vários adapters e transação.

### Camada 3 — Infrastructure (repositórios)

**Pasta:** `modules/catalog/infrastructure/repositories/`

O padrão **Repository** isola o acesso a dados. Base genérica em
[`core/repository.py`](../../src/screenflix/core/repository.py):
```python
class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> T | None: ...
    async def list_all(self, skip=0, limit=50, order_by=None, desc=False, **filters) -> list[T]: ...
    async def count(self, **filters) -> int: ...
```

Repositórios concretos só adicionam consultas específicas:
```python
class MediaRepository(BaseRepository[Media]): pass

class EpisodeRepository(BaseRepository[Episode]):
    async def get_by_media_and_season_and_episode(self, media_id, season, episode):
        ...  # consulta de domínio específica
```

E o `RepositoryFactor` agrega os repositórios que um service precisa:
```python
class RepositoryFactor:
    def __init__(self, session: AsyncSession):
        self.media = MediaRepository(session, Media)
        self.episode = EpisodeRepository(session, Episode)
```

**Regra do `agents/database-development.md`:** *"Do not query DB directly from
presentation layer."* Nunca um endpoint fala com o banco — sempre passa por service → repository.

### Camada 4 — Presentation (API HTTP) + Injeção de Dependência

**Pasta:** `modules/catalog/presentation/api/v1/`

O endpoint é **fino** — valida entrada, delega, devolve. [`enpoints/media.py`](../../src/screenflix/modules/catalog/presentation/api/v1/enpoints/media.py):
```python
async def get_media_service(session: AsyncSession = Depends(get_db_session)) -> MediaService:
    return MediaService(session)

@router.get("/movies/top5", response_model=list[MediaBaseSchema])
async def list_top_five_movies(service: MediaService = Depends(get_media_service)):
    return await service.top_five(media_type="movie")
```

A **injeção de dependência** encadeia: `get_db_session` (abre/fecha a sessão async
via `async with`) → `get_media_service` (constrói o service) → endpoint. Definido em
[`core/app/dependencies.py`](../../src/screenflix/core/app/dependencies.py):
```python
async def get_db_session():
    session_maker = get_session_maker()
    async with session_maker() as session:
        yield session
```

O `response_model=` do FastAPI garante que a saída **sempre** obedece ao schema —
o contrato da API é validado automaticamente.

### A regra de dependência (o coração da Clean Architecture)

As dependências apontam **para dentro**:

```
presentation ──▶ application ──▶ domain
                     │
infrastructure ──────┘ (depende de domain + core)
adapters ────────────▶ core.settings / domain
```

Do `agents/architecture-planning.md` (e `CONTRIBUTING.md`):
- `domain` **não** importa `presentation`.
- `presentation` **não** implementa regra de negócio (só transporte HTTP).
- `application` coordena domain + adapters/repositories.
- `infrastructure`/`adapters` podem depender de `core`, **nunca** de `presentation`.

> **Demonstração ao vivo:** pedir à turma para prever "onde eu colocaria uma nova
> regra de negócio?" e "onde uma nova query?" — reforçando o mapa mental por camada.

---

## Bloco 5 — Hands-on (68–82 min)

Escolha **um** dos dois exercícios conforme o ritmo da turma:

### Opção A (rastreio) — request de ponta a ponta

Rastrear `GET /api/v1/media/movies/top5` percorrendo as camadas:

1. **Presentation** — `enpoints/media.py::list_top_five_movies`
2. **DI** — `get_media_service` → `get_db_session`
3. **Application** — `MediaService.top_five("movie")`
4. **Infrastructure** — `RepositoryFactor.media.list_all(order_by="rating", desc=True, limit=5)`
5. **Domain/DB** — entidade `Media`, tabela `media`
6. **Saída** — serializada por `response_model=list[MediaBaseSchema]`

Rodar de verdade:
```bash
docker compose up -d
curl -s http://localhost:8000/api/v1/media/movies/top5 | jq
```

### Opção B (construção) — adicionar um endpoint respeitando as camadas

Adicionar `GET /api/v1/media/count` que retorna a contagem de mídias:

1. **Application** — método `count()` no `MediaService` usando `self.repository.media.count()`.
2. **Presentation** — novo handler em `enpoints/media.py` delegando ao service.
3. **Contrato** — retornar um DTO Pydantic (ex.: `{"total": int}`).
4. **Teste** — seguindo a política do `agents/qa-guidelines.md`: happy path + erro.

Validar com os quality gates:
```bash
make check     # ou: uv run ruff check . && uv run mypy src && uv run pytest
```

> **Regra de ouro do exercício:** *nenhuma consulta ao banco no endpoint*. Se a turma
> tentar chamar o repository direto da camada de apresentação, é o gancho perfeito para
> reforçar a regra de dependência.

---

## Bloco 6 — Trade-offs pragmáticos e gancho (82–90 min)

**Onde o ScreenFlix escolheu pragmatismo sobre pureza (ótimos pontos de debate):**

1. **Entidades = modelos ORM** — acopla domínio ao SQLAlchemy; troca portabilidade por simplicidade.
2. **`RepositoryFactor` concreto** — services instanciam repositórios concretos, sem
   interface/inversão no boundary de persistência. Simples, mas difícil de trocar a persistência.
3. **`register` como *fire-and-forget*** — o endpoint dispara `asyncio.create_task` e
   responde na hora (`"Media registration initiated"`). Sem uma fila durável (Celery/RQ),
   o trabalho se perde se o processo cair. O `agents/backend-development.md` reconhece
   isso explicitamente como dívida consciente.
4. **Top 5 no frontend** — embora existam endpoints `/top5`, a HomeView calcula o Top 5
   no cliente ordenando as listas. Pragmatismo do front, mas duplica lógica.

**Mensagem final:** Clean Architecture é um **espectro**, não um checklist. O valor está
em **camadas com responsabilidades claras e dependências controladas** — e em saber,
conscientemente, *onde* relaxar.

**Gancho para o Dia 3:** "Repararam que o repositório tem uma pasta `agents/` e um
`AGENTS.md`? O time codificou todas essas regras de arquitetura em **contexto para IA**.
Amanhã veremos como o Claude Code usa esse tipo de contexto — com **Skills**, **subagents**
e **times de agentes** — para desenvolver respeitando exatamente estas camadas."

---

## 📌 Apêndice — arquivos-chave do dia

| Camada / tema | Arquivo |
|---------------|---------|
| Settings (ambiente) | `src/screenflix/core/settings.py` |
| Config do frontend | `frontend/src/api/screenflix.js`, `frontend/.env.example` |
| Entrypoint | `src/screenflix/main.py` |
| Domain | `src/screenflix/modules/catalog/domain/entities/` |
| Service | `src/screenflix/modules/catalog/application/services/media_service.py` |
| Use case | `src/screenflix/modules/catalog/application/use_cases/register_data_workflow.py` |
| Repository base | `src/screenflix/core/repository.py` |
| Endpoint + DI | `src/screenflix/modules/catalog/presentation/api/v1/enpoints/media.py` |
| DI da sessão | `src/screenflix/core/app/dependencies.py` |
| Regras de arquitetura | `agents/architecture-planning.md`, `CONTRIBUTING.md` |

> **Curiosidade para citar:** a pasta de endpoints está escrita `enpoints/` (sem o "d").
> Bom lembrete de que padrões de nomenclatura consistentes importam — e de que
> ninguém é perfeito. 🙂
