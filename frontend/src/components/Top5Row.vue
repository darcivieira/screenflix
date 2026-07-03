<script setup>
import { useRouter } from "vue-router";
import PosterImage from "./PosterImage.vue";
import { hueFor, posterBg, posterSrc } from "../lib/media.js";

defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
});

const router = useRouter();

function open(id) {
  router.push({ name: "detail", params: { id } });
}
</script>

<template>
  <section class="top5">
    <h2 class="top5__title">{{ title }}</h2>
    <div class="sf-row top5__track">
      <div
        v-for="(item, i) in items"
        :key="item.id"
        class="top5__item"
        @click="open(item.id)"
      >
        <span class="top5__rank">{{ i + 1 }}</span>
        <div class="top5__poster">
          <PosterImage
            :src="posterSrc(item.poster_url)"
            :title="item.title"
            :bg="posterBg(hueFor(item.id))"
            title-size="16px"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.top5 {
  margin-bottom: 34px;
}
.top5__title {
  font-family: "Archivo", sans-serif;
  font-weight: 800;
  font-size: 20px;
  margin: 0 0 14px;
}
.top5__track {
  display: flex;
  gap: 28px;
  overflow-x: auto;
  padding: 8px 4px 16px;
}
.top5__item {
  display: flex;
  align-items: flex-end;
  flex: 0 0 auto;
  cursor: pointer;
}
.top5__rank {
  font-family: "Archivo", sans-serif;
  font-weight: 900;
  font-size: 130px;
  line-height: 0.8;
  color: var(--sf-bg);
  -webkit-text-stroke: 3px var(--sf-top5-stroke);
  margin-right: -14px;
  user-select: none;
}
.top5__poster {
  position: relative;
  width: 150px;
  aspect-ratio: 2 / 3;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  transition: transform 0.18s;
}
.top5__item:hover .top5__poster {
  transform: scale(1.04);
}
</style>
