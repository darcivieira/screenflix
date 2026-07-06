# Dia 3 — IA no Desenvolvimento

> **Duração:** 90 min · **Tema:** Claude Code, Skills, Subagents e Agent Teams
> **Repositório de referência:** ScreenFlix (que já possui uma camada de contexto para IA)
> **Formatos válidos para:** Claude Code v2.1.x (jul/2026)

---

## 🎯 Objetivos de aprendizagem

Ao final do dia, o participante será capaz de:

1. Entender o que é o **Claude Code** e como ele usa **contexto de projeto** (`CLAUDE.md`).
2. Ligar a camada de contexto **genérica** que o ScreenFlix já tem (`AGENTS.md`, `AI-CONFIG.json`, `/agents`) aos recursos **nativos** do Claude Code.
3. Criar **Skills** (`.claude/skills/*/SKILL.md`) que encapsulam procedimentos do projeto (ex.: quality gate).
4. Criar **Subagents** (`.claude/agents/*.md`) especializados por domínio, traduzindo os guias de `/agents/`.
5. Compreender o conceito de **Agent Teams** (orquestração multi-agente) e quando usá-lo.

## ✅ Pré-requisitos

- **Claude Code CLI** instalado e autenticado (`claude`).
- Repositório ScreenFlix aberto; Dias 1 e 2 concluídos (o participante já conhece a arquitetura).
- Familiaridade com o conteúdo de `AGENTS.md` e da pasta `agents/` (revisado no fim do Dia 2).

---

## 🕐 Cronograma (90 min)

| Bloco | Tempo | Conteúdo |
|-------|-------|----------|
| 1 | 0–10 min | O que é Claude Code + o "insight" do ScreenFlix |
| 2 | 10–25 min | `CLAUDE.md`: ligando o contexto existente (`AGENTS.md`, `/agents`) |
| 3 | 25–45 min | **Skills:** encapsulando procedimentos do projeto |
| 4 | 45–70 min | **Subagents:** traduzindo `/agents/*.md` em especialistas reais |
| 5 | 70–85 min | **Agent Teams:** orquestração multi-agente (experimental) |
| 6 | 85–90 min | Síntese dos 3 dias e próximos passos |

---

## Bloco 1 — Claude Code e o insight do ScreenFlix (0–10 min)

**O que é o Claude Code?** Um agente de desenvolvimento que roda no terminal (e integra
com IDEs). Ele lê o seu repositório, executa comandos, edita arquivos e segue o **contexto**
e as **regras** que você define — respeitando permissões.

**O insight que torna este repositório especial:** o ScreenFlix **já foi construído
pensando em IA**. Abra o [`AGENTS.md`](../../AGENTS.md):

> *"This file is the root entry point for machine and human contributors using
> AI-assisted workflows. It explains how `/agents` must be used as the canonical
> engineering context layer for this repository."*

E o [`AI-CONFIG.json`](../../AI-CONFIG.json) declara explicitamente vários **consumidores** de IA:
```json
"consumers": {
  "codex_cli":  {"enabled": true, "mode": "write_and_validate"},
  "cursor":     {"enabled": true, "mode": "assist_with_context"},
  "mcp_agents": {"enabled": true, "mode": "context_first"},
  "ci_bots":    {"enabled": true, "mode": "check_and_comment"}
}
```

**A grande sacada do dia:** essa camada de contexto é **genérica e agnóstica de
ferramenta** (Markdown + JSON). O Claude Code **não lê `AGENTS.md` automaticamente**.
Então o trabalho de hoje é **traduzir** esse contexto genérico em artefatos **nativos**
do Claude Code:

| Contexto genérico do repo | Artefato nativo do Claude Code |
|---------------------------|-------------------------------|
| `AGENTS.md` (ponto de entrada) | `CLAUDE.md` (memória de projeto) |
| `AI-CONFIG.json → quality_checks` | **Skill** `/quality-gate` + **Hook** |
| `agents/backend-development.md` | **Subagent** `backend-dev` |
| `agents/qa-guidelines.md` | **Subagent** `qa-reviewer` |
| `agents/security-check.md` | **Subagent** `security-check` |
| `agents/architecture-planning.md` | **Subagent** `architect` |
| conjunto de subagents atuando junto | **Agent Team** |

---

## Bloco 2 — CLAUDE.md: ligando o contexto existente (10–25 min)

**O que é o `CLAUDE.md`?** Um arquivo que o Claude Code lê **no início de toda sessão**.
Contém instruções persistentes: convenções, comandos de build, padrões. Sobrevive a
`/compact` (é relido do disco).

**Localizações (mencionar ambas):**
- **Projeto (versionado, compartilhado):** `./CLAUDE.md` ou `./.claude/CLAUDE.md`
- **Usuário (sua máquina, todos os projetos):** `~/.claude/CLAUDE.md`
- **Local pessoal (não versionado):** `./CLAUDE.local.md` (colocar no `.gitignore`)

