import { useMutation, useQueryClient } from '@tanstack/vue-query';
import { ref } from 'vue';
import { initiativesApi } from '../api/initiatives.api';
import { useNotifications } from '@/core/composables/useNotifications';
import type { InitiativeImportResult } from '../types/initiative.types';

export function useInitiativeImport() {
  const queryClient = useQueryClient();
  const { success, error } = useNotifications();
  const importResult = ref<InitiativeImportResult | null>(null);

  // Import CSV
  const importCSVMutation = useMutation({
    mutationFn: (file: File) => initiativesApi.importCSV(file),
    onSuccess: (response) => {
      importResult.value = response.data;
      queryClient.invalidateQueries({ queryKey: ['initiatives'] });
      
      if (response.data.failed_count === 0) {
        success(`Successfully imported ${response.data.created_count} initiatives`);
      } else {
        error(
          `Imported ${response.data.created_count} initiatives, ${response.data.failed_count} failed`
        );
      }
    },
    onError: (err: any) => {
      error(err.message || 'Failed to import CSV file');
    },
  });

  // Import ZIP
  const importZIPMutation = useMutation({
    mutationFn: (file: File) => initiativesApi.importZIP(file),
    onSuccess: (response) => {
      importResult.value = response.data;
      queryClient.invalidateQueries({ queryKey: ['initiatives'] });
      
      if (response.data.failed_count === 0) {
        success(`Successfully imported ${response.data.created_count} initiatives`);
      } else {
        error(
          `Imported ${response.data.created_count} initiatives, ${response.data.failed_count} failed`
        );
      }
    },
    onError: (err: any) => {
      error(err.message || 'Failed to import ZIP file');
    },
  });

  const clearResult = () => {
    importResult.value = null;
  };

  return {
    importResult,
    importCSV: importCSVMutation.mutateAsync,
    importZIP: importZIPMutation.mutateAsync,
    isImporting: importCSVMutation.isPending || importZIPMutation.isPending,
    clearResult,
  };
}
