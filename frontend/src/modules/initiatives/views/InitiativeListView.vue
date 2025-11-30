<template>
  <div>
    <v-row class="mb-4 align-center">
      <v-col cols="12" md="6">
        <h1 class="text-h3">{{ $t('initiatives.title') }}</h1>
        <p class="text-subtitle-1 text-grey">
          {{ total }} {{ total === 1 ? 'initiative' : 'initiatives' }}
        </p>
      </v-col>
      <v-col cols="12" md="6" class="text-right">
        <v-btn
          variant="outlined"
          prepend-icon="mdi-refresh"
          @click="handleRefresh"
          :loading="isLoading"
          class="mr-2"
        >
          {{ $t('common.refresh') }}
        </v-btn>
        <v-btn
          variant="outlined"
          prepend-icon="mdi-download"
          @click="handleExport"
          :loading="isExporting"
          :disabled="items.length === 0"
          class="mr-2"
        >
          {{ $t('common.export') }}
        </v-btn>
        <v-btn
          color="secondary"
          prepend-icon="mdi-upload"
          to="/initiatives/import"
          class="mr-2"
        >
          {{ $t('initiatives.import') }}
        </v-btn>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          to="/initiatives/create"
        >
          {{ $t('initiatives.create') }}
        </v-btn>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <SearchBar
              v-model="searchQuery"
              :placeholder="$t('initiatives.searchPlaceholder')"
              @search="handleSearch"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.type"
              :items="typeOptions"
              :label="$t('initiatives.type')"
              clearable
              variant="outlined"
              density="compact"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.ordering"
              :items="orderingOptions"
              :label="$t('common.sortBy')"
              variant="outlined"
              density="compact"
            ></v-select>
          </v-col>
          <v-col cols="12" md="2">
            <v-btn
              block
              variant="outlined"
              prepend-icon="mdi-filter"
              @click="showAdvancedFilters = !showAdvancedFilters"
              :color="showAdvancedFilters ? 'primary' : undefined"
            >
              {{ $t('common.filters') }}
            </v-btn>
          </v-col>
        </v-row>

        <!-- Advanced Filters -->
        <v-expand-transition>
          <div v-if="showAdvancedFilters">
            <v-divider class="my-4"></v-divider>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="filters.start_date_after"
                  :label="$t('initiatives.startDateAfter')"
                  type="date"
                  variant="outlined"
                  density="compact"
                  clearable
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="filters.end_date_before"
                  :label="$t('initiatives.endDateBefore')"
                  type="date"
                  variant="outlined"
                  density="compact"
                  clearable
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row v-if="hasActiveFilters">
              <v-col cols="12" class="text-right">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-filter-remove"
                  @click="handleClearFilters"
                >
                  {{ $t('common.clearAll') }}
                </v-btn>
              </v-col>
            </v-row>
          </div>
        </v-expand-transition>
      </v-card-text>
    </v-card>

    <!-- Loading State -->
    <LoadingSpinner v-if="isLoading" />

    <!-- Error State -->
    <v-alert v-else-if="isError" type="error" class="mb-4">
      {{ queryError?.message || $t('common.error') }}
    </v-alert>

    <!-- Empty State -->
    <v-card v-else-if="items.length === 0">
      <v-card-text class="text-center py-12">
        <v-icon icon="mdi-rocket-launch-outline" size="64" color="grey"></v-icon>
        <p class="text-h6 mt-4">{{ $t('initiatives.noInitiatives') }}</p>
        <v-btn color="primary" to="/initiatives/create" class="mt-4">
          {{ $t('initiatives.createFirst') }}
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- Initiatives Grid -->
    <v-row v-else>
      <v-col
        v-for="initiative in items"
        :key="initiative.id"
        cols="12"
        md="6"
        lg="4"
      >
        <InitiativeCard
          :initiative="initiative"
          @edit="handleEdit"
          @delete="handleDelete"
        />
      </v-col>
    </v-row>

    <!-- Pagination -->
    <v-row v-if="total > pageSize" class="mt-4">
      <v-col cols="12" class="d-flex justify-center">
        <v-pagination
          v-model="page"
          :length="Math.ceil(total / pageSize)"
          :total-visible="7"
        ></v-pagination>
      </v-col>
    </v-row>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      ref="deleteDialog"
      :title="$t('initiatives.deleteTitle')"
      :message="$t('initiatives.deleteMessage')"
      confirm-color="error"
      icon="mdi-delete"
      icon-color="error"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useInitiatives } from '../composables/useInitiatives';
