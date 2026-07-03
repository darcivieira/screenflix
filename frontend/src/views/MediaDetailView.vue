<script setup>
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useCatalogStore } from "../stores/catalog";
import {
  hueFor,
  posterBg,
  posterBg2,
  posterSrc,
  formatDate,
  formatRating,
} from "../lib/media.js";
import PosterImage from "../components/PosterImage.vue";
import EpisodeItem from "../components/EpisodeItem.vue";

const props = defineProps({
  id: { type: Number, required: true },
});

const router = useRouter();
const catalog = useCatalogStore();

const selectedSeason = ref(1);

const hue = computed(() => hueFor(props.id));
const isSeries = computed(() => catalog.isSeries(props.id));

// Une o item base (das listas) com a ficha completa (cache de detalhe).
const detail = computed(() => {
  const base = catalog.findInLists(props.id) || {};
  const full = catalog.detailCache[props.id] || {};
  const d = { ...base, ...full };
  const loading = catalog.apiState === "online" && !catalog.detailCache[props.id];
  return {
    title: d.title || "",
    originalLine: `Título original: ${d.original_title || d.title || ""}`,
    year: d.year || (d.release_date ? String(d.release_date).slice(0, 4) : ""),
    rating: formatRating(d.rating),
    genres: d.genres || "",
    directors: d.directors || "—",
    writers: d.writers || "—",
    actors: d.actors || "—",
    plot: d.plot || (loading ? "Carregando sinopse…" : ""),
    releaseLine: formatDate(d.release_date),
    posterUrl: posterSrc(d.poster_url),
  };
});

const seasons = computed(() => catalog.seasonsCache[props.id] || []);
const episodes = computed(
  () => catalog.episodesCache[`${props.id}:${selectedSeason.value}`] || [],
);

async function load() {
  selectedSeason.value = 1;
  await catalog.loadDetail(props.id);
  if (catalog.isSeries(props.id)) {
    const nums = await catalog.loadSeasons(props.id);
    if (nums.length) {
      selectedSeason.value = nums.includes(1) ? 1 : nums[0];
      catalog.loadEpisodes(props.id, selectedSeason.value);
    }
  }
}

watch(() => props.id, load, { immediate: true });
// Recarrega ficha/temporadas quando as listas terminam de carregar (define isSeries).
watch(
  () => catalog.apiState,
  (s) => {
    if (s === "online") load();
  },
);

watch(selectedSeason, (s) => {
  if (catalog.isSeries(props.id)) catalog.loadEpisodes(props.id, s);
});

function goBack() {
  if (window.history.length > 1) router.back();
  else router.push({ name: "home" });
}
</script>

