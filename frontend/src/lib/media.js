// Helpers determinísticos de apresentação de mídia (cor/pôster/datas).

// hue determinístico por id — estável entre reloads.
export const hueFor = (id) => (Number(id) * 47) % 360;

// Gradiente de fallback do pôster (fileiras/grades/hero).
export const posterBg = (hue) =>
  `linear-gradient(155deg, oklch(0.46 0.13 ${hue}), oklch(0.24 0.09 ${(hue + 40) % 360}))`;

// Variante do gradiente para o detalhe / stills de episódio.
export const posterBg2 = (hue) =>
  `linear-gradient(155deg, oklch(0.42 0.12 ${(hue + 20) % 360}), oklch(0.22 0.08 ${(hue + 60) % 360}))`;

// Monta a URL da imagem (aceita URL absoluta ou path do TMDB).
export const posterSrc = (url) => {
  if (!url) return "";
  return /^https?:/.test(url) ? url : `https://image.tmdb.org/t/p/w500${url}`;
};

// Formata "YYYY-MM-DD" → "dd/mm/aaaa" (ou "—").
export const formatDate = (value) => {
  if (!value) return "—";
  const [y, mo, da] = String(value).split("-");
  if (!y || !mo || !da) return "—";
  return `${da}/${mo}/${y}`;
};

// Nota sempre com uma casa decimal.
export const formatRating = (value) => (Number(value) || 0).toFixed(1);
