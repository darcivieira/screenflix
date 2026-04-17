# Prompt para Google Stitch - ScreenFlix

Use o prompt abaixo no Google Stitch para gerar o frontend completo.

```text
Você é um(a) Frontend Engineer + Product Designer sênior.
Crie o frontend completo da aplicação ScreenFlix com visual premium inspirado em plataformas de streaming (look & feel Netflix-like), com HTML, CSS e JavaScript modernos, responsivos e acessíveis.

Objetivo:
- Gerar uma aplicação web moderna para navegação de filmes/séries, detalhes da mídia e episódios por temporada.
- Consumir a API descrita no arquivo openapi.json deste projeto.
- Entregar layout consistente com design system sólido (tokens + componentes + estados).

Referência obrigatória:
- Ler e usar o contrato OpenAPI em: ./openapi.json
- Base URL da API: http://localhost:8000

Endpoints que devem ser integrados:
- GET /healthz
- POST /api/v1/register
- GET /api/v1/media
- GET /api/v1/media/movies
- GET /api/v1/media/series
- GET /api/v1/media/movies/top5
- GET /api/v1/media/series/top5
- GET /api/v1/media/{media_id}
- GET /api/v1/media/{media_id}/seasons/{season_id}
- GET /api/v1/media/{media_id}/seasons/{season_id}/episode/{episode_id}

Campos principais vindos da API (usar no mapeamento visual):
- Media base: id, title, original_title, poster_url, rating, plot
- Media detalhe: id, title, original_title, poster_url, rating, year, release_date, genres, actors, writers, directors, plot
- Episódio base: id, original_title, poster_url
- Episódio detalhe: id, original_title, title, released, poster_url, rating, plot

Arquitetura de frontend desejada:
- Estrutura limpa e modular em HTML/CSS/JS (sem depender de framework).
- Criar camada de API (api.js) com funções para cada endpoint.
- Criar camada de estado simples para loading, erro e sucesso.
- Separar estilos globais, tokens e componentes.
- Não usar dados mockados quando houver endpoint correspondente.

Páginas/Seções obrigatórias:
1) Landing/Home:
- Hero dinâmico com destaque de mídia.
- Trilhos horizontais (carousels) para:
  - Top 5 Filmes
  - Top 5 Séries
  - Todos os Títulos
  - Filmes
  - Séries
- Cards com poster, título, rating e hover state.

2) Detalhe da mídia:
- Banner/poster grande.
- Metadados (ano, gêneros, elenco, direção, roteiristas, nota).
- Sinopse.
- Bloco de temporadas/episódios quando aplicável.

3) Detalhe de episódio:
- Poster/thumb.
- Título original e título local.
- Nota e data de lançamento.
- Descrição.

4) Cadastro rápido de mídia:
- Formulário com campo "name" para POST /api/v1/register.
- Feedback visual de sucesso/erro.

5) Estado de saúde da API:
- Indicador discreto no header/footer baseado em GET /healthz.

Design System (obrigatório):
- Definir tokens CSS em :root (cores, tipografia, espaçamento, radius, sombra, z-index, breakpoints, transições).
- Paleta recomendada:
  - Background principal: #0B0B0F
  - Surface 1: #14141D
  - Surface 2: #1E1E2A
  - Primary/Brand: #E50914
  - Primary hover: #F6121D
  - Accent frio: #00B3FF
  - Texto principal: #F5F7FA
  - Texto secundário: #A9B0BD
  - Sucesso: #22C55E
  - Aviso: #F59E0B
  - Erro: #EF4444
- Tipografia:
  - Headings fortes e cinematográficos.
  - Corpo com ótima legibilidade.
  - Escala tipográfica fluida.
- Componentes mínimos:
  - Header sticky com navegação
  - Hero
  - Card de mídia
  - Carrossel horizontal com controles
  - Botões (primário, secundário, ghost)
  - Input + formulário
  - Badge de rating
  - Modal ou página de detalhes
  - Skeleton loader
  - Empty state
  - Error state + retry
  - Toast/alerta de feedback

UX e interação:
- Microinterações suaves (hover, focus, transições).
- Navegação por teclado completa.
- Estados de foco visíveis (acessibilidade).
- Lazy loading de imagens.
- Scroll horizontal confortável em mobile.
- Evitar layout genérico; visual deve parecer produto real pronto para produção.

Responsividade:
- Mobile-first.
- Breakpoints para mobile, tablet e desktop.
- Ajustar hero, trilhos e grid sem quebrar legibilidade.

Acessibilidade:
- Contraste adequado (WCAG AA).
- aria-labels onde necessário.
- Estrutura semântica (header, main, section, nav, footer).
- Formulários com label associado e mensagens de erro claras.

Requisitos de integração:
- Implementar funções assíncronas para todos os endpoints listados.
- Tratar HTTP 404/422 e falhas de rede com mensagens amigáveis.
- Centralizar configuração de base URL em constante.
- Renderização orientada por dados da API.

Qualidade de código:
- Código organizado, comentado apenas quando necessário.
- Nomes de classes e funções claros.
- Sem duplicação excessiva.
- CSS com organização por camadas (tokens, base, layout, components, utilities).

Entregáveis esperados:
- index.html (home + seções principais)
- media.html (detalhe de mídia)
- episode.html (detalhe de episódio)
- styles.css (design system + componentes + responsividade)
- api.js (integrações HTTP)
- app.js (estado, renderização, interações)

Instruções finais:
- Primeiro, descreva rapidamente a estrutura de arquivos gerada.
- Depois, entregue todo o código completo de cada arquivo.
- Garanta que o resultado rode localmente apenas abrindo os HTMLs e apontando para a API em localhost:8000.
```