**Ponto crucial:** o Claude Code lê **`CLAUDE.md`**, e **não** `AGENTS.md`. Como o
ScreenFlix já investiu num `AGENTS.md` e numa pasta `/agents` rica, a jogada certa é
**importar**, não duplicar.

**Exercício ao vivo — criar `CLAUDE.md` na raiz** que reaproveita o que já existe:

```markdown
# ScreenFlix — Contexto para Claude Code

Este projeto já mantém uma camada de contexto de engenharia. Carregue-a:

@AGENTS.md
@AI-CONFIG.json
@agents/architecture-planning.md

## Regras rápidas
- Arquitetura: monólito modular em camadas (domain → application → infra → presentation).
  Nunca acesse o banco a partir da camada de presentation.
- Sempre rode os quality gates antes de concluir uma mudança:
  `uv run ruff format . && uv run ruff check . && uv run mypy src && uv run pytest`
- Todo componente novo (endpoint, use case, repository, adapter) exige testes unitários
  no mesmo PR (happy path, validação e erro) — ver agents/qa-guidelines.md.
- Segredos vêm sempre do ambiente (SCREENFLIX_*). Nunca commite .env.

## Comandos
- Dev local: `uv run uvicorn screenflix.main:app --reload --reload-dir src --port 8000`
- Stack completo: `docker compose up --build`
```

O `@AGENTS.md` faz o Claude Code **puxar** o arquivo existente para o contexto —
reaproveitando todo o trabalho do time. (Alternativa: `ln -s AGENTS.md CLAUDE.md`.)

> **Demonstração:** iniciar `claude` na raiz e pedir *"Onde eu adicionaria um endpoint
> para listar mídias por gênero?"*. Com o `CLAUDE.md` carregando o contexto de camadas,
> o Claude responde respeitando a arquitetura (application → presentation), sem sugerir
> query no endpoint.

---

## Bloco 3 — Skills: encapsulando procedimentos (25–45 min)

**O que é uma Skill?** Um procedimento reutilizável que **enriquece a conversa principal**
e é carregado **sob demanda** (lazy loading — economiza contexto). Vira um comando
`/nome-da-skill`. O Claude pode invocá-la sozinho (se `invocation: auto`) ou você chama
manualmente.

**Localização:**
- **Projeto:** `.claude/skills/<nome>/SKILL.md`
- **Usuário:** `~/.claude/skills/<nome>/SKILL.md`

**Frontmatter principal:** `name`, `description` (obrigatórios); opcionais `invocation`
(`manual`/`auto`/`both`), `context` (`main`/`fork`), `tools`.

### Exercício 1 — Skill de quality gate

Os `quality_checks.commands` do `AI-CONFIG.json` são **bloqueantes**. Vamos transformá-los
em uma Skill. Criar `.claude/skills/quality-gate/SKILL.md`:

```markdown
---
name: quality-gate
description: Roda os quality gates bloqueantes do ScreenFlix (format, lint, types, testes). Use antes de concluir qualquer mudança de código.
invocation: both
---

Execute, nesta ordem, e pare no primeiro que falhar, reportando a saída:

1. `uv run ruff format .`
2. `uv run ruff check .`
3. `uv run mypy src`
4. `uv run pytest`

Se algum passo falhar, resuma o erro e proponha a correção mínima antes de repetir.
Não considere a tarefa concluída enquanto os quatro passos não passarem.
```

Agora, em vez de decorar 4 comandos, o dev (ou o próprio Claude) usa `/quality-gate`.

### Exercício 2 (opcional) — Skill de scaffolding de módulo

Uma Skill que gera o esqueleto de camadas de um novo módulo (Clean Architecture do
Dia 2). `.claude/skills/new-module/SKILL.md`:

```markdown
---
name: new-module
description: Cria o esqueleto de um novo módulo de negócio seguindo a Clean Architecture do ScreenFlix (domain, application, infrastructure, presentation).
invocation: manual
---

Dado o nome de um módulo <nome>, crie em src/screenflix/modules/<nome>/ as pastas e
__init__.py replicando o padrão de modules/catalog/:
- domain/entities/
- application/{schemas,services,use_cases}/
- infrastructure/repositories/
- adapters/
- presentation/api/v1/endpoints/  (atenção: use "endpoints" corretamente)

Respeite a regra de dependência (presentation → application → domain) e registre o
router em presentation/api/v1/router.py. Não implemente lógica de negócio — só o esqueleto.
```

**Skill vs Subagent (conceito-chave a fixar):**
- **Skill** = procedimento/comando que roda **na conversa principal**, carregado sob demanda.
- **Subagent** = trabalhador **isolado**, com contexto próprio e sistema/ferramentas
  próprios; começa "do zero" e devolve um resultado.

