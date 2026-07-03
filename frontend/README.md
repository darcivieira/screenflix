# ScreenFlix — Frontend (Vue 3 + Vite)

Catálogo de filmes e séries que consome a **ScreenFlix API** (FastAPI). Implementa o
design descrito em `../design_handoff_screenflix/README.md` — tema escuro, destaque
vermelho, home com hero + fileiras, telas de Filmes/Séries, ficha de título (com
episódios por temporada, para séries) e cadastro por nome.

## Stack

- **Vue 3** (Composition API + `<script setup>`)
- **Vue Router 4** — rotas das telas
- **Pinia** — cache de catálogo/detalhe/temporadas/episódios (`src/stores/catalog.js`)
- `fetch` nativo na camada de API (`src/api/screenflix.js`, portado do handoff)

## Configuração

A URL base da API vem de `VITE_API_BASE`. Copie o exemplo e ajuste se necessário:

```bash
cp .env.example .env       # VITE_API_BASE=http://localhost:8000
```

Se `VITE_API_BASE` estiver vazio ou a API estiver inacessível, o app entra em
"Modo demonstração" (pílula de status âmbar) e as listas ficam vazias.

## Rodando

```bash
npm install
npm run dev      # servidor de desenvolvimento (Vite)
npm run build    # build de produção em dist/
npm run preview  # serve o build
```

## Estrutura

```
src/
  api/screenflix.js     # cliente HTTP (funções 1:1 com o openapi.json)
  lib/media.js          # helpers: hue determinístico, gradientes de pôster, datas
  stores/catalog.js     # Pinia store (init, loadDetail, loadSeasons, loadEpisodes, registerTitle)
  router/index.js       # rotas: /, /filmes, /series, /titulo/:id, /cadastrar
  components/            # TheHeader, StatusPill, PosterImage, PosterCard, MediaRow, Top5Row, EpisodeItem
  views/                # HomeView, MoviesView, SeriesView, MediaDetailView, RegisterView
```

## Notas de implementação

- **Fallback de pôster**: cada `poster_url` tem um gradiente determinístico por baixo
  (`posterBg(hue)`, `hue = (id * 47) % 360`) + o título; o `<img>` cobre por cima e, em
  `@error`, é escondido para revelar o fallback (`components/PosterImage.vue`).
- **Séries vs filmes**: a `MediaSchema` não tem campo de tipo — o store mantém um `Set`
  de ids de série (a partir de `GET /api/v1/media/series`).
- **Temporadas**: descobertas sondando `GET /media/{id}/seasons/{s}` até 404/vazio.
- **Episódios**: `listEpisodes` traz o básico; o detalhe de cada episódio é buscado em
  paralelo (`Promise.all`) e cacheado por `${id}:${season}`.
