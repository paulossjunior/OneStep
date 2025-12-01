<template>
  <v-card>
    <v-card-title>
      <v-icon class="mr-2">mdi-upload</v-icon>
      {{ t('initiatives.import.title') }}
    </v-card-title>

    <v-card-text>
      <v-tabs v-model="importType" class="mb-4">
        <v-tab value="csv">
          <v-icon class="mr-2">mdi-file-delimited</v-icon>
          CSV
        </v-tab>
        <v-tab value="zip">
          <v-icon class="mr-2">mdi-folder-zip</v-icon>
          ZIP
        </v-tab>
      </v-tabs>

      <v-window v-model="importType">
        <v-window-item value="csv">
          <v-file-input
            v-model="csvFile"
            :label="t('initiatives.import.selectCsv')"
            accept=".csv"
            prepend-icon="mdi-file-delimited"
            variant="outlined"
            :error-messages="fileError"
            @change="fileError = ''"
          />
          
          <v-alert type="info" variant="tonal" class="mb-4">
            {{ t('initiatives.import.csvInfo') }}
          </v-alert>

          <v-btn
            color="primary"
            :disabled="!csvFile || !csvFile.length"
            :loading="uploading"
            prepend-icon="mdi-upload"
            @click="handleCsvUpload"
          >
            {{ t('initiatives.import.upload') }}
          </v-btn>
        </v-window-item>

        <v-window-item value="zip">
          <v-file-input
            v-model="zipFile"
            :label="t('initiatives.import.selectZip')"
            accept=".zip"
            prepend-icon="mdi-folder-zip"
            variant="outlined"
            :error-messages="fileError"
            @change="fileError = ''"
          />
          
          <v-alert type="info" variant="tonal" class="mb-4">
            {{ t('initiatives.import.zipInfo') }}
          </v-alert>

          <v-btn
            color="primary"
            :disabled="!zipFile || !zipFile.length"
            :loading="uploading"
            prepend-icon="mdi-upload"
            @click="handleZipUpload"
          >
            {{ t('initiatives.import.upload') }}
          </v-btn>
        </v-window-item>
      </v-window>

      <!-- Upload Progress -->
      <v-progress-linear
        v-if="uploading"
        indeterminate
        color="primary"
        class="mt-4"
      />

      <!-- Upload Result -->
      <v-alert
        v-if="uploadResult"
        :type="uploadResult.success ? 'success' : 'error'"
        variant="tonal"
        class="mt-4"
      >
        <div class="text-h6 mb-2">
          {{ uploadResult.success ? t('initiatives.import.success') : t('initiatives.import.error') }}
        </div>
        <div v-if="uploadResult.created_count > 0">
          {{ t('initiatives.import.created', { count: uploadResult.created_count }) }}
        </div>
        <div v-if="uploadResult.updated_count > 0">
          {{ t('initiatives.import.updated', { count: uploadResult.updated_count }) }}
        </div>
        <div v-if="uploadResult.failed_count > 0" class="text-error">
          {{ t('initiatives.import.failed', { count: uploadResult.failed_count }) }}
        </div>
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useImportHandler } from '../handlers/initiative.handlers';
import type { InitiativeImportResult } from '../types/initiative.types';

const { t } = useI18n();
const { handleCsvImport, handleZipImport, isImporting: uploading } = useImportHandler();

const importType = ref('csv');
const csvFile = ref<File[]>([]);
const zipFile = ref<File[]>([]);
const fileError = ref('');
const uploadResult = ref<InitiativeImportResult | null>(null);

const handleCsvUpload = async () => {
  if (!csvFile.value || csvFile.value.length === 0) {
    fileError.value = t('initiatives.import.noFile');
    return;
  }

  uploadResult.value = null;
  const result = await handleCsvImport(csvFile.value[0]);
  
  if (result) {
    uploadResult.value = result;
    if (result.success) {
      csvFile.value = [];
    }
  }
};

const handleZipUpload = async () => {
  if (!zipFile.value || zipFile.value.length === 0) {
    fileError.value = t('initiatives.import.noFile');
    return;
  }

  uploadResult.value = null;
  const result = await handleZipImport(zipFile.value[0]);
  
  if (result) {
    uploadResult.value = result;
    if (result.success) {
      zipFile.value = [];
    }
  }
};
</script>
