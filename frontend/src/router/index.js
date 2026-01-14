import store from "@/store";
import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    redirect: "/code",
  },
  {
    path: "/code",
    component: () => import("@/views/Home.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/overview",
    component: () => import("@/views/Overview.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/overview/:object",
    component: () => import("@/views/OverviewDetail.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/login",
    component: () => import("@/views/Login.vue"),
  },
  {
    path: "/models",
    component: () => import("@/views/rest/Models.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/analyzers",
    component: () => import("@/views/rest/Analyzers.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/vulnerability",
    component: () => import("@/views/rest/Vulnerability.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/rule",
    component: () => import("@/views/rest/Rule.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  store.dispatch("getUser");
  const isAuthenticated = !!localStorage.getItem("LLMAccess");

  if (isAuthenticated && to.path === "/login") {
    next("/code");
    return;
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login");
    return;
  }

  next();
});

export default router;
