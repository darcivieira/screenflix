<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useCatalogStore } from "../stores/catalog";
import { hueFor, posterBg, formatRating } from "../lib/media.js";

const router = useRouter();
const catalog = useCatalogStore();

const name = ref("");
const error = ref("");
const submitting = ref(false);
const result = ref(null); // { id, title, year, genres, rating, plot, indexed }

const btnLabel = computed(() => (submitting.value ? "Buscando…" : "Cadastrar"));

const resultBg = computed(() =>
  result.value ? posterBg(hueFor(result.value.id > 0 ? result.value.id : 200)) : "",
);

async function submit() {
  const trimmed = name.value.trim();
  if (!trimmed) {
    error.value = "Digite o nome de um título para cadastrar.";
    return;
  }
  if (submitting.value) return;
  if (catalog.apiState !== "online") {
    error.value = "API indisponível. Verifique a conexão para cadastrar.";
    return;
  }

  submitting.value = true;
  error.value = "";
  result.value = null;

  try {
    const found = await catalog.registerTitle(trimmed);
    name.value = "";
    if (found) {
      result.value = {
        id: found.id,
        title: found.title,
        year: found.year || "",
        genres: found.genres || "—",
        rating: formatRating(found.rating),
        plot: found.plot || "",
        indexed: true,
      };
    } else {
      result.value = {
        id: -1,
        title: trimmed,
        year: "",
        genres: "—",
        rating: formatRating(0),
        plot: "Título enviado à API. Os metadados podem levar alguns instantes para serem indexados.",
        indexed: false,
      };
    }
  } catch (e) {
    error.value = "Não foi possível cadastrar. Verifique a conexão com a API.";
  } finally {
    submitting.value = false;
  }
}

function openResult() {
  if (result.value && result.value.id > 0) {
    router.push({ name: "detail", params: { id: result.value.id } });
  }
}
</script>

<template>
  <div class="register">
    <h1 class="register__title">Cadastrar título</h1>
    <p class="register__lead">
      Digite o nome de um filme ou série. A ScreenFlix busca automaticamente
      sinopse, elenco, direção, gêneros e pôster.
    </p>

    <div class="card">
      <label class="card__label" for="register-name">Nome do título</label>
      <div class="card__row">
        <input
          id="register-name"
          v-model="name"
          class="card__input"
          placeholder="Ex.: Duna, The Office, Oppenheimer…"
          @input="error = ''"
          @keydown.enter="submit"
        />
        <button class="card__btn" :disabled="submitting" @click="submit">
          {{ btnLabel }}
        </button>
      </div>
      <p v-if="error" class="card__error">{{ error }}</p>
    </div>

    <div v-if="result" class="result">
      <div class="result__poster" :style="{ background: resultBg }">
        <span class="result__poster-title">{{ result.title }}</span>
      </div>
      <div class="result__body">
        <div class="result__badge" :class="{ 'result__badge--pending': !result.indexed }">
          {{ result.indexed ? "✓ Adicionado ao catálogo" : "⏳ Processando metadados" }}
        </div>
        <h3 class="result__title">{{ result.title }}</h3>
        <div class="result__meta">
          <template v-if="result.indexed">
            {{ result.year ? result.year + " · " : "" }}{{ result.genres }} · ★ {{ result.rating }}
          </template>
        </div>
        <p class="result__plot">{{ result.plot }}</p>
        <button v-if="result.id > 0" class="result__btn" @click="openResult">
          Ver detalhes →
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register {
  max-width: 560px;
  margin: 60px auto 0;
  padding: 0 24px;
}
.register__title {
  font-family: "Archivo", sans-serif;
  font-weight: 900;
  font-size: 32px;
  letter-spacing: -0.02em;
  margin: 0 0 8px;
}
.register__lead {
  color: var(--sf-text-3);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 30px;
}

.card {
  background: var(--sf-surface);
  border: 1px solid var(--sf-border);
  border-radius: 12px;
  padding: 28px;
}
.card__label {
  display: block;
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sf-text-3);
  margin-bottom: 10px;
}
.card__row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.card__input {
  flex: 1 1 240px;
  background: var(--sf-surface-input);
  border: 1px solid var(--sf-border-input);
  border-radius: 7px;
  padding: 13px 15px;
  color: var(--sf-text);
  font-family: "Manrope", sans-serif;
  font-size: 15px;
  outline: none;
  transition: border-color 0.15s;
}
.card__input:focus {
  border-color: var(--sf-accent);
}
.card__btn {
  flex: 0 0 auto;
  border: none;
  cursor: pointer;
  background: var(--sf-accent);
  color: #fff;
  font-family: "Manrope", sans-serif;
  font-weight: 700;
  font-size: 15px;
  padding: 13px 24px;
  border-radius: 7px;
  transition: background 0.15s;
}
.card__btn:hover:not(:disabled) {
  background: var(--sf-accent-hover);
}
.card__btn:disabled {
  opacity: 0.7;
  cursor: default;
}
.card__error {
  margin: 12px 0 0;
  color: #f87171;
  font-size: 13.5px;
}

.result {
  margin-top: 24px;
  background: var(--sf-surface);
  border: 1px solid rgba(38, 208, 124, 0.35);
  border-radius: 12px;
  padding: 22px;
  display: flex;
  gap: 18px;
  align-items: flex-start;
}
.result__poster {
  position: relative;
  width: 84px;
  aspect-ratio: 2 / 3;
  flex: 0 0 auto;
  border-radius: 6px;
  overflow: hidden;
}
.result__poster-title {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  padding: 8px;
  font-family: "Archivo", sans-serif;
  font-weight: 800;
  font-size: 11px;
  line-height: 1.1;
  color: rgba(255, 255, 255, 0.9);
}
.result__body {
  flex: 1 1 auto;
}
.result__badge {
  font-size: 12px;
  font-weight: 700;
  color: var(--sf-success);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.result__badge--pending {
  color: var(--sf-warn);
}
.result__title {
  font-family: "Archivo", sans-serif;
  font-weight: 800;
  font-size: 19px;
  margin: 0 0 6px;
}
.result__meta {
  font-size: 13px;
  color: var(--sf-text-3);
  margin-bottom: 10px;
}
.result__plot {
  font-size: 13.5px;
  line-height: 1.55;
  color: var(--sf-text-3);
  margin: 0 0 14px;
}
.result__btn {
  border: none;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.1);
  color: var(--sf-text);
  font-family: "Manrope", sans-serif;
  font-weight: 600;
  font-size: 13.5px;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background 0.15s;
}
.result__btn:hover {
  background: rgba(255, 255, 255, 0.18);
}
</style>
