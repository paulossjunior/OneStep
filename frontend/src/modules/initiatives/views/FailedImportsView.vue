<template>
  <div class="failed-imports">
    <v-container>
      <v-row>
        <v-col cols="12">
          <div class="d-flex align-center mb-4">
            <v-btn
              icon="mdi-arrow-left"
              variant="text"
              @click="router.back()"
            />
            <h1 class="text-h5 ml-2">{{ t('initiatives.failedImports.pageTitle') }}</h1>
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <FailedImportList />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import FailedImportList from '../components/FailedImportList.vue';

const router = useRouter();
const { t } = useI18n();
</script>

<style scoped>
.failed-imports {
  padding: 24px;
}
</style>
