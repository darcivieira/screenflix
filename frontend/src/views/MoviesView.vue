<script setup>
import { storeToRefs } from "pinia";
import { useCatalogStore } from "../stores/catalog";
import PosterCard from "../components/PosterCard.vue";

const catalog = useCatalogStore();
const { movies } = storeToRefs(catalog);
</script>

<template>
  <div class="grid-view sf-gutter">
    <h1 class="grid-view__title">Filmes</h1>
    <p class="grid-view__count">{{ movies.length }} títulos no catálogo</p>
    <div class="grid-view__grid">
      <PosterCard
        v-for="item in movies"
        :key="item.id"
        :item="item"
        variant="grid"
      />
    </div>
  </div>
</template>

<style scoped>
.grid-view {
  padding-top: 40px;
}
.grid-view__title {
  font-family: "Archivo", sans-serif;
  font-weight: 900;
  font-size: 34px;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
}
.grid-view__count {
  color: var(--sf-text-3);
  font-size: 14px;
  margin: 0 0 28px;
}
.grid-view__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(158px, 1fr));
  gap: 22px 16px;
}
</style>
