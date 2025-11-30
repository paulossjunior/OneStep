<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from '@/core/stores/auth.store';

const authStore = useAuthStore();

onMounted(() => {
  // Initialize auth on app mount
  authStore.initializeAuth();
});
</script>

<style>
/* Global styles are imported in main.ts */
</style>
