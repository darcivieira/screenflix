import { defineStore } from "pinia";
import { ref, computed } from "vue";
import * as api from "../api/screenflix";

const MAX_SEASON_PROBE = 8;

export const useCatalogStore = defineStore("catalog", () => {
  // 'loading' | 'online' | 'offline'
  const apiState = ref("loading");
  const movies = ref([]);
  const series = ref([]);
  const seriesIds = ref(new Set());

  const detailCache = ref({}); // { [id]: MediaSchema }
  const seasonsCache = ref({}); // { [id]: number[] }
  const episodesCache = ref({}); // { [`${id}:${season}`]: EpisodeSchema[] }

  let initialized = false;

  const isSeries = (id) => seriesIds.value.has(Number(id));

  const findInLists = (id) => {
    const nid = Number(id);
    return (
      movies.value.find((m) => m.id === nid) ||
      series.value.find((m) => m.id === nid) ||
      null
    );
  };

  async function refreshLists() {
    const [mv, sr] = await Promise.all([api.listMovies(), api.listSeries()]);
    movies.value = mv;
    series.value = sr;
    seriesIds.value = new Set(sr.map((s) => s.id));
  }

  async function init() {
    if (initialized) return;
    initialized = true;
    if (!api.API_BASE) {
      apiState.value = "offline";
      return;
    }
    try {
      await api.health();
      await refreshLists();
      apiState.value = "online";
    } catch (e) {
      apiState.value = "offline";
    }
  }

  async function loadDetail(id) {
    const nid = Number(id);
    if (detailCache.value[nid]) return detailCache.value[nid];
    try {
      const full = await api.getMedia(nid);
      detailCache.value = { ...detailCache.value, [nid]: full };
      return full;
    } catch (e) {
      return null;
    }
  }

  // Descobre temporadas sondando /seasons/{s} até 404/vazio.
  async function loadSeasons(id) {
    const nid = Number(id);
    if (seasonsCache.value[nid]) return seasonsCache.value[nid];
    const nums = [];
    for (let s = 1; s <= MAX_SEASON_PROBE; s++) {
      try {
        const eps = await api.listEpisodes(nid, s);
        if (Array.isArray(eps) && eps.length) nums.push(s);
        else break;
      } catch (e) {
        break;
      }
    }
    seasonsCache.value = { ...seasonsCache.value, [nid]: nums };
    return nums;
  }

  async function loadEpisodes(id, season) {
    const nid = Number(id);
    const key = `${nid}:${season}`;
    if (episodesCache.value[key]) return episodesCache.value[key];
    try {
      const base = await api.listEpisodes(nid, season);
      const full = await Promise.all(
        base.map((ep) => api.getEpisode(nid, season, ep.id).catch(() => ep)),
      );
      episodesCache.value = { ...episodesCache.value, [key]: full };
      return full;
    } catch (e) {
      episodesCache.value = { ...episodesCache.value, [key]: [] };
      return [];
    }
  }

  // Cadastra um título e recarrega as listas; devolve o item encontrado (ou null).
  async function registerTitle(name) {
    await api.register(name);
    await refreshLists();
    const target = name.trim().toLowerCase();
    return (
      [...movies.value, ...series.value].find(
        (x) => (x.title || "").toLowerCase() === target,
      ) || null
    );
  }

  const moviesCount = computed(() => movies.value.length);
  const seriesCount = computed(() => series.value.length);

  return {
    apiState,
    movies,
    series,
    seriesIds,
    detailCache,
    seasonsCache,
    episodesCache,
    moviesCount,
    seriesCount,
    isSeries,
    findInLists,
    init,
    refreshLists,
    loadDetail,
    loadSeasons,
    loadEpisodes,
    registerTitle,
  };
});
