import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export interface PaginationOptions {
  page?: number;
  pageSize?: number;
  total?: number;
}

export function usePagination(options: PaginationOptions = {}) {
  const route = useRoute();
  const router = useRouter();

  const page = ref(Number(route.query.page) || options.page || 1);
  const pageSize = ref(Number(route.query.page_size) || options.pageSize || 10);
  const total = ref(options.total || 0);

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value));
  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasPreviousPage = computed(() => page.value > 1);
  const startIndex = computed(() => (page.value - 1) * pageSize.value);
  const endIndex = computed(() => Math.min(startIndex.value + pageSize.value, total.value));

  const setPage = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages.value) {
      page.value = newPage;
      updateUrl();
    }
  };

  const setPageSize = (newPageSize: number) => {
    pageSize.value = newPageSize;
    page.value = 1; // Reset to first page
    updateUrl();
  };

  const setTotal = (newTotal: number) => {
    total.value = newTotal;
  };

  const nextPage = () => {
    if (hasNextPage.value) {
      setPage(page.value + 1);
    }
  };

  const previousPage = () => {
    if (hasPreviousPage.value) {
      setPage(page.value - 1);
    }
  };

  const goToFirstPage = () => {
    setPage(1);
  };

  const goToLastPage = () => {
    setPage(totalPages.value);
  };

  const updateUrl = () => {
    router.push({
      query: {
        ...route.query,
        page: page.value.toString(),
        page_size: pageSize.value.toString(),
      },
    });
  };

  // Watch for external URL changes
  watch(() => route.query.page, (newPage) => {
    if (newPage) {
      page.value = Number(newPage);
    }
  });

  watch(() => route.query.page_size, (newPageSize) => {
    if (newPageSize) {
      pageSize.value = Number(newPageSize);
    }
  });

  return {
    page,
    pageSize,
    total,
    totalPages,
    hasNextPage,
    hasPreviousPage,
    startIndex,
    endIndex,
    setPage,
    setPageSize,
    setTotal,
    nextPage,
    previousPage,
    goToFirstPage,
    goToLastPage,
  };
}
