<template>
  <v-card>
    <v-card-title class="d-flex align-center justify-space-between">
      <div>
        <v-icon class="mr-2">mdi-alert-circle</v-icon>
        {{ t('initiatives.failedImports.title') }}
      </div>
      <v-chip color="error">
        {{ total }} {{ t('initiatives.failedImports.items') }}
      </v-chip>
    </v-card-title>

    <v-card-text>
      <LoadingSpinner v-if="loading" />

      <v-alert v-else-if="error" type="error" variant="tonal">
        {{ error }}
      </v-alert>

      <template v-else-if="failedImports && failedImports.length > 0">
        <v-expansion-panels>
          <v-expansion-panel
            v-for="item in failedImports"
            :key="item.id"
          >
            <v-expansion-panel-title>
              <div class="d-flex align-center justify-space-between w-100">
                <div>
                  <v-chip size="small" color="error" class="mr-2">
                    {{ t('initiatives.failedImports.row') }} {{ item.row_number }}
                  </v-chip>
                  <span class="text-body-2">{{ item.file_name }}</span>
                </div>
                <span class="text-caption text-grey">
                  {{ formatDate(item.created_at) }}
                </span>
              </div>
            </v-expansion-panel-title>

            <v-expansion-panel-text>
              <!-- Data -->
              <div class="mb-4">
                <div class="text-subtitle-2 mb-2">
                  {{ t('initiatives.failedImports.data') }}:
                </div>
                <v-card variant="outlined">
                  <v-card-text>
                    <pre class="text-caption">{{ JSON.stringify(item.data, null, 2) }}</pre>
                  </v-card-text>
                </v-card>
              </div>

              <!-- Errors -->
              <div class="mb-4">
                <div class="text-subtitle-2 mb-2">
                  {{ t('initiatives.failedImports.errors') }}:
                </div>
                <v-alert
                  v-for="(messages, field) in item.errors"
                  :key="field"
                  type="error"
                  variant="tonal"
                  density="compact"
                  class="mb-2"
                >
                  <strong>{{ field }}:</strong> {{ messages.join(', ') }}
                </v-alert>
              </div>

              <!-- Actions -->
              <div class="d-flex gap-2">
                <v-btn
                  color="primary"
                  size="small"
                  prepend-icon="mdi-refresh"
                  :loading="retrying === item.id"
                  @click="handleRetry(item.id)"
                >
                  {{ t('initiatives.failedImports.retry') }}
                </v-btn>
                <v-btn
                  color="error"
                  size="small"
                  variant="outlined"
                  prepend-icon="mdi-delete"
                  :loading="deleting === item.id"
                  @click="handleDelete(item.id)"
                >
                  {{ t('common.delete') }}
                </v-btn>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>

        <!-- Pagination -->
        <div class="d-flex justify-center mt-4">
          <v-pagination
            v-model="currentPage"
            :length="totalPages"
            :total-visible="7"
          />
        </div>
      </template>

      <v-alert v-else type="success" variant="tonal">
        {{ t('initiatives.failedImports.empty') }}
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { format } from 'date-fns';
import { useFailedImports } from '../composables/useFailedImports';
import { useFailedImportHandler } from '../handlers/initiative.handlers';
import LoadingSpinner from '@/core/components/LoadingSpinner.vue';

const { t } = useI18n();

const currentPage = ref(1);
const { failedImports, total, isLoading: loading, error: queryError } = useFailedImports(currentPage);
const { handleRetry, handleDelete, retrying, deleting } = useFailedImportHandler();

const error = computed(() => 
  queryError.value ? t('initiatives.failedImports.error') : null
);

const totalPages = computed(() => Math.ceil(total.value / 10));

const formatDate = (date: string) => {
  return format(new Date(date), 'dd/MM/yyyy HH:mm');
};
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
