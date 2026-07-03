import { createRouter, createWebHistory } from "vue-router";

import HomeView from "../views/HomeView.vue";
import MoviesView from "../views/MoviesView.vue";
import SeriesView from "../views/SeriesView.vue";
import MediaDetailView from "../views/MediaDetailView.vue";
import RegisterView from "../views/RegisterView.vue";

const routes = [
  { path: "/", name: "home", component: HomeView },
  { path: "/filmes", name: "movies", component: MoviesView },
  { path: "/series", name: "series", component: SeriesView },
  {
    path: "/titulo/:id",
    name: "detail",
    component: MediaDetailView,
    props: (route) => ({ id: Number(route.params.id) }),
  },
  { path: "/cadastrar", name: "register", component: RegisterView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;
