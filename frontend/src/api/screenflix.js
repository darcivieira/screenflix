// ============================================================
// ScreenFlix — camada de integração com a API (OpenAPI 1.0.0)
// ------------------------------------------------------------
// A URL base vem da variável de ambiente do Vite (VITE_API_BASE).
// Enquanto estiver vazia (ou inacessível), o app roda em
// "Modo demonstração". Ex.: VITE_API_BASE=http://localhost:8000
// ============================================================
export const API_BASE = import.meta.env.VITE_API_BASE || "";

const j = async (path) => {
  const res = await fetch(API_BASE + path, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error("HTTP " + res.status + " em " + path);
  return res.json();
};

// GET /healthz
export const health = () => j("/healthz");

// GET /api/v1/media  → MediaBaseSchema[]
export const listAllMedia = () => j("/api/v1/media");

// GET /api/v1/media/movies  → MediaBaseSchema[]
export const listMovies = () => j("/api/v1/media/movies");

// GET /api/v1/media/series  → MediaBaseSchema[]
export const listSeries = () => j("/api/v1/media/series");

// GET /api/v1/media/movies/top5  → MediaBaseSchema[]
export const topMovies = () => j("/api/v1/media/movies/top5");

// GET /api/v1/media/series/top5  → MediaBaseSchema[]
export const topSeries = () => j("/api/v1/media/series/top5");

// GET /api/v1/media/{id}  → MediaSchema (ficha completa)
export const getMedia = (id) => j("/api/v1/media/" + id);

// GET /api/v1/media/{id}/seasons/{season}  → EpisodeBaseSchema[]
export const listEpisodes = (id, season) =>
  j("/api/v1/media/" + id + "/seasons/" + season);

// GET /api/v1/media/{id}/seasons/{season}/episode/{episode}  → EpisodeSchema
export const getEpisode = (id, season, episode) =>
  j("/api/v1/media/" + id + "/seasons/" + season + "/episode/" + episode);

// POST /api/v1/register  { name }
export const register = async (name) => {
  const res = await fetch(API_BASE + "/api/v1/register", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error("HTTP " + res.status + " em /register");
  return res.json().catch(() => ({}));
};
