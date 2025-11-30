<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-filter" class="mr-2"></v-icon>
      {{ $t('common.filters') }}
      <v-spacer></v-spacer>
      <v-btn
        variant="text"
        size="small"
        @click="handleClear"
        :disabled="!hasActiveFilters"
      >
        {{ $t('common.clearAll') }}
      </v-btn>
    </v-card-title>

    <v-divider></v-divider>

    <v-card-text>
      <slot :filters="filters" :update-filter="updateFilter" />
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="handleClear">
        {{ $t('common.clear') }}
      </v-btn>
      <v-btn color="primary" @click="handleApply">
        {{ $t('common.apply') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

const props = defineProps<{
  modelValue: Record<string, any>;
}>();

const emit = defineEmits<{
  'update:modelValue': [filters: Record<string, any>];
  'apply': [filters: Record<string, any>];
  'clear': [];
}>();

const filters = ref<Record<string, any>>({ ...props.modelValue });

const hasActiveFilters = computed(() => {
  return Object.values(filters.value).some(value => {
    if (Array.isArray(value)) return value.length > 0;
    return value !== null && value !== undefined && value !== '';
  });
});

const updateFilter = (key: string, value: any) => {
  filters.value[key] = value;
};

const handleApply = () => {
  emit('update:modelValue', { ...filters.value });
  emit('apply', { ...filters.value });
};

const handleClear = () => {
  const clearedFilters: Record<string, any> = {};
  Object.keys(filters.value).forEach(key => {
    clearedFilters[key] = Array.isArray(filters.value[key]) ? [] : null;
  });
  filters.value = clearedFilters;
  emit('update:modelValue', clearedFilters);
  emit('clear');
};

watch(() => props.modelValue, (newValue) => {
  filters.value = { ...newValue };
}, { deep: true });
</script>
