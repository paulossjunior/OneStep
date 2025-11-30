/**
 * Initiative Handlers
 * Reusable handlers for common initiative operations
 */

import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { initiativeService } from '../services/initiative.service';
import { useNotifications } from '@/core/composables/useNotifications';
import type { Initiative, InitiativeFormData } from '../types/initiative.types';

/**
 * Handler for creating an initiative
 */
export function useCreateInitiativeHandler() {
  const router = useRouter();
  const { success, error } = useNotifications();
  const isSubmitting = ref(false);

  const handleCreate = async (data: InitiativeFormData) => {
    isSubmitting.value = true;

    try {
      const initiative = await initiativeService.createInitiative(data);
      success('Initiative created successfully');
      router.push(`/initiatives/${initiative.id}`);
      return initiative;
    } catch (err: any) {
      error(err.message || 'Failed to create initiative');
      throw err;
    } finally {
      isSubmitting.value = false;
    }
  };

  return {
    handleCreate,
    isSubmitting,
  };
}

/**
 * Handler for updating an initiative
 */
export function useUpdateInitiativeHandler(initiativeId: number) {
  const router = useRouter();
  const { success, error } = useNotifications();
  const isSubmitting = ref(false);

  const handleUpdate = async (data: Partial<InitiativeFormData>) => {
    isSubmitting.value = true;

    try {
      const initiative = await initiativeService.updateInitiative(initiativeId, data);
      success('Initiative updated successfully');
      router.push(`/initiatives/${initiative.id}`);
      return initiative;
    } catch (err: any) {
      error(err.message || 'Failed to update initiative');
      throw err;
    } finally {
      isSubmitting.value = false;
    }
  };

  return {
    handleUpdate,
    isSubmitting,
  };
}

/**
 * Handler for deleting an initiative
 */
export function useDeleteInitiativeHandler() {
  const router = useRouter();
  const { success, error } = useNotifications();
  const isDeleting = ref(false);

  const handleDelete = async (initiative: Initiative, redirectTo: string = '/initiatives') => {
    isDeleting.value = true;

    try {
      await initiativeService.deleteInitiative(initiative.id);
      success(`Initiative "${initiative.name}" deleted successfully`);
      router.push(redirectTo);
    } catch (err: any) {
      error(err.message || 'Failed to delete initiative');
      throw err;
    } finally {
      isDeleting.value = false;
    }
  };

  return {
    handleDelete,
    isDeleting,
  };
}

/**
 * Handler for team member operations
 */
export function useTeamMemberHandler(initiativeId: number) {
  const { success, error } = useNotifications();
  const isProcessing = ref(false);

  const handleAddMember = async (personId: number, personName: string) => {
    isProcessing.value = true;

    try {
      await initiativeService.addTeamMember(initiativeId, personId);
      success(`${personName} added to team`);
    } catch (err: any) {
      error(err.message || 'Failed to add team member');
      throw err;
    } finally {
      isProcessing.value = false;
    }
  };

  const handleRemoveMember = async (personId: number, personName: string) => {
    isProcessing.value = true;

    try {
      await initiativeService.removeTeamMember(initiativeId, personId);
      success(`${personName} removed from team`);
    } catch (err: any) {
      error(err.message || 'Failed to remove team member');
      throw err;
    } finally {
      isProcessing.value = false;
    }
  };

  return {
    handleAddMember,
    handleRemoveMember,
    isProcessing,
  };
}

/**
 * Handler for student operations
 */
export function useStudentHandler(initiativeId: number) {
  const { success, error } = useNotifications();
  const isProcessing = ref(false);

  const handleAddStudent = async (personId: number, personName: string) => {
    isProcessing.value = true;

    try {
      await initiativeService.addStudent(initiativeId, personId);
      success(`${personName} added as student`);
    } catch (err: any) {
      error(err.message || 'Failed to add student');
      throw err;
    } finally {
      isProcessing.value = false;
    }
  };

  const handleRemoveStudent = async (personId: number, personName: string) => {
    isProcessing.value = true;

    try {
      await initiativeService.removeStudent(initiativeId, personId);
      success(`${personName} removed from students`);
    } catch (err: any) {
      error(err.message || 'Failed to remove student');
      throw err;
    } finally {
      isProcessing.value = false;
    }
  };

  return {
    handleAddStudent,
    handleRemoveStudent,
    isProcessing,
  };
}

/**
 * Handler for file import operations
 */
