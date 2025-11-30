<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-card-title class="text-h5">
        <v-icon :icon="icon" :color="iconColor" class="mr-2"></v-icon>
        {{ title }}
      </v-card-title>

      <v-card-text>
        {{ message }}
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          variant="text"
          @click="handleCancel"
          :disabled="loading"
        >
          {{ cancelText || $t('common.cancel') }}
        </v-btn>
        <v-btn
          :color="confirmColor"
          @click="handleConfirm"
          :loading="loading"
        >
          {{ confirmText || $t('common.confirm') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = withDefaults(defineProps<{
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmColor?: string;
  icon?: string;
  iconColor?: string;
}>(), {
  confirmColor: 'primary',
  icon: 'mdi-help-circle',
  iconColor: 'primary',
});

const emit = defineEmits<{
  'confirm': [];
  'cancel': [];
}>();

const dialog = ref(false);
const loading = ref(false);

const open = () => {
  dialog.value = true;
  loading.value = false;
};

const close = () => {
  dialog.value = false;
  loading.value = false;
};

const handleConfirm = () => {
  loading.value = true;
  emit('confirm');
};

const handleCancel = () => {
  emit('cancel');
  close();
};

defineExpose({
  open,
  close,
});
</script>
