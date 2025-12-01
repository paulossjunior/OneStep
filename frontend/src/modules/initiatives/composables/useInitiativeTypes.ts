import { useQuery } from '@tanstack/vue-query';
import { computed } from 'vue';
import { initiativesApi } from '../api/initiatives.api';
import type { InitiativeTypeOption } from '../types/initiative.types';

export function useInitiativeTypes() {
    const {
        data,
        isLoading,
        isError,
        error,
        refetch,
    } = useQuery({
        queryKey: ['initiativeTypes'],
        queryFn: async () => {
            const response = await initiativesApi.getTypes();
            return response.data.types;
        },
        staleTime: 1000 * 60 * 60, // 1 hour - types don't change often
    });

    const types = computed(() => data.value as InitiativeTypeOption[] | undefined);

    return {
        types,
        isLoading,
        isError,
        error,
        refetch,
    };
}
