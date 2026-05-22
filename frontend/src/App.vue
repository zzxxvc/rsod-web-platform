<template>
  <router-view v-if="isAuthPage" />
  <MainLayout v-else>
    <template #sidebar v-if="showSidebar">
      <Sidebar />
    </template>
    <template #header>
      <Header />
    </template>
    <template #content>
      <router-view />
    </template>
  </MainLayout>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import MainLayout from "./layouts/MainLayout.vue";
import Sidebar from "./components/Sidebar.vue";
import Header from "./components/Header.vue";

const route = useRoute();

const isAuthPage = computed(() => {
  const authPaths = ["/login", "/register", "/forgot-password"];
  return authPaths.includes(route.path);
});

const showSidebar = computed(() => {
  if (isAuthPage.value) return false;
  // hide global sidebar for pages that use their own left panel
  const hideFor = ["/detection", "/history", "/qa", "/targets", "/profile"];
  return !hideFor.includes(route.path);
});
</script>

<style scoped></style>
