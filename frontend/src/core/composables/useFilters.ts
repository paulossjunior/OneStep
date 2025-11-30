import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export interface FilterConfig {
  [key: string]: any;
}

export function useFilters<T extends FilterConfig>(initialFilters: T) {
  const route = useRoute();
  const router = useRouter();

  // Initialize filters from URL query params or defaults
  const filters = ref<T>({ ...initialFilters });

  // Load filters from URL on mount
  const loadFiltersFromUrl = () => {
    const query = route.query;
    Object.keys(initialFilters).forEach((key) => {
      if (query[key] !== undefined) {
        const value = query[key];
        // Parse arrays
        if (Array.isArray(initialFilters[key])) {
          filters.value[key] = Array.isArray(value) ? value : [value];
        } else {
          filters.value[key] = value;
        }
      }
    });
  };

  // Update URL when filters change
  const updateUrl = () => {
    const query: Record<string, any> = {};
    
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        if (Array.isArray(value) && value.length > 0) {
          query[key] = value;
        } else if (!Array.isArray(value)) {
          query[key] = value;
        }
      }
    });

    router.push({ query });
  };

  // Update a single filter
  const updateFilter = (key: keyof T, value: any) => {
    filters.value[key] = value;
  };

  // Update multiple filters
  const updateFilters = (newFilters: Partial<T>) => {
    filters.value = { ...filters.value, ...newFilters };
  };

  // Clear all filters
  const clearFilters = () => {
    filters.value = { ...initialFilters };
    router.push({ query: {} });
  };

  // Clear a single filter
  const clearFilter = (key: keyof T) => {
    filters.value[key] = initialFilters[key];
  };

  // Check if any filter is active
  const hasActiveFilters = computed(() => {
    return Object.entries(filters.value).some(([key, value]) => {
      const initialValue = initialFilters[key as keyof T];
      if (Array.isArray(value)) {
        return value.length > 0;
      }
      return value !== initialValue && value !== null && value !== undefined && value !== '';
    });
  });

  // Get active filter count
  const activeFilterCount = computed(() => {
    return Object.entries(filters.value).filter(([key, value]) => {
      const initialValue = initialFilters[key as keyof T];
      if (Array.isArray(value)) {
        return value.length > 0;
      }
      return value !== initialValue && value !== null && value !== undefined && value !== '';
    }).length;
  });

  // Initialize from URL
  loadFiltersFromUrl();

  // Watch for external URL changes
  watch(() => route.query, () => {
    loadFiltersFromUrl();
  });

  return {
    filters,
    updateFilter,
    updateFilters,
    clearFilters,
    clearFilter,
    updateUrl,
    hasActiveFilters,
    activeFilterCount,
  };
}
