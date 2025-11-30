<template>
  <v-footer app class="bg-grey-lighten-3">
    <v-row justify="center" no-gutters>
      <v-col class="text-center py-2" cols="12">
        <span class="text-body-2">
          © {{ currentYear }} OneStep. {{ $t('common.allRightsReserved') }}
        </span>
        <v-divider vertical class="mx-4"></v-divider>
        <span class="text-body-2">
          v{{ appVersion }}
        </span>
      </v-col>
    </v-row>
  </v-footer>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());
const appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0';
</script>
