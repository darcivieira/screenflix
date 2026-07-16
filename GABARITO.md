# Gabarito dos hands-on — Workshop ScreenFlix

Esta branch (`claude/screenflix-workshop-gabarito`) parte da `master` (código real) e traz
**todos os exercícios de "mão no código" já resolvidos**, para você ir copiando durante a
apresentação. Cada seção diz o arquivo e o que foi feito, na ordem em que aparece no roteiro.

> Dica: mantenha esta branch aberta num editor à parte e copie de cada arquivo conforme
> a turma tenta o exercício.

---

## Dia 1 — Infra & Containers

### ▸ Ligar a persistência do banco  → `docker-compose.yml`
Descomente o volume nomeado e o mount. Resultado já aplicado:

```yaml
volumes:
  db-data:

services:
  db:
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
```
Teste: suba, registre uma mídia, `docker compose down` (sem `-v`) e confirme que os dados sobrevivem.

### ▸ Adicionar o alvo `db-shell`  → `Makefile` (seção Docker)
```makefile
.PHONY: db-shell
db-shell: ## Abre um psql no banco (usa as credenciais do container)
	$(COMPOSE) exec db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'
```
Rode `make help` e mostre o alvo aparecendo **ordenado** (por causa do `sort`).
Ponto de armadilha: o `$$` faz o Make repassar `$` ao shell — aqui o `sh -c` resolve a
variável **dentro do container**, onde `POSTGRES_USER`/`POSTGRES_DB` existem.

---

## Dia 2 — Programação Pragmática

### ▸ Endpoint `GET /api/v1/media/count` respeitando as camadas
Quatro arquivos, uma camada de cada vez. O `BaseRepository.count()` **já existia** — o
exercício é conectar service → endpoint → DTO → teste.

**1. DTO** → `src/screenflix/modules/catalog/application/schemas/media.py`
```python
class MediaCountSchema(BaseModel):
    total: int
```

**2. Application** → `.../application/services/media_service.py`
```python
async def count(self, media_type: str | None = None) -> int:
    return await self.repository.media.count(media_type=media_type)
```

**3. Presentation** → `.../presentation/api/v1/enpoints/media.py`
```python
# IMPORTANTE: /count precisa vir ANTES de /{media_id}, senão o FastAPI
# casa "count" como se fosse um media_id e a rota nunca é alcançada.
@router.get("/count", response_model=MediaCountSchema)
async def count_media(media_type: str | None = None,
                      service: MediaService = Depends(get_media_service)):
    total = await service.count(media_type=media_type)
    return MediaCountSchema(total=total)
```
(e inclua `MediaCountSchema` no import dos schemas)

**4. Testes** → `tests/test_media_count.py` (caminho feliz, filtro/validação, ordem de rota, service).

Valide com `make check`. Regra de ouro: **nenhuma query no endpoint**.

---

## Dia 3 — IA no Desenvolvimento

### ▸ `CLAUDE.md`  (raiz)
Importa o contexto que já existe em vez de duplicar (`@AGENTS.md`, `@AI-CONFIG.json`, `@agents/...`).
Arquivo pronto na raiz desta branch.

### ▸ Skill `/quality-gate`  → `.claude/skills/quality-gate/SKILL.md`
Encapsula os quality gates bloqueantes. (Bônus: `.claude/skills/new-module/SKILL.md`.)

### ▸ Subagents (o "time")  → `.claude/agents/*.md`
Sete especialistas, um por guia da pasta `agents/`:
`architect` · `backend-dev` · `database-dev` · `ai-ml-dev` · `security-check` · `qa-reviewer` · `devops`.
Cada um traz `name` / `description` / `tools` / `model` e aponta para o guia-fonte.

### ▸ Hook (opcional)  → salve como `.claude/settings.json`
Este arquivo **não** vai versionado (alteraria o comportamento de quem abrir o repo).
Copie o bloco abaixo e salve como `.claude/settings.json` na hora da demo — ele roda o lint
ao encerrar uma resposta (a máquina executa, não o modelo):

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "uv run ruff check src tests" } ] }
    ]
  }
}
```

---

## Como demonstrar o "time" de subagents
Com os arquivos de `.claude/agents/` no lugar, peça algo como:
> "Adicione um endpoint `GET /media/count` com testes."

e mostre o Claude **delegando**: `backend-dev` para o código, `database-dev` para a consulta,
`qa-reviewer` para os testes — cada um carregando só o seu guia de domínio.
