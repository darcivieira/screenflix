<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import PosterImage from "./PosterImage.vue";
import {
  hueFor,
  posterBg,
  posterSrc,
  formatRating,
} from "../lib/media.js";

const props = defineProps({
  item: { type: Object, required: true },
  // "row" → meta ano + nota, raio 6px · "grid" → meta título + nota, raio 7px
  variant: { type: String, default: "row" },
});

const router = useRouter();

const bg = computed(() => posterBg(hueFor(props.item.id)));
const src = computed(() => posterSrc(props.item.poster_url));
const rating = computed(() => formatRating(props.item.rating));
const year = computed(() => props.item.year || "");

function open() {
  router.push({ name: "detail", params: { id: props.item.id } });
}
</script>

<template>
  <div class="card" :class="`card--${variant}`" @click="open">
    <div class="card__poster">
      <PosterImage
        :src="src"
        :title="item.title"
        :bg="bg"
        :title-size="variant === 'grid' ? '16px' : '15px'"
      />
    </div>
    <div class="card__meta">
      <template v-if="variant === 'grid'">
        <span class="card__title">{{ item.title }}</span>
        <span class="card__rating">★ {{ rating }}</span>
      </template>
      <template v-else>
        <span class="card__year">{{ year }}</span>
        <span class="card__rating">★ {{ rating }}</span>
      </template>
    </div>
  </div>
</template>

<style scoped>
.card {
  cursor: pointer;
}
.card__poster {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 3;
  border-radius: 6px;
  overflow: hidden;
  transition: transform 0.18s;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
}
.card--grid .card__poster {
  border-radius: 7px;
}
.card:hover .card__poster {
  transform: scale(1.05);
}
.card--grid:hover .card__poster {
  transform: scale(1.04);
}

.card__meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12.5px;
}
.card--grid .card__meta {
  margin-top: 9px;
  font-size: 13px;
}
.card__year {
  color: var(--sf-text-2);
  font-weight: 600;
}
.card__title {
  color: #e5e5e7;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card__rating {
  color: var(--sf-gold);
  font-weight: 700;
  flex: 0 0 auto;
  margin-left: 8px;
}
</style>