import { useDeleteInitiativeHandler, useSearchHandler, useExportHandler } from '../handlers/initiative.handlers';
import { InitiativeType } from '../types/initiative.types';
import type { Initiative } from '../types/initiative.types';
import InitiativeCard from '../components/InitiativeCard.vue';
import SearchBar from '@/core/components/SearchBar.vue';
import LoadingSpinner from '@/core/components/LoadingSpinner.vue';
import ConfirmDialog from '@/core/components/ConfirmDialog.vue';

const router = useRouter();

// Pagination
const page = ref(1);
const pageSize = ref(12);
const showAdvancedFilters = ref(false);

// Search handler
const { searchQuery, debouncedSearch, handleSearch: onSearch, clearSearch } = useSearchHandler();

// Filters
const filters = reactive({
  search: '',
  type: '' as InitiativeType | '',
  ordering: '-created_at',
  start_date_after: '',
  end_date_before: '',
});

// Watch debounced search and update filters
watch(debouncedSearch, (value) => {
  filters.search = value;
  page.value = 1;
});

// Composable for data fetching
const filtersRef = computed(() => ({
  ...filters,
  page: page.value,
  page_size: pageSize.value,
}));

const { items, total, isLoading, isError, queryError, refetch } = useInitiatives(filtersRef);

// Delete handler
const { handleDelete: deleteHandler, isDeleting } = useDeleteInitiativeHandler();
const deleteDialog = ref();
const initiativeToDelete = ref<Initiative | null>(null);

// Export handler
const { handleExportCSV, isExporting } = useExportHandler();

// Type options for filter
const typeOptions = [
  { title: 'Program', value: InitiativeType.PROGRAM },
  { title: 'Project', value: InitiativeType.PROJECT },
  { title: 'Event', value: InitiativeType.EVENT },
];

// Ordering options
const orderingOptions = [
  { title: 'Newest First', value: '-created_at' },
  { title: 'Oldest First', value: 'created_at' },
  { title: 'Name (A-Z)', value: 'name' },
  { title: 'Name (Z-A)', value: '-name' },
  { title: 'Start Date', value: 'start_date' },
];

// Computed
const hasActiveFilters = computed(() => {
  return (
    filters.search ||
    filters.type ||
    filters.start_date_after ||
    filters.end_date_before
  );
});

// Methods
const handleSearch = (value: string) => {
  onSearch(value);
};

const handleEdit = (initiative: Initiative) => {
  router.push(`/initiatives/${initiative.id}/edit`);
};

const handleDelete = (initiative: Initiative) => {
  initiativeToDelete.value = initiative;
  deleteDialog.value.open();
};

const confirmDelete = async () => {
  if (initiativeToDelete.value) {
    try {
      await deleteHandler(initiativeToDelete.value, '/initiatives');
      deleteDialog.value.close();
      initiativeToDelete.value = null;
      refetch();
    } catch (error) {
      // Error is handled by the handler
      deleteDialog.value.close();
    }
  }
};

const handleClearFilters = () => {
  filters.search = '';
  filters.type = '';
  filters.start_date_after = '';
  filters.end_date_before = '';
  clearSearch();
  page.value = 1;
};

const handleExport = async () => {
  if (items.value.length > 0) {
    await handleExportCSV(items.value);
  }
};

const handleRefresh = () => {
  refetch();
};

// Watch page changes and scroll to top
watch(page, () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Watch filter changes and reset page
watch(
  () => [filters.type, filters.ordering, filters.start_date_after, filters.end_date_before],
  () => {
    page.value = 1;
  }
);
</script>
