<template>
  <div class="data-table">
    <v-data-table
      :headers="headers"
      :items="items"
      :loading="loading"
      :items-per-page="itemsPerPage"
      :page="page"
      :server-items-length="totalItems"
      @update:options="handleOptionsUpdate"
      class="elevation-1"
    >
      <!-- Pass through all slots -->
      <template v-for="(_, slot) in $slots" v-slot:[slot]="scope">
        <slot :name="slot" v-bind="scope" />
      </template>

      <!-- Loading slot -->
      <template v-slot:loading>
        <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
      </template>

      <!-- No data slot -->
      <template v-slot:no-data>
        <v-empty-state
          icon="mdi-database-off"
          :text="$t('common.noData')"
        ></v-empty-state>
      </template>
    </v-data-table>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

interface DataTableHeader {
  title: string;
  key: string;
  sortable?: boolean;
  align?: 'start' | 'center' | 'end';
}

interface DataTableOptions {
  page: number;
  itemsPerPage: number;
  sortBy?: Array<{ key: string; order: 'asc' | 'desc' }>;
}

const props = defineProps<{
  headers: DataTableHeader[];
  items: any[];
  loading?: boolean;
  totalItems?: number;
  itemsPerPage?: number;
  page?: number;
}>();

const emit = defineEmits<{
  'update:options': [options: DataTableOptions];
  'update:page': [page: number];
  'update:itemsPerPage': [itemsPerPage: number];
}>();

const page = ref(props.page || 1);
const itemsPerPage = ref(props.itemsPerPage || 10);

const handleOptionsUpdate = (options: any) => {
  page.value = options.page;
  itemsPerPage.value = options.itemsPerPage;
  
  emit('update:options', {
    page: options.page,
    itemsPerPage: options.itemsPerPage,
    sortBy: options.sortBy,
  });
  
  emit('update:page', options.page);
  emit('update:itemsPerPage', options.itemsPerPage);
};

watch(() => props.page, (newPage) => {
  if (newPage !== undefined) {
    page.value = newPage;
  }
});

watch(() => props.itemsPerPage, (newItemsPerPage) => {
  if (newItemsPerPage !== undefined) {
    itemsPerPage.value = newItemsPerPage;
  }
});
</script>
