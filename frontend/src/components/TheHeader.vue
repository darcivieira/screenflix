<script setup>
import StatusPill from "./StatusPill.vue";
</script>

<template>
  <header class="header sf-gutter">
    <RouterLink :to="{ name: 'home' }" class="logo">
      <span class="logo__brand">SCREEN</span><span class="logo__rest">FLIX</span>
    </RouterLink>

    <nav class="nav">
      <RouterLink :to="{ name: 'home' }" class="nav__link">Início</RouterLink>
      <RouterLink :to="{ name: 'movies' }" class="nav__link">Filmes</RouterLink>
      <RouterLink :to="{ name: 'series' }" class="nav__link">Séries</RouterLink>
    </nav>

    <div class="header__right">
      <StatusPill />
      <RouterLink :to="{ name: 'register' }" class="btn-register">
        <span class="btn-register__plus">+</span> Cadastrar
      </RouterLink>
      <div class="avatar">S</div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  gap: 28px;
  padding-top: 14px;
  padding-bottom: 14px;
  background: linear-gradient(
    180deg,
    rgba(15, 15, 17, 0.96),
    rgba(15, 15, 17, 0.72) 70%,
    rgba(15, 15, 17, 0)
  );
  backdrop-filter: blur(6px);
}

.logo {
  font-family: "Archivo", sans-serif;
  font-weight: 900;
  font-size: 23px;
  letter-spacing: -0.02em;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
.logo__brand {
  color: var(--sf-accent);
}
.logo__rest {
  color: var(--sf-text);
}

.nav {
  display: flex;
  gap: 24px;
  align-items: center;
}
.nav__link {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--sf-nav-idle);
  transition: color 0.15s;
}
.nav__link:hover {
  color: var(--sf-text-2);
}
.nav__link.router-link-exact-active {
  color: var(--sf-nav-active);
}

.header__right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-register {
  display: flex;
  align-items: center;
  gap: 7px;
  border: none;
  cursor: pointer;
  background: var(--sf-accent);
  color: #fff;
  font-family: "Manrope", sans-serif;
  font-weight: 700;
  font-size: 14px;
  padding: 9px 16px;
  border-radius: 5px;
  transition: background 0.15s;
}
.btn-register:hover {
  background: var(--sf-accent-hover);
}
.btn-register__plus {
  font-size: 17px;
  line-height: 1;
  margin-top: -1px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 5px;
  background: linear-gradient(135deg, #e50914, #8a0009);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  font-family: "Archivo", sans-serif;
}

@media (max-width: 640px) {
  .header {
    flex-wrap: wrap;
    gap: 14px 20px;
  }
  .header__right {
    gap: 12px;
  }
}
</style>
