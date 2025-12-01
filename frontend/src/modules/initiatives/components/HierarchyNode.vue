<template>
  <div :class="['hierarchy-node', `level-${level}`]">
    <div class="node-content" @click="handleClick">
      <v-btn
        v-if="hasChildren"
        :icon="expanded ? 'mdi-chevron-down' : 'mdi-chevron-right'"
        size="x-small"
        variant="text"
        @click.stop="toggleExpanded"
      />
      <v-icon v-else size="x-small" class="mr-2">mdi-circle-small</v-icon>

      <v-chip
        :color="getTypeColor(node.type)"
        size="small"
        class="mr-2"
      >
        {{ t(`initiatives.types.${node.type.toLowerCase()}`) }}
      </v-chip>

      <span class="node-name">{{ node.name }}</span>

      <v-chip size="small" variant="outlined" class="ml-2">
        {{ node.coordinator.full_name }}
      </v-chip>
    </div>

    <v-expand-transition>
      <div v-if="expanded && hasChildren" class="node-children">
        <HierarchyNode
          v-for="child in node.children"
          :key="child.id"
          :node="child"
          :level="level + 1"
          @select="$emit('select', $event)"
        />
      </div>
    </v-expand-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { InitiativeHierarchy } from '../types/initiative.types';

interface Props {
  node: InitiativeHierarchy;
  level: number;
}

interface Emits {
  (e: 'select', initiative: InitiativeHierarchy): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();
const { t } = useI18n();

const expanded = ref(props.level === 0);

const hasChildren = computed(() => 
  props.node.children && props.node.children.length > 0
);

const toggleExpanded = () => {
  expanded.value = !expanded.value;
};

const handleClick = () => {
  emit('select', props.node);
};

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    PROGRAM: 'primary',
    PROJECT: 'success',
    EVENT: 'warning',
  };
  return colors[type] || 'grey';
};
</script>

<style scoped>
.hierarchy-node {
  margin-left: 0;
}

.level-1 { margin-left: 24px; }
.level-2 { margin-left: 48px; }
.level-3 { margin-left: 72px; }
.level-4 { margin-left: 96px; }

.node-content {
  display: flex;
  align-items: center;
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.node-content:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.node-name {
  font-weight: 500;
  flex: 1;
}

.node-children {
  margin-top: 4px;
}
</style>
