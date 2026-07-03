<script setup>
import PosterCard from "./PosterCard.vue";

defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <section class="row-section">
    <h2 class="row-section__title">{{ title }}</h2>
    <div class="sf-row row-section__track">
      <div v-for="item in items" :key="item.id" class="row-section__cell">
        <PosterCard :item="item" variant="row" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.row-section {
  margin-bottom: 34px;
}
.row-section__title {
  font-family: "Archivo", sans-serif;
  font-weight: 800;
  font-size: 20px;
  margin: 0 0 14px;
}
.row-section__track {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  padding: 4px 2px 16px;
}
.row-section__cell {
  flex: 0 0 auto;
  width: 154px;
}
</style>