export function useImportHandler() {
  const { success, error, warning } = useNotifications();
  const isImporting = ref(false);
  const importResult = ref<any>(null);

  const handleCSVImport = async (file: File) => {
    isImporting.value = true;
    importResult.value = null;

    try {
      const result = await initiativeService.importCSV(file);
      importResult.value = result;

      if (result.failed_count === 0) {
        success(`Successfully imported ${result.created_count} initiatives`);
      } else {
        warning(
          `Imported ${result.created_count} initiatives. ${result.failed_count} failed. Check failed imports for details.`
        );
      }

      return result;
    } catch (err: any) {
      error(err.message || 'Failed to import CSV file');
      throw err;
    } finally {
      isImporting.value = false;
    }
  };

  const handleZIPImport = async (file: File) => {
    isImporting.value = true;
    importResult.value = null;

    try {
      const result = await initiativeService.importZIP(file);
      importResult.value = result;

      if (result.failed_count === 0) {
        success(`Successfully imported ${result.created_count} initiatives`);
      } else {
        warning(
          `Imported ${result.created_count} initiatives. ${result.failed_count} failed. Check failed imports for details.`
        );
      }

      return result;
    } catch (err: any) {
      error(err.message || 'Failed to import ZIP file');
      throw err;
    } finally {
      isImporting.value = false;
    }
  };

  const clearResult = () => {
    importResult.value = null;
  };

  return {
    handleCSVImport,
    handleZIPImport,
    isImporting,
    importResult,
    clearResult,
  };
}

/**
 * Handler for failed import operations
 */
export function useFailedImportHandler() {
  const { success, error } = useNotifications();
  const isProcessing = ref(false);

  const handleRetry = async (importId: number) => {
    isProcessing.value = true;

    try {
      await initiativeService.retryFailedImport(importId);
      success('Import retried successfully');
    } catch (err: any) {
      error(err.message || 'Failed to retry import');
      throw err;
    } finally {
      isProcessing.value = false;
    }
  };

  const handleDelete = async (importId: number) => {
    isProcessing.value = true;

    try {
      await initiativeService.deleteFailedImport(importId);
      success('Failed import deleted');
    } catch (err: any) {
      error(err.message || 'Failed to delete import');
      throw err;
    } finally {
      isProcessing.value = false;
    }
  };

  return {
    handleRetry,
    handleDelete,
    isProcessing,
  };
}

/**
 * Handler for bulk operations
 */
export function useBulkOperationsHandler() {
  const { success, error } = useNotifications();
  const isProcessing = ref(false);
  const progress = ref(0);

  const handleBulkDelete = async (initiatives: Initiative[]) => {
    isProcessing.value = true;
    progress.value = 0;

    const total = initiatives.length;
    let deleted = 0;
    const errors: string[] = [];

    try {
      for (const initiative of initiatives) {
        try {
          await initiativeService.deleteInitiative(initiative.id);
          deleted++;
          progress.value = Math.round((deleted / total) * 100);
        } catch (err: any) {
          errors.push(`${initiative.name}: ${err.message}`);
        }
      }

      if (errors.length === 0) {
        success(`Successfully deleted ${deleted} initiatives`);
      } else {
        error(`Deleted ${deleted} of ${total} initiatives. ${errors.length} failed.`);
      }

      return { deleted, failed: errors.length, errors };
    } finally {
      isProcessing.value = false;
      progress.value = 0;
    }
  };

  return {
    handleBulkDelete,
    isProcessing,
    progress,
  };
}

/**
 * Handler for search and filter operations
 */
export function useSearchHandler() {
  const searchQuery = ref('');
  const debouncedSearch = ref('');
  let debounceTimeout: NodeJS.Timeout;

  const handleSearch = (query: string) => {
    searchQuery.value = query;

    // Debounce search
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
      debouncedSearch.value = query;
    }, 300);
  };

  const clearSearch = () => {
    searchQuery.value = '';
    debouncedSearch.value = '';
  };

  return {
    searchQuery,
    debouncedSearch,
    handleSearch,
    clearSearch,
  };
}

/**
 * Handler for export operations
 */
export function useExportHandler() {
  const { success, error } = useNotifications();
  const isExporting = ref(false);

  const handleExportCSV = async (initiatives: Initiative[]) => {
    isExporting.value = true;

    try {
      // Convert initiatives to CSV
      const headers = ['ID', 'Name', 'Type', 'Coordinator', 'Start Date', 'End Date'];
      const rows = initiatives.map((i) => [
        i.id,
        i.name,
        i.type,
        `${i.coordinator.first_name} ${i.coordinator.last_name}`,
        i.start_date,
        i.end_date || '',
      ]);

      const csv = [
        headers.join(','),
        ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
      ].join('\n');

      // Download file
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `initiatives_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      URL.revokeObjectURL(url);

      success('Initiatives exported successfully');
    } catch (err: any) {
      error(err.message || 'Failed to export initiatives');
      throw err;
    } finally {
      isExporting.value = false;
    }
  };

  return {
    handleExportCSV,
    isExporting,
  };
}
