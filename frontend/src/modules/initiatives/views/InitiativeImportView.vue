<template>
  <div class="initiative-import">
    <v-container>
      <v-row>
        <v-col cols="12">
          <div class="d-flex align-center mb-4">
            <v-btn
              icon="mdi-arrow-left"
              variant="text"
              @click="router.back()"
            />
            <h1 class="text-h5 ml-2">{{ t('initiatives.import.pageTitle') }}</h1>
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="8">
          <BulkImportUploader />
        </v-col>

        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>
              <v-icon class="mr-2">mdi-information</v-icon>
              {{ t('initiatives.import.instructions') }}
            </v-card-title>
            <v-card-text>
              <div class="text-body-2 mb-4">
                {{ t('initiatives.import.instructionsText') }}
              </div>

              <v-list density="compact">
                <v-list-item>
                  <template #prepend>
                    <v-icon size="small">mdi-numeric-1-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">
                    {{ t('initiatives.import.step1') }}
                  </v-list-item-title>
                </v-list-item>

                <v-list-item>
                  <template #prepend>
                    <v-icon size="small">mdi-numeric-2-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">
                    {{ t('initiatives.import.step2') }}
                  </v-list-item-title>
                </v-list-item>

                <v-list-item>
                  <template #prepend>
                    <v-icon size="small">mdi-numeric-3-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">
                    {{ t('initiatives.import.step3') }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>

              <v-divider class="my-4" />

              <v-btn
                color="primary"
                variant="outlined"
                prepend-icon="mdi-download"
                block
                @click="downloadTemplate"
              >
                {{ t('initiatives.import.downloadTemplate') }}
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-btn
            color="error"
            variant="text"
            prepend-icon="mdi-alert-circle"
            @click="router.push('/initiatives/failed-imports')"
          >
            {{ t('initiatives.import.viewFailed') }}
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import BulkImportUploader from '../components/BulkImportUploader.vue';

const router = useRouter();
const { t } = useI18n();

const downloadTemplate = () => {
  // Create CSV template
  const headers = ['name', 'description', 'type', 'start_date', 'end_date', 'coordinator_id', 'parent_id'];
  const example = ['Example Project', 'Project description', 'PROJECT', '2024-01-01', '2024-12-31', '1', ''];
  
  const csv = [headers.join(','), example.join(',')].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'initiatives_template.csv';
  a.click();
  window.URL.revokeObjectURL(url);
};
</script>

<style scoped>
.initiative-import {
  padding: 24px;
}
</style>
