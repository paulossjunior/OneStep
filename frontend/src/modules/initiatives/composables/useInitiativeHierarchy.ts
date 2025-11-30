import { useQuery } from '@tanstack/vue-query';
import { computed, type Ref } from 'vue';
import { initiativesApi } from '../api/initiatives.api';

export function useInitiativeHierarchy(id?: Ref<number | null>) {
  const {
    data: hierarchy,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['initiative-hierarchy', id],
    queryFn: () => initiativesApi.getHierarchy(id?.value || undefined),
  });

  const tree = computed(() => hierarchy.value?.data || []);

  return {
    tree,
    isLoading,
    isError,
    error,
    refetch,
  };
}