<template>
  <section class="detail">
    <div class="detail__backdrop" :style="{ background: posterBg(hue) }">
      <div class="detail__overlay"></div>

      <div class="detail__inner sf-gutter">
        <button class="detail__back" @click="goBack">← Voltar</button>

        <div class="detail__layout">
          <div class="detail__poster" :style="{ background: posterBg2(hue) }">
            <PosterImage
              :src="detail.posterUrl"
              :title="detail.title"
              :bg="posterBg2(hue)"
              title-size="20px"
            />
          </div>

          <div class="detail__info">
            <div class="detail__kicker">{{ isSeries ? "Série" : "Filme" }}</div>
            <h1 class="detail__title">{{ detail.title }}</h1>
            <p class="detail__original">{{ detail.originalLine }}</p>
            <div class="detail__meta">
              <span class="detail__rating">★ {{ detail.rating }}</span>
              <span v-if="detail.year">{{ detail.year }}</span>
              <span v-if="detail.genres" class="detail__genre">{{ detail.genres }}</span>
            </div>
            <p class="detail__plot">{{ detail.plot }}</p>

            <div class="detail__facts">
              <div class="fact">
                <div class="fact__label">Direção</div>
                <div class="fact__value">{{ detail.directors }}</div>
              </div>
              <div class="fact">
                <div class="fact__label">Roteiro</div>
                <div class="fact__value">{{ detail.writers }}</div>
              </div>
              <div class="fact">
                <div class="fact__label">Elenco</div>
                <div class="fact__value">{{ detail.actors }}</div>
              </div>
              <div class="fact">
                <div class="fact__label">Lançamento</div>
                <div class="fact__value">{{ detail.releaseLine }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isSeries" class="episodes sf-gutter">
      <div class="episodes__head">
        <h2 class="episodes__title">Episódios</h2>
        <select
          v-if="seasons.length"
          v-model.number="selectedSeason"
          class="sf-select episodes__select"
        >
          <option v-for="s in seasons" :key="s" :value="s">Temporada {{ s }}</option>
        </select>
      </div>

      <div v-if="episodes.length" class="episodes__list">
        <EpisodeItem
          v-for="(ep, i) in episodes"
          :key="ep.id ?? i"
          :episode="ep"
          :index="i"
          :hue="hue"
        />
      </div>
      <p v-else class="episodes__empty">Carregando episódios…</p>
    </div>
  </section>
</template>

<style scoped>
.detail {
  position: relative;
}
.detail__backdrop {
  position: relative;
  min-height: 62vh;
  padding-top: 120px;
  padding-bottom: 40px;
  margin-top: -78px;
}
.detail__overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      90deg,
      rgba(10, 10, 12, 0.94) 0%,
      rgba(10, 10, 12, 0.6) 50%,
      rgba(10, 10, 12, 0.3) 100%
    ),
    linear-gradient(0deg, #0f0f11 1%, rgba(15, 15, 17, 0) 60%);
}
.detail__inner {
  position: relative;
}
.detail__back {
  position: relative;
  margin-bottom: 26px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: var(--sf-text);
  cursor: pointer;
  font-family: "Manrope", sans-serif;
  font-weight: 600;
  font-size: 13.5px;
  padding: 8px 15px;
  border-radius: 20px;
  transition: background 0.15s;
}
.detail__back:hover {
  background: rgba(255, 255, 255, 0.18);
}
.detail__layout {
  position: relative;
  display: flex;
  gap: 36px;
  flex-wrap: wrap;
  align-items: flex-end;
}
.detail__poster {
  position: relative;
  width: 210px;
  aspect-ratio: 2 / 3;
  flex: 0 0 auto;
  border-radius: 9px;
  overflow: hidden;
  box-shadow: 0 16px 44px rgba(0, 0, 0, 0.6);
}
.detail__info {
  flex: 1 1 340px;
  min-width: 300px;
}
.detail__kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sf-accent);
}
.detail__title {
  font-family: "Archivo", sans-serif;
  font-weight: 900;
  font-size: clamp(30px, 4.4vw, 50px);
  line-height: 1.02;
  letter-spacing: -0.02em;
  margin: 0 0 6px;
}
.detail__original {
  margin: 0 0 18px;
  color: var(--sf-text-3);
  font-size: 15px;
  font-style: italic;
}
.detail__meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 22px;
  font-size: 14px;
  color: var(--sf-text-2);
}
.detail__rating {
  color: var(--sf-gold);
  font-weight: 700;
}
.detail__genre {
  padding: 3px 10px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 5px;
  font-size: 12px;
  font-weight: 600;
}
.detail__plot {
  font-size: 16px;
  line-height: 1.65;
  color: #e5e5e7;
  margin: 0 0 26px;
  max-width: 640px;
}
.detail__facts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px 32px;
  max-width: 640px;
}
.fact__label {
  font-size: 11.5px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--sf-label);
  font-weight: 700;
  margin-bottom: 4px;
}
.fact__value {
  font-size: 14.5px;
  color: #e5e5e7;
}

.episodes {
  padding-top: 36px;
}
.episodes__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 22px;
}
.episodes__title {
  font-family: "Archivo", sans-serif;
  font-weight: 800;
  font-size: 24px;
  margin: 0;
}
.episodes__select {
  background: #1b1b1f;
  color: var(--sf-text);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 6px;
  padding: 9px 14px;
  font-family: "Manrope", sans-serif;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
}
.episodes__list {
  display: flex;
  flex-direction: column;
}
.episodes__empty {
  color: var(--sf-text-3);
  font-size: 14px;
}
</style>
