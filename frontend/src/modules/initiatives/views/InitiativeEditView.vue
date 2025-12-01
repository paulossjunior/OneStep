<template>
  <div class="initiative-edit">
    <LoadingSpinner v-if="isLoading" />

    <v-alert v-else-if="error" type="error" variant="tonal">
      {{ error }}
    </v-alert>

    <v-container v-else-if="initiative">
      <v-row justify="center">
        <v-col cols="12" md="10" lg="8">
          <div class="d-flex align-center mb-4">
            <v-btn
              icon="mdi-arrow-left"
              variant="text"
              @click="router.back()"
            />
            <h1 class="text-h5 ml-2">{{ t('initiatives.edit.title') }}</h1>
          </div>

          <InitiativeForm
            :initial-data="formData"
            :loading="isUpdating"
            @submit="handleSubmit"
            @cancel="handleCancel"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useInitiative } from '../composables/useInitiatives';
import { useUpdateInitiativeHandler } from '../handlers/initiative.handlers';
import LoadingSpinner from '@/core/components/LoadingSpinner.vue';
import InitiativeForm from '../components/InitiativeForm.vue';
import type { InitiativeFormData } from '../types/initiative.types';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();

const initiativeId = computed(() => Number(route.params.id));
const { initiative, isLoading, error: queryError } = useInitiative(initiativeId);
const { handleUpdate, isUpdating } = useUpdateInitiativeHandler(initiativeId.value);

const error = computed(() => 
  queryError.value ? t('initiatives.edit.error') : null
);

const formData = computed<Partial<InitiativeFormData>>(() => {
  if (!initiative.value) return {};
  
  return {
    name: initiative.value.name,
    description: initiative.value.description,
    type: initiative.value.type,
    start_date: initiative.value.start_date,
    end_date: initiative.value.end_date,
    coordinator_id: initiative.value.coordinator.id,
    parent_id: initiative.value.parent_id,
    team_member_ids: initiative.value.team_members.map(m => m.id),
    student_ids: initiative.value.students.map(s => s.id),
    organizational_group_ids: initiative.value.organizational_groups.map(g => g.id),
  };
});

const handleSubmit = async (data: InitiativeFormData) => {
  const success = await handleUpdate(data);
  if (success) {
    router.push(`/initiatives/${initiativeId.value}`);
  }
};

const handleCancel = () => {
  router.back();
};
</script>

<style scoped>
.initiative-edit {
  padding: 24px;
}
</style>