> **Hook (menção rápida):** para *forçar* o quality gate automaticamente, dá para
> configurar um **hook** em `.claude/settings.json` no evento `Stop`:
> ```json
> { "hooks": { "Stop": [ { "hooks": [ { "type": "command", "command": "uv run ruff check ." } ] } ] } }
> ```
> Hooks são a forma de tornar comportamentos **automáticos** (a máquina executa, não o modelo).

---

## Bloco 4 — Subagents: traduzindo `/agents/*.md` em especialistas (45–70 min)

Este é o coração do dia. O ScreenFlix tem, em `/agents/`, **7 guias de domínio**
(backend, database, ai-ml, security, devops, qa, architecture). Eles são **documentos**.
Vamos convertê-los em **subagents reais** do Claude Code.

**O que é um Subagent?** Um agente especializado com **contexto próprio**, sistema
próprio e **ferramentas restritas**. O Claude principal **delega** tarefas a ele com base
na `description`. Roda isolado e reporta de volta.

**Localização:**
- **Projeto:** `.claude/agents/<nome>.md`
- **Usuário:** `~/.claude/agents/<nome>.md`

**Frontmatter:** `name`, `description` (obrigatórios — a `description` é o que o Claude
usa para decidir delegar); opcionais `tools`, `model`, `permissionMode`, etc.

**Invocação:** automática (match de descrição), por `@agent-<nome>`, ou linguagem natural.

### Exercício — criar o subagent `qa-reviewer`

Traduzindo o [`agents/qa-guidelines.md`](../../agents/qa-guidelines.md). Criar
`.claude/agents/qa-reviewer.md`:

```markdown
---
name: qa-reviewer
description: Revisor de QA do ScreenFlix. Use após escrever ou alterar código para verificar cobertura de testes e política de componentes. Bloqueia mudanças sem testes.
tools: Read, Grep, Glob, Bash
model: sonnet
---

Você é o revisor de QA do ScreenFlix. Sua fonte de verdade é agents/qa-guidelines.md.

Ao revisar uma mudança:
1. Identifique componentes novos (endpoint, use case, service, repository, adapter, util).
2. Exija testes unitários no mesmo change set cobrindo: happy path, validação/normalização
   e caminho de erro.
3. Verifique os thresholds: >=80% em módulos alterados, >=90% em parsing/normalização crítica.
4. Rode `uv run pytest` e reporte falhas.
5. Se faltar teste para um componente novo, marque como BLOQUEANTE e liste exatamente o
   que testar.

Seja específico e acionável. Não aprove mudanças que violem a política de testes.
```

### Modelo replicável — o "time" de subagents do ScreenFlix

Cada guia vira um subagent com a mesma receita (nome + description apontando para o guia + tools):

| Subagent | Traduz de | Papel |
|----------|-----------|-------|
| `architect` | `agents/architecture-planning.md` | Classifica a mudança por camada; barra violações da regra de dependência |
| `backend-dev` | `agents/backend-development.md` | Padrões FastAPI async, endpoints finos, mypy strict |
| `database-dev` | `agents/database-development.md` | Entidades/repos/migrations, sem query na presentation |
| `ai-ml-dev` | `agents/ai-ml-development.md` | Guardrails de LLM: output validado por schema, retries, fallback |
| `security-check` | `agents/security-check.md` | Segredos via env, sem auth bypass, "fail closed" |
| `qa-reviewer` | `agents/qa-guidelines.md` | Cobertura e política de testes por componente |
| `devops` | `agents/devops-guidelines.md` | Docker, healthcheck, CI mínima |

> **Demonstração poderosa:** peça ao Claude *"Adicione um endpoint `GET /media/genres`
> que lista os gêneros distintos, com testes."* Observe o Claude **delegar** ao `backend-dev`
> para o código, ao `database-dev` para a query e ao `qa-reviewer` para os testes — cada um
> carregando o guia de domínio correspondente. É o `/agents` do repo **ganhando vida**.

**Por que isso é melhor que um `AGENTS.md` monolítico?**
- **Contexto isolado** — cada subagent só carrega o guia que precisa (menos ruído, mais foco).
- **Ferramentas restritas** — o `qa-reviewer` não precisa de `Write`; o `security-check` só lê.
- **Delegação automática** — o Claude escolhe o especialista pela `description`.

---

## Bloco 5 — Agent Teams: orquestração multi-agente (70–85 min)

