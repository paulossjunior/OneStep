import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { computed, type Ref } from 'vue';
import { initiativesApi } from '../api/initiatives.api';
import { useNotifications } from '@/core/composables/useNotifications';

export function useFailedImports(page?: Ref<number>) {
  const queryClient = useQueryClient();
  const { success, error } = useNotifications();

  const {
    data: failedImports,
    isLoading,
    isError,
    error: queryError,
    refetch,
  } = useQuery({
    queryKey: ['failed-imports', page],
    queryFn: () => initiativesApi.getFailedImports({ page: page?.value }),
  });

  const items = computed(() => failedImports.value?.data.results || []);
  const total = computed(() => failedImports.value?.data.count || 0);

  // Retry failed import
  const retryMutation = useMutation({
    mutationFn: (id: number) => initiativesApi.retryFailedImport(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['failed-imports'] });
      queryClient.invalidateQueries({ queryKey: ['initiatives'] });
      success('Import retried successfully');
    },
    onError: (err: any) => {
      error(err.message || 'Failed to retry import');
    },
  });

  // Delete failed import
  const deleteMutation = useMutation({
    mutationFn: (id: number) => initiativesApi.deleteFailedImport(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['failed-imports'] });
      success('Failed import deleted');
    },
    onError: (err: any) => {
      error(err.message || 'Failed to delete import');
    },
  });

  return {
    items,
    total,
    isLoading,
    isError,
    queryError,
    refetch,
    retry: retryMutation.mutateAsync,
    delete: deleteMutation.mutateAsync,
    isRetrying: retryMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
