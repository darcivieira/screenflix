<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  src: { type: String, default: "" },
  title: { type: String, default: "" },
  bg: { type: String, default: "" },
  // posição do título no fallback: "bottom" (pôsteres) ou "center" (stills)
  titleAlign: { type: String, default: "bottom" },
  titleSize: { type: String, default: "15px" },
});

const failed = ref(false);
// Se a fonte mudar (reuso do componente entre itens), reseta o estado de erro.
watch(
  () => props.src,
  () => {
    failed.value = false;
  },
);
</script>

<template>
  <div class="poster" :style="{ background: bg }">
    <span
      class="poster__title"
      :class="`poster__title--${titleAlign}`"
      :style="{ fontSize: titleSize }"
      >{{ title }}</span
    >
    <img
      v-if="src && !failed"
      :src="src"
      alt=""
      class="poster__img"
      @error="failed = true"
    />
  </div>
</template>

<style scoped>
.poster {
  position: absolute;
  inset: 0;
  overflow: hidden;
}
.poster__title {
  position: absolute;
  inset: 0;
  display: flex;
  padding: 12px;
  font-family: "Archivo", sans-serif;
  font-weight: 800;
  line-height: 1.12;
  color: rgba(255, 255, 255, 0.92);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
}
.poster__title--bottom {
  align-items: flex-end;
}
.poster__title--center {
  align-items: center;
  justify-content: center;
  text-align: center;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.85);
  padding: 10px;
}
.poster__img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
