<template>
  <v-form ref="formRef" @submit.prevent="handleSubmit">
    <v-card>
      <v-card-title>
        {{ isEditMode ? t('initiatives.form.editTitle') : t('initiatives.form.createTitle') }}
      </v-card-title>

      <v-card-text>
        <v-row>
          <!-- Name -->
          <v-col cols="12">
            <v-text-field
              v-model="formData.name"
              :label="t('initiatives.form.name')"
              :rules="[rules.required]"
              :error-messages="errors.name"
              required
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- Description -->
          <v-col cols="12">
            <v-textarea
              v-model="formData.description"
              :label="t('initiatives.form.description')"
              :rules="[rules.required]"
              :error-messages="errors.description"
              rows="3"
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- Type -->
          <v-col cols="12" md="6">
            <v-select
              v-model="formData.type"
              :label="t('initiatives.form.type')"
              :items="typeOptions"
              :rules="[rules.required]"
              :error-messages="errors.type"
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- Parent Initiative -->
          <v-col cols="12" md="6">
            <v-autocomplete
              v-model="formData.parent_id"
              :label="t('initiatives.form.parent')"
              :items="parentOptions"
              :loading="loadingParents"
              :error-messages="errors.parent_id"
              item-title="name"
              item-value="id"
              clearable
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- Start Date -->
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.start_date"
              :label="t('initiatives.form.startDate')"
              :rules="[rules.required]"
              :error-messages="errors.start_date"
              type="date"
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- End Date -->
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.end_date"
              :label="t('initiatives.form.endDate')"
              :error-messages="errors.end_date"
              type="date"
              clearable
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- Coordinator -->
          <v-col cols="12">
            <v-autocomplete
              v-model="formData.coordinator_id"
              :label="t('initiatives.form.coordinator')"
              :items="peopleOptions"
              :loading="loadingPeople"
              :rules="[rules.required]"
              :error-messages="errors.coordinator_id"
              item-title="full_name"
              item-value="id"
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- Team Members -->
          <v-col cols="12">
            <v-autocomplete
              v-model="formData.team_member_ids"
              :label="t('initiatives.form.teamMembers')"
              :items="peopleOptions"
              :loading="loadingPeople"
              :error-messages="errors.team_member_ids"
              item-title="full_name"
              item-value="id"
              multiple
              chips
              closable-chips
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- Students -->
          <v-col cols="12">
            <v-autocomplete
              v-model="formData.student_ids"
              :label="t('initiatives.form.students')"
              :items="peopleOptions"
              :loading="loadingPeople"
              :error-messages="errors.student_ids"
              item-title="full_name"
              item-value="id"
              multiple
              chips
              closable-chips
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- Organizational Groups -->
          <v-col cols="12">
            <v-autocomplete
              v-model="formData.organizational_group_ids"
              :label="t('initiatives.form.organizationalGroups')"
              :items="groupOptions"
              :loading="loadingGroups"
              :error-messages="errors.organizational_group_ids"
              item-title="name"
              item-value="id"
              multiple
              chips
              closable-chips
              variant="outlined"
              density="comfortable"
            />
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="handleCancel"
        >
          {{ t('common.cancel') }}
        </v-btn>
        <v-btn
          type="submit"
          color="primary"
          :loading="loading"
          variant="elevated"
        >
          {{ isEditMode ? t('common.update') : t('common.create') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import type { InitiativeFormData } from '../types/initiative.types';

interface Props {
  initialData?: Partial<InitiativeFormData>;
  loading?: boolean;
}

interface Emits {
  (e: 'submit', data: InitiativeFormData): void;
  (e: 'cancel'): void;
}

const props = withDefaults(defineProps<Props>(), {
  initialData: () => ({}),
  loading: false,
});

const emit = defineEmits<Emits>();
const { t } = useI18n();

// Form ref
const formRef = ref();

// Form data
const formData = ref<InitiativeFormData>({
  name: '',
  description: '',
  type: 'PROJECT',
  start_date: '',
  end_date: null,
  coordinator_id: 0,
  parent_id: null,
  team_member_ids: [],
  student_ids: [],
  organizational_group_ids: [],
  ...props.initialData,
});

// Validation errors
const errors = ref<Record<string, string>>({});

// Mock data (replace with actual API calls)
const loadingParents = ref(false);
const loadingPeople = ref(false);
const loadingGroups = ref(false);

const parentOptions = ref([
  { id: 1, name: 'Programa de Extensão Rural' },
  { id: 4, name: 'Programa de Pesquisa em Sustentabilidade' },
]);

const peopleOptions = ref([
  { id: 1, full_name: 'Maria Silva' },
  { id: 2, full_name: 'João Santos' },
  { id: 3, full_name: 'Ana Costa' },
  { id: 4, full_name: 'Carlos Rodrigues' },
]);

const groupOptions = ref([
  { id: 1, name: 'Grupo de Pesquisa em Agroecologia' },
  { id: 2, name: 'Centro de Inovação Tecnológica' },
  { id: 3, name: 'Laboratório de Sustentabilidade' },
]);

// Type options
const typeOptions = computed(() => [
  { value: 'PROGRAM', title: t('initiatives.types.program') },
  { value: 'PROJECT', title: t('initiatives.types.project') },
  { value: 'EVENT', title: t('initiatives.types.event') },
]);

// Validation rules
const rules = {
  required: (value: any) => !!value || t('validation.required'),
};

// Computed
const isEditMode = computed(() => !!props.initialData?.name);

// Watch for initial data changes
watch(
  () => props.initialData,
  (newData) => {
    if (newData) {
      formData.value = {
        ...formData.value,
        ...newData,
      };
    }
  },
  { deep: true }
);

// Methods
const handleSubmit = async () => {
  const { valid } = await formRef.value.validate();
  
  if (valid) {
    errors.value = {};
    emit('submit', formData.value);
  }
};

const handleCancel = () => {
  emit('cancel');
};

// Expose methods for parent component
defineExpose({
  validate: () => formRef.value.validate(),
  reset: () => formRef.value.reset(),
  setErrors: (newErrors: Record<string, string>) => {
    errors.value = newErrors;
  },
});
</script>