> ⚠️ **Recurso experimental**, desativado por padrão. Ative com
> `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Apresente como **direção do futuro**, não
> como fluxo de produção estável.

**Subagents vs Agent Teams:**

| Aspecto | Subagents | Agent Teams |
|---------|-----------|-------------|
| Comunicação | Reportam **de volta** ao agente principal | Teammates **conversam entre si** |
| Coordenação | O agente principal gerencia tudo | **Lista de tarefas compartilhada**; auto-coordenação |
| Contexto | Janela própria; devolve resultado | Instâncias totalmente independentes |
| Uso ideal | Tarefas focadas e rápidas | Trabalho paralelo complexo (pesquisa, review amplo, design) |

**Como funciona (conceito):**
- Um **team lead** (sessão principal) spawna **teammates** (instâncias independentes do Claude Code).
- Eles compartilham uma **lista de tarefas** (job board), com dependências.
- **Trocam mensagens** diretamente e herdam automaticamente o `CLAUDE.md`, MCP servers e Skills do projeto.

**Exemplo de invocação (linguagem natural):**
```text
Monte um time para preparar a feature de "listagem por gênero":
- um teammate implementa o endpoint e o service (perfil backend)
- um teammate escreve os testes seguindo qa-guidelines
- um teammate revisa segurança e a aderência às camadas
Coordenem pela lista de tarefas e me avisem quando os quality gates passarem.
```

**Quando usar Team vs Subagent (regra prática):**
- Mudança pequena e focada → **subagent** (ou só o agente principal).
- Trabalho amplo, paralelizável, com partes interdependentes → **agent team**.
- Na dúvida, comece simples: o ScreenFlix, sendo um monólito modular, raramente precisa
  de um time — mas é um ótimo laboratório para **entender o conceito**.

> **Discussão:** o `AI-CONFIG.json` já imagina **múltiplos consumidores de IA** trabalhando
> sobre o mesmo contexto. Agent Teams é a evolução natural: em vez de ferramentas separadas,
> vários agentes **coordenados** sobre o mesmo `CLAUDE.md` e o mesmo conjunto de Skills/Subagents.

---

## Bloco 6 — Síntese dos 3 dias e próximos passos (85–90 min)

**A jornada completa, num só repositório:**

| Dia | Tema | O que o ScreenFlix ensinou |
|-----|------|----------------------------|
| **1** | Infra & Containers | Empacotar a app: Dockerfile multi-stage, compose, Makefile |
| **2** | Programação Pragmática | Organizar por dentro: ambientes modulares + Clean Architecture |
| **3** | IA no Desenvolvimento | Deixar a IA respeitar tudo isso: CLAUDE.md, Skills, Subagents, Teams |

**A grande costura:** os artefatos de IA do Dia 3 **fazem cumprir** a arquitetura do
Dia 2 e os fluxos de infra do Dia 1. O `qa-reviewer` exige os testes; o `architect`
protege as camadas; a Skill `/quality-gate` roda os gates do `AI-CONFIG.json`; o hook
os torna automáticos. **Contexto de engenharia vira contexto executável de IA.**

**Próximos passos sugeridos para os participantes (backlog do repo, tudo hands-on):**
1. Criar o **Makefile** (Dia 1) e uma **CI** (`.github/workflows`) que rode `make check`.
2. Adicionar **migrations Alembic** de verdade (hoje só há `scripts/init.sql`).
3. Escrever os **testes de integração com testcontainers** (a dependência já existe; os
   testes atuais são todos mockados) — e gerar esses testes **com o subagent `qa-reviewer`**.
4. Materializar os **7 subagents** e a Skill `/quality-gate` neste repositório.

**Encerramento:** "Vocês saem com um projeto que sabem **empacotar** (Dia 1), **arquitetar**
(Dia 2) e desenvolver **com IA de forma disciplinada** (Dia 3) — usando um único código
como fio condutor."

---

## 📌 Apêndice — mapa dos artefatos criados no dia

```
screenflix/
├── CLAUDE.md                              # importa AGENTS.md / AI-CONFIG.json / agents/*
└── .claude/
    ├── skills/
    │   ├── quality-gate/SKILL.md          # roda os gates bloqueantes
    │   └── new-module/SKILL.md            # scaffolding de módulo (Clean Architecture)
    ├── agents/
    │   ├── architect.md                   # ← agents/architecture-planning.md
    │   ├── backend-dev.md                 # ← agents/backend-development.md
    │   ├── database-dev.md                # ← agents/database-development.md
    │   ├── ai-ml-dev.md                   # ← agents/ai-ml-development.md
    │   ├── security-check.md              # ← agents/security-check.md
    │   ├── qa-reviewer.md                 # ← agents/qa-guidelines.md
    │   └── devops.md                      # ← agents/devops-guidelines.md
    └── settings.json                      # hook: quality gate no evento Stop
```

> **Lembrete de precisão:** formatos válidos para o Claude Code v2.1.x (jul/2026).
> Agent Teams é **experimental** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`).
> O Claude Code lê **`CLAUDE.md`**, não `AGENTS.md` — por isso importamos com `@AGENTS.md`.
