<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-file-tree</v-icon>
      {{ t('initiatives.hierarchy.title') }}
    </v-card-title>

    <v-card-text>
      <LoadingSpinner v-if="loading" />
      
      <v-alert v-else-if="error" type="error" variant="tonal">
        {{ error }}
      </v-alert>

      <div v-else-if="hierarchy">
        <HierarchyNode
          :node="hierarchy"
          :level="0"
          @select="handleSelect"
        />
      </div>

      <v-alert v-else type="info" variant="tonal">
        {{ t('initiatives.hierarchy.noData') }}
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useInitiativeHierarchy } from '../composables/useInitiativeHierarchy';
import LoadingSpinner from '@/core/components/LoadingSpinner.vue';
import HierarchyNode from './HierarchyNode.vue';
import type { InitiativeHierarchy } from '../types/initiative.types';

interface Props {
  initiativeId?: number | null;
}

interface Emits {
  (e: 'select', initiative: InitiativeHierarchy): void;
}

const props = withDefaults(defineProps<Props>(), {
  initiativeId: null,
});

const emit = defineEmits<Emits>();
const { t } = useI18n();

// Use hierarchy composable
const id = computed(() => props.initiativeId);
const { hierarchy, isLoading: loading, error: queryError } = useInitiativeHierarchy(id);

const error = computed(() => 
  queryError.value ? t('initiatives.hierarchy.error') : null
);

// Methods
const handleSelect = (initiative: InitiativeHierarchy) => {
  emit('select', initiative);
};
</script>
