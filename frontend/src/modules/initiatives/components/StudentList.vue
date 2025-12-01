<template>
  <v-card>
    <v-card-title class="d-flex align-center justify-space-between">
      <div>
        <v-icon class="mr-2">mdi-school</v-icon>
        {{ t('initiatives.students.title') }}
      </div>
      <v-btn
        v-if="canEdit"
        color="primary"
        size="small"
        prepend-icon="mdi-plus"
        @click="showAddDialog = true"
      >
        {{ t('initiatives.students.add') }}
      </v-btn>
    </v-card-title>

    <v-card-text>
      <v-list v-if="students.length > 0">
        <v-list-item
          v-for="student in students"
          :key="student.id"
          :title="student.full_name"
          :subtitle="student.email"
        >
          <template #prepend>
            <v-avatar color="success">
              <v-icon>mdi-school</v-icon>
            </v-avatar>
          </template>

          <template #append>
            <v-btn
              v-if="canEdit"
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="handleRemove(student.id)"
            />
          </template>
        </v-list-item>
      </v-list>

      <v-alert v-else type="info" variant="tonal">
        {{ t('initiatives.students.empty') }}
      </v-alert>
    </v-card-text>

    <!-- Add Student Dialog -->
    <v-dialog v-model="showAddDialog" max-width="500">
      <v-card>
        <v-card-title>{{ t('initiatives.students.addTitle') }}</v-card-title>
        <v-card-text>
          <v-autocomplete
            v-model="selectedPersonId"
            :label="t('initiatives.students.selectPerson')"
            :items="availablePeople"
            item-title="full_name"
            item-value="id"
            variant="outlined"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showAddDialog = false">
            {{ t('common.cancel') }}
          </v-btn>
          <v-btn
            color="primary"
            :disabled="!selectedPersonId"
            :loading="adding"
            @click="handleAdd"
          >
            {{ t('common.add') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Person } from '../types/initiative.types';

interface Props {
  students: Person[];
  canEdit?: boolean;
}

interface Emits {
  (e: 'add', personId: number): void;
  (e: 'remove', personId: number): void;
}

const props = withDefaults(defineProps<Props>(), {
  canEdit: false,
});

const emit = defineEmits<Emits>();
const { t } = useI18n();

const showAddDialog = ref(false);
const selectedPersonId = ref<number | null>(null);
const adding = ref(false);

// Mock available people (replace with actual API call)
const availablePeople = computed(() => [
  { id: 10, full_name: 'Pedro Oliveira', email: 'pedro.oliveira@example.com' },
  { id: 11, full_name: 'Lucas Ferreira', email: 'lucas.ferreira@example.com' },
  { id: 12, full_name: 'Carla Mendes', email: 'carla.mendes@example.com' },
].filter(person => !props.students.find(s => s.id === person.id)));

const handleAdd = async () => {
  if (selectedPersonId.value) {
    adding.value = true;
    emit('add', selectedPersonId.value);
    showAddDialog.value = false;
    selectedPersonId.value = null;
    adding.value = false;
  }
};

const handleRemove = (personId: number) => {
  emit('remove', personId);
};
</script>
