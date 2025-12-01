<template>
  <div class="initiative-detail">
    <LoadingSpinner v-if="isLoading" />

    <v-alert v-else-if="error" type="error" variant="tonal" class="mb-4">
      {{ error }}
    </v-alert>

    <template v-else-if="initiative">
      <!-- Header -->
      <v-card class="mb-4">
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-btn
              icon="mdi-arrow-left"
              variant="text"
              @click="router.back()"
            />
            <h1 class="text-h5 ml-2">{{ initiative.name }}</h1>
          </div>
          <div>
            <v-btn
              v-if="canEdit"
              color="primary"
              prepend-icon="mdi-pencil"
              class="mr-2"
              @click="handleEdit"
            >
              {{ t('common.edit') }}
            </v-btn>
            <v-btn
              v-if="canDelete"
              color="error"
              prepend-icon="mdi-delete"
              variant="outlined"
              @click="handleDelete"
            >
              {{ t('common.delete') }}
            </v-btn>
          </div>
        </v-card-title>

        <v-card-text>
          <v-row>
            <v-col cols="12" md="8">
              <!-- Type Badge -->
              <v-chip
                :color="getTypeColor(initiative.type)"
                class="mb-4"
              >
                {{ t(`initiatives.types.${initiative.type.toLowerCase()}`) }}
              </v-chip>

              <!-- Description -->
              <p class="text-body-1 mb-4">{{ initiative.description }}</p>

              <!-- Dates -->
              <div class="mb-4">
                <v-icon class="mr-2">mdi-calendar</v-icon>
                <strong>{{ t('initiatives.detail.period') }}:</strong>
                {{ formatDate(initiative.start_date) }}
                <span v-if="initiative.end_date">
                  - {{ formatDate(initiative.end_date) }}
                </span>
                <span v-else>
                  - {{ t('initiatives.detail.ongoing') }}
                </span>
              </div>

              <!-- Coordinator -->
              <div class="mb-4">
                <v-icon class="mr-2">mdi-account-tie</v-icon>
                <strong>{{ t('initiatives.detail.coordinator') }}:</strong>
                {{ initiative.coordinator.full_name }}
              </div>

              <!-- Parent -->
              <div v-if="initiative.parent" class="mb-4">
                <v-icon class="mr-2">mdi-file-tree</v-icon>
                <strong>{{ t('initiatives.detail.parent') }}:</strong>
                <router-link :to="`/initiatives/${initiative.parent.id}`">
                  {{ initiative.parent.name }}
                </router-link>
              </div>

              <!-- Organizational Groups -->
              <div v-if="initiative.organizational_groups.length > 0" class="mb-4">
                <v-icon class="mr-2">mdi-domain</v-icon>
                <strong>{{ t('initiatives.detail.groups') }}:</strong>
                <v-chip
                  v-for="group in initiative.organizational_groups"
                  :key="group.id"
                  size="small"
                  class="ml-2"
                >
                  {{ group.name }}
                </v-chip>
              </div>
            </v-col>

            <v-col cols="12" md="4">
              <!-- Metadata -->
              <v-card variant="outlined">
                <v-card-text>
                  <div class="text-caption text-grey mb-2">
                    {{ t('initiatives.detail.created') }}:
                    {{ formatDateTime(initiative.created_at) }}
                  </div>
                  <div class="text-caption text-grey">
                    {{ t('initiatives.detail.updated') }}:
                    {{ formatDateTime(initiative.updated_at) }}
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Team Members -->
      <v-row class="mb-4">
        <v-col cols="12" md="6">
          <TeamMemberList
            :members="initiative.team_members"
            :can-edit="canEdit"
            @add="handleAddTeamMember"
            @remove="handleRemoveTeamMember"
          />
        </v-col>

        <v-col cols="12" md="6">
          <StudentList
            :students="initiative.students"
            :can-edit="canEdit"
            @add="handleAddStudent"
            @remove="handleRemoveStudent"
          />
        </v-col>
      </v-row>

      <!-- Hierarchy -->
      <InitiativeHierarchy
        v-if="initiative.parent_id"
        :initiative-id="initiative.parent_id"
        class="mb-4"
        @select="handleHierarchySelect"
      />
    </template>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      v-model="showDeleteDialog"
      :title="t('initiatives.delete.title')"
      :message="t('initiatives.delete.message')"
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { format } from 'date-fns';
import { useInitiative } from '../composables/useInitiatives';
import { useTeamMemberHandler, useStudentHandler, useDeleteInitiativeHandler } from '../handlers/initiative.handlers';
import { usePermissions } from '@/core/composables/usePermissions';
import LoadingSpinner from '@/core/components/LoadingSpinner.vue';
import ConfirmDialog from '@/core/components/ConfirmDialog.vue';
import TeamMemberList from '../components/TeamMemberList.vue';
import StudentList from '../components/StudentList.vue';
import InitiativeHierarchy from '../components/InitiativeHierarchy.vue';
import type { InitiativeHierarchy as IHierarchy } from '../types/initiative.types';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { hasPermission } = usePermissions();

const initiativeId = computed(() => Number(route.params.id));
const { initiative, isLoading, error: queryError } = useInitiative(initiativeId);

const error = computed(() => 
  queryError.value ? t('initiatives.detail.error') : null
);

// Permissions
const canEdit = computed(() => hasPermission('initiatives.change_initiative'));
const canDelete = computed(() => hasPermission('initiatives.delete_initiative'));

// Team member handlers
const { handleAdd: handleAddTeamMember, handleRemove: handleRemoveTeamMember } = 
  useTeamMemberHandler(initiativeId.value);

// Student handlers
const { handleAdd: handleAddStudent, handleRemove: handleRemoveStudent } = 
  useStudentHandler(initiativeId.value);

// Delete handler
const showDeleteDialog = ref(false);
const { handleDelete: deleteInitiative, isDeleting: deleting } = useDeleteInitiativeHandler();

// Methods
const formatDate = (date: string) => {
  return format(new Date(date), 'dd/MM/yyyy');
};

const formatDateTime = (date: string) => {
  return format(new Date(date), 'dd/MM/yyyy HH:mm');
};

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    PROGRAM: 'primary',
    PROJECT: 'success',
    EVENT: 'warning',
  };
  return colors[type] || 'grey';
};

const handleEdit = () => {
  router.push(`/initiatives/${initiativeId.value}/edit`);
};

const handleDelete = () => {
  showDeleteDialog.value = true;
};

const confirmDelete = async () => {
  await deleteInitiative(initiativeId.value);
  showDeleteDialog.value = false;
  router.push('/initiatives');
};

const handleHierarchySelect = (selected: IHierarchy) => {
  router.push(`/initiatives/${selected.id}`);
};
</script>

<style scoped>
.initiative-detail {
  padding: 24px;
}
</style>
