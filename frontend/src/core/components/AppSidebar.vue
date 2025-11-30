<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    permanent
    @click="rail = false"
  >
    <v-list density="compact" nav>
      <v-list-item
        prepend-icon="mdi-view-dashboard"
        title="Dashboard"
        value="dashboard"
        to="/"
      ></v-list-item>

      <v-divider class="my-2"></v-divider>

      <!-- Initiatives -->
      <v-list-group value="initiatives">
        <template v-slot:activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-rocket-launch-outline"
            title="Initiatives"
          ></v-list-item>
        </template>

        <v-list-item
          prepend-icon="mdi-format-list-bulleted"
          title="All Initiatives"
          value="initiatives-list"
          to="/initiatives"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-plus-circle"
          title="New Initiative"
          value="initiatives-create"
          to="/initiatives/create"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-file-tree"
          title="Hierarchy"
          value="initiatives-hierarchy"
          to="/initiatives/hierarchy"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-upload"
          title="Import"
          value="initiatives-import"
          to="/initiatives/import"
        ></v-list-item>
      </v-list-group>

      <!-- Scholarships -->
      <v-list-group value="scholarships">
        <template v-slot:activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-school-outline"
            title="Scholarships"
          ></v-list-item>
        </template>

        <v-list-item
          prepend-icon="mdi-format-list-bulleted"
          title="All Scholarships"
          value="scholarships-list"
          to="/scholarships"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-plus-circle"
          title="New Scholarship"
          value="scholarships-create"
          to="/scholarships/create"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-chart-bar"
          title="Statistics"
          value="scholarships-stats"
          to="/scholarships/statistics"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-upload"
          title="Import"
          value="scholarships-import"
          to="/scholarships/import"
        ></v-list-item>
      </v-list-group>

      <!-- People -->
      <v-list-item
        prepend-icon="mdi-account-group"
        title="People"
        value="people"
        to="/people"
      ></v-list-item>

      <!-- Organizations -->
      <v-list-group value="organizations">
        <template v-slot:activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-office-building"
            title="Organizations"
          ></v-list-item>
        </template>

        <v-list-item
          prepend-icon="mdi-domain"
          title="Units"
          value="org-units"
          to="/organizations/units"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-map-marker"
          title="Campuses"
          value="campuses"
          to="/organizations/campuses"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-book-open-variant"
          title="Knowledge Areas"
          value="knowledge-areas"
          to="/organizations/knowledge-areas"
        ></v-list-item>
      </v-list-group>

      <v-divider class="my-2"></v-divider>

      <!-- Reports -->
      <v-list-item
        prepend-icon="mdi-chart-line"
        title="Reports"
        value="reports"
        to="/reports"
      ></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  rail?: boolean;
}>();

const emit = defineEmits<{
  'update:rail': [value: boolean];
}>();

const drawer = ref(true);
const rail = ref(props.rail || false);
</script>
