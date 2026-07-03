<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useCatalogStore } from "../stores/catalog";
import { hueFor, posterBg, formatRating } from "../lib/media.js";
import Top5Row from "../components/Top5Row.vue";
import MediaRow from "../components/MediaRow.vue";

const catalog = useCatalogStore();
const router = useRouter();
const { movies, series } = storeToRefs(catalog);

const byRating = (list) => [...list].sort((a, b) => (b.rating || 0) - (a.rating || 0));

// Destaque: filme de maior nota; se não houver filmes, o título de maior nota.
const hero = computed(
  () => byRating(movies.value)[0] || byRating(series.value)[0] || null,
);
const heroBg = computed(() =>
  hero.value ? posterBg(hueFor(hero.value.id)) : "var(--sf-bg)",
);
const heroRating = computed(() =>
  hero.value ? formatRating(hero.value.rating) : "",
);
const heroTypeLabel = computed(() =>
  hero.value && catalog.isSeries(hero.value.id) ? "Série" : "Filme",
);

const top5Movies = computed(() => byRating(movies.value).slice(0, 5));
const top5Series = computed(() => byRating(series.value).slice(0, 5));

function openHero() {
  if (hero.value) router.push({ name: "detail", params: { id: hero.value.id } });
}
</script>

<template>
  <div v-if="hero" class="home">
    <section class="hero sf-gutter" :style="{ background: heroBg }">
      <div class="hero__overlay"></div>
      <div class="hero__content">
        <div class="hero__kicker">Em destaque · {{ heroTypeLabel }}</div>
        <h1 class="hero__title">{{ hero.title }}</h1>
        <div class="hero__meta">
          <span class="hero__rating">★ {{ heroRating }}</span>
        </div>
        <p class="hero__plot">{{ hero.plot }}</p>
        <div class="hero__actions">
          <button class="hero__btn" @click="openHero">▶&nbsp;&nbsp;Ver detalhes</button>
        </div>
      </div>
    </section>

    <div class="home__rows sf-gutter">
      <Top5Row
        v-if="top5Movies.length"
        title="Top 5 filmes da semana"
        :items="top5Movies"
      />
      <Top5Row
        v-if="top5Series.length"
        title="Top 5 séries da semana"
        :items="top5Series"
      />
      <MediaRow v-if="movies.length" title="Filmes" :items="movies" />
      <MediaRow v-if="series.length" title="Séries" :items="series" />
    </div>
  </div>

  <div v-else class="home-empty sf-gutter">
    <p>{{ catalog.apiState === "loading" ? "Carregando catálogo…" : "Nenhum título no catálogo ainda." }}</p>
  </div>
</template>

<style scoped>
.hero {
  position: relative;
  min-height: 78vh;
  display: flex;
  align-items: flex-end;
  padding-top: 48px;
  padding-bottom: 40px;
  margin-top: -78px;
}
.hero__overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      90deg,
      rgba(10, 10, 12, 0.92) 0%,
      rgba(10, 10, 12, 0.55) 45%,
      rgba(10, 10, 12, 0.15) 100%
    ),
    linear-gradient(0deg, #0f0f11 2%, rgba(15, 15, 17, 0) 55%);
}
.hero__content {
  position: relative;
  max-width: 560px;
}
.hero__kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sf-accent);
}
.hero__title {
  font-family: "Archivo", sans-serif;
  font-weight: 900;
  font-size: clamp(34px, 5vw, 60px);
  line-height: 1.02;
  margin: 0 0 8px;
  letter-spacing: -0.02em;
}
.hero__meta {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--sf-text-2);
}
.hero__rating {
  color: var(--sf-gold);
  font-weight: 700;
}
.hero__plot {
  font-size: 16px;
  line-height: 1.6;
  color: var(--sf-text-2);
  margin: 0 0 26px;
  max-width: 520px;
  /* Sinopses reais podem ser longas — limita para não estourar o hero. */
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.hero__btn {
  border: none;
  cursor: pointer;
  background: #fff;
  color: var(--sf-bg);
  font-family: "Manrope", sans-serif;
  font-weight: 700;
  font-size: 15px;
  padding: 12px 26px;
  border-radius: 5px;
  transition: background 0.15s;
}
.hero__btn:hover {
  background: #e6e6e6;
}

.home__rows {
  padding-top: 8px;
  margin-top: -10px;
  position: relative;
  z-index: 2;
}

.home-empty {
  padding-top: 80px;
  color: var(--sf-text-3);
}
</style>
