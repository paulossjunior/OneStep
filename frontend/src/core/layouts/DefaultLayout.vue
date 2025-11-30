<template>
  <v-app>
    <AppHeader @toggle-sidebar="rail = !rail" />
    
    <AppSidebar v-model:rail="rail" />

    <v-main>
      <v-container fluid class="pa-4">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </v-container>
    </v-main>

    <AppFooter />
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppHeader from '@/core/components/AppHeader.vue';
import AppSidebar from '@/core/components/AppSidebar.vue';
import AppFooter from '@/core/components/AppFooter.vue';

const rail = ref(false);
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
