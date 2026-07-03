<script setup>
import { onMounted } from "vue";
import { useCatalogStore } from "./stores/catalog";
import TheHeader from "./components/TheHeader.vue";

const catalog = useCatalogStore();

onMounted(() => {
  catalog.init();
});
</script>

<template>
  <TheHeader />
  <main class="app-main">
    <RouterView />
  </main>
</template>

<style scoped>
.app-main {
  padding-bottom: 80px;
}
</style>
