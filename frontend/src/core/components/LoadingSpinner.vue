<template>
  <div class="loading-spinner" :class="{ 'fullscreen': fullscreen }">
    <v-progress-circular
      :size="size"
      :width="width"
      :color="color"
      indeterminate
    ></v-progress-circular>
    <p v-if="message" class="mt-4 text-body-1">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  size?: number;
  width?: number;
  color?: string;
  message?: string;
  fullscreen?: boolean;
}>(), {
  size: 64,
  width: 6,
  color: 'primary',
  fullscreen: false,
});
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.loading-spinner.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  z-index: 9999;
}
</style>
