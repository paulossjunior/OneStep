<template>
  <v-card>
    <v-card-title>
      <v-icon class="mr-2">mdi-history</v-icon>
      {{ t('initiatives.coordinatorChanges.title') }}
    </v-card-title>

    <v-card-text>
      <LoadingSpinner v-if="loading" />

      <v-alert v-else-if="error" type="error" variant="tonal">
        {{ error }}
      </v-alert>

      <v-timeline v-else-if="changes && changes.length > 0" side="end" density="compact">
        <v-timeline-item
          v-for="change in changes"
          :key="change.id"
          dot-color="primary"
          size="small"
        >
          <template #opposite>
            <div class="text-caption text-grey">
              {{ formatDate(change.changed_at) }}
            </div>
          </template>

          <v-card variant="outlined">
            <v-card-text>
              <div class="d-flex align-center mb-2">
                <v-avatar size="32" color="error" class="mr-2">
                  <v-icon size="small">mdi-account-minus</v-icon>
                </v-avatar>
                <div>
                  <div class="text-caption text-grey">
                    {{ t('initiatives.coordinatorChanges.previous') }}
                  </div>
                  <div class="text-body-2 font-weight-medium">
                    {{ change.previous_coordinator.full_name }}
                  </div>
                </div>
              </div>

              <v-icon class="mx-4">mdi-arrow-down</v-icon>

              <div class="d-flex align-center mb-2">
                <v-avatar size="32" color="success" class="mr-2">
                  <v-icon size="small">mdi-account-plus</v-icon>
                </v-avatar>
                <div>
                  <div class="text-caption text-grey">
                    {{ t('initiatives.coordinatorChanges.new') }}
                  </div>
                  <div class="text-body-2 font-weight-medium">
                    {{ change.new_coordinator.full_name }}
                  </div>
                </div>
              </div>

              <v-divider class="my-2" />

              <div class="text-caption text-grey">
                {{ t('initiatives.coordinatorChanges.changedBy') }}:
                {{ change.changed_by.full_name }}
              </div>

              <div v-if="change.reason" class="text-caption mt-2">
                <strong>{{ t('initiatives.coordinatorChanges.reason') }}:</strong>
                {{ change.reason }}
              </div>
            </v-card-text>
          </v-card>
        </v-timeline-item>
      </v-timeline>

      <v-alert v-else type="info" variant="tonal">
        {{ t('initiatives.coordinatorChanges.empty') }}
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useQuery } from '@tanstack/vue-query';
import { format } from 'date-fns';
import { initiativesApi } from '../api/initiatives.api';
import LoadingSpinner from '@/core/components/LoadingSpinner.vue';

interface Props {
  initiativeId: number;
}

const props = defineProps<Props>();
const { t } = useI18n();

const { data: changes, isLoading: loading, error: queryError } = useQuery({
  queryKey: ['coordinatorChanges', props.initiativeId],
  queryFn: () => initiativesApi.getCoordinatorChanges(props.initiativeId),
});

const error = computed(() => 
  queryError.value ? t('initiatives.coordinatorChanges.error') : null
);

const formatDate = (date: string) => {
  return format(new Date(date), 'dd/MM/yyyy HH:mm');
};
</script>
