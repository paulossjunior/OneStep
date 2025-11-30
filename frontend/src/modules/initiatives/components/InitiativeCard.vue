<template>
  <v-card :to="`/initiatives/${initiative.id}`" hover>
    <v-card-title class="d-flex align-center">
      <v-icon :icon="typeIcon" :color="typeColor" class="mr-2"></v-icon>
      {{ initiative.name }}
    </v-card-title>

    <v-card-subtitle>
      {{ $t(`initiatives.types.${initiative.type}`) }}
    </v-card-subtitle>

    <v-card-text>
      <p class="text-body-2 mb-3">{{ truncatedDescription }}</p>

      <v-chip size="small" class="mr-2" prepend-icon="mdi-account">
        {{ initiative.coordinator.full_name || `${initiative.coordinator.first_name} ${initiative.coordinator.last_name}` }}
      </v-chip>

      <v-chip v-if="initiative.team_members.length" size="small" class="mr-2" prepend-icon="mdi-account-group">
        {{ initiative.team_members.length }} {{ $t('initiatives.teamMembers') }}
      </v-chip>

      <v-chip v-if="initiative.students.length" size="small" prepend-icon="mdi-school">
        {{ initiative.students.length }} {{ $t('initiatives.students') }}
      </v-chip>
    </v-card-text>

    <v-card-text>
      <div class="text-caption">
        <v-icon icon="mdi-calendar-start" size="small"></v-icon>
        {{ formatDate(initiative.start_date) }}
        <span v-if="initiative.end_date">
          - <v-icon icon="mdi-calendar-end" size="small"></v-icon>
          {{ formatDate(initiative.end_date) }}
        </span>
      </div>
    </v-card-text>

    <v-card-actions v-if="showActions">
      <v-spacer></v-spacer>
      <v-btn
        icon="mdi-pencil"
        size="small"
        variant="text"
        @click.prevent="$emit('edit', initiative)"
      ></v-btn>
      <v-btn
        icon="mdi-delete"
        size="small"
        variant="text"
        color="error"
        @click.prevent="$emit('delete', initiative)"
      ></v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { format } from 'date-fns';
import type { Initiative } from '../types/initiative.types';
import { InitiativeType } from '../types/initiative.types';

const props = withDefaults(
  defineProps<{
    initiative: Initiative;
    showActions?: boolean;
  }>(),
  {
    showActions: true,
  }
);

defineEmits<{
  edit: [initiative: Initiative];
  delete: [initiative: Initiative];
}>();

const typeIcon = computed(() => {
  switch (props.initiative.type) {
    case InitiativeType.PROGRAM:
      return 'mdi-folder-multiple';
    case InitiativeType.PROJECT:
      return 'mdi-briefcase';
    case InitiativeType.EVENT:
      return 'mdi-calendar-star';
    default:
      return 'mdi-file';
  }
});

const typeColor = computed(() => {
  switch (props.initiative.type) {
    case InitiativeType.PROGRAM:
      return 'primary';
    case InitiativeType.PROJECT:
      return 'success';
    case InitiativeType.EVENT:
      return 'warning';
    default:
      return 'grey';
  }
});

const truncatedDescription = computed(() => {
  const maxLength = 150;
  if (props.initiative.description.length <= maxLength) {
    return props.initiative.description;
  }
  return props.initiative.description.substring(0, maxLength) + '...';
});

const formatDate = (date: string) => {
  return format(new Date(date), 'MMM dd, yyyy');
};
</script>
