<script setup>
import { computed } from "vue";
import PosterImage from "./PosterImage.vue";
import { posterBg2, posterSrc, formatDate, formatRating } from "../lib/media.js";

const props = defineProps({
  episode: { type: Object, required: true },
  index: { type: Number, required: true },
  hue: { type: Number, required: true },
});

const number = computed(() => props.index + 1);
const stillBg = computed(() => posterBg2(props.hue + props.index * 18));
const title = computed(
  () =>
    props.episode.title ||
    props.episode.original_title ||
    `Episódio ${number.value}`,
);
const releaseLine = computed(() => formatDate(props.episode.released));
const rating = computed(() => formatRating(props.episode.rating));
</script>

<template>
  <div class="ep">
    <span class="ep__number">{{ number }}</span>
    <div class="ep__still">
      <PosterImage
        :src="posterSrc(episode.poster_url)"
        :title="episode.original_title"
        :bg="stillBg"
        title-align="center"
        title-size="12.5px"
      />
    </div>
    <div class="ep__body">
      <div class="ep__head">
        <h4 class="ep__title">{{ title }}</h4>
        <span class="ep__rating">★ {{ rating }}</span>
      </div>
      <div class="ep__date">{{ releaseLine }}</div>
      <p class="ep__plot">{{ episode.plot }}</p>
    </div>
  </div>
</template>

<style scoped>
.ep {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  padding: 18px 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.ep__number {
  font-family: "Archivo", sans-serif;
  font-weight: 800;
  font-size: 26px;
  color: var(--sf-label-2);
  flex: 0 0 34px;
  text-align: center;
  padding-top: 14px;
}
.ep__still {
  position: relative;
  width: 170px;
  aspect-ratio: 16 / 9;
  flex: 0 0 auto;
  border-radius: 7px;
  overflow: hidden;
}
.ep__body {
  flex: 1 1 auto;
  min-width: 0;
}
.ep__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}
.ep__title {
  font-family: "Manrope", sans-serif;
  font-weight: 700;
  font-size: 16px;
  margin: 0;
  color: var(--sf-text);
}
.ep__rating {
  color: var(--sf-gold);
  font-weight: 700;
  font-size: 13px;
  flex: 0 0 auto;
}
.ep__date {
  font-size: 12px;
  color: var(--sf-label);
  margin-bottom: 7px;
}
.ep__plot {
  font-size: 14px;
  line-height: 1.55;
  color: var(--sf-text-3);
  margin: 0;
  max-width: 720px;
}

@media (max-width: 560px) {
  .ep__still {
    width: 130px;
  }
}
</style>
