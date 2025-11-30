<template>
  <v-text-field
    :model-value="modelValue"
    @update:model-value="handleInput"
    :placeholder="placeholder || $t('common.search')"
    prepend-inner-icon="mdi-magnify"
    variant="outlined"
    density="compact"
    hide-details
    clearable
    @click:clear="handleClear"
  >
    <template v-if="$slots.prepend" v-slot:prepend>
      <slot name="prepend" />
    </template>
    <template v-if="$slots.append" v-slot:append>
      <slot name="append" />
    </template>
  </v-text-field>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core';

const props = defineProps<{
  modelValue: string;
  placeholder?: string;
  debounce?: number;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
  'search': [value: string];
}>();

const debouncedSearch = useDebounceFn((value: string) => {
  emit('search', value);
}, props.debounce || 300);

const handleInput = (value: string) => {
  emit('update:modelValue', value);
  debouncedSearch(value);
};

const handleClear = () => {
  emit('update:modelValue', '');
  emit('search', '');
};
</script>
