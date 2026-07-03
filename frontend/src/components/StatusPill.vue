<script setup>
import { computed } from "vue";
import { useCatalogStore } from "../stores/catalog";

const catalog = useCatalogStore();

const text = computed(() => {
  if (catalog.apiState === "online") return "API conectada";
  if (catalog.apiState === "loading") return "Conectando…";
  return "Modo demonstração";
});

const dotColor = computed(() => {
  if (catalog.apiState === "online") return "var(--sf-success)";
  if (catalog.apiState === "loading") return "var(--sf-text-3)";
  return "var(--sf-warn)";
});
</script>

<template>
  <div class="pill" title="Fonte de dados">
    <span class="pill__dot" :style="{ background: dotColor }"></span>
    {{ text }}
  </div>
</template>

<style scoped>
.pill {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 600;
  color: var(--sf-text-3);
}
.pill__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex: 0 0 auto;
}
</style>
