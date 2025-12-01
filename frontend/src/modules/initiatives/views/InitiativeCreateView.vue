<template>
  <div class="initiative-create">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="10" lg="8">
          <div class="d-flex align-center mb-4">
            <v-btn
              icon="mdi-arrow-left"
              variant="text"
              @click="router.back()"
            />
            <h1 class="text-h5 ml-2">{{ t('initiatives.create.title') }}</h1>
          </div>

          <InitiativeForm
            :loading="isCreating"
            @submit="handleSubmit"
            @cancel="handleCancel"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useCreateInitiativeHandler } from '../handlers/initiative.handlers';
import InitiativeForm from '../components/InitiativeForm.vue';
import type { InitiativeFormData } from '../types/initiative.types';

const router = useRouter();
const { t } = useI18n();

const { handleCreate, isCreating } = useCreateInitiativeHandler();

const handleSubmit = async (data: InitiativeFormData) => {
  const success = await handleCreate(data);
  if (success) {
    router.push('/initiatives');
  }
};

const handleCancel = () => {
  router.back();
};
</script>

<style scoped>
.initiative-create {
  padding: 24px;
}
</style>
