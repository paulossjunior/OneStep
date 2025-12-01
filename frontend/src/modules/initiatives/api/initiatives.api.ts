import apiClient from '@/core/api/client';
import type { PaginatedResponse } from '@/core/types/api.types';
import type {
  Initiative,
  InitiativeFormData,
  InitiativeHierarchy,
  InitiativeImportResult,
  FailedImport,
  InitiativeFilters,
  CoordinatorChange,
} from '../types/initiative.types';

const BASE_URL = '/initiatives';

export const initiativesApi = {
  // List initiatives with filters and pagination
  list(params?: InitiativeFilters & { page?: number; page_size?: number }) {
    return apiClient.get<PaginatedResponse<Initiative>>(`${BASE_URL}/`, { params });
  },

  // Get single initiative
  get(id: number) {
    return apiClient.get<Initiative>(`${BASE_URL}/${id}/`);
  },

  // Create initiative
  create(data: InitiativeFormData) {
    return apiClient.post<Initiative>(`${BASE_URL}/`, data);
  },

  // Update initiative
  update(id: number, data: Partial<InitiativeFormData>) {
    return apiClient.patch<Initiative>(`${BASE_URL}/${id}/`, data);
  },

  // Delete initiative
  delete(id: number) {
    return apiClient.delete(`${BASE_URL}/${id}/`);
  },

  // Get initiative hierarchy
  getHierarchy(id?: number) {
    const url = id ? `${BASE_URL}/${id}/hierarchy/` : `${BASE_URL}/hierarchy/`;
    return apiClient.get<InitiativeHierarchy[]>(url);
  },

  // Get children of an initiative
  getChildren(id: number) {
    return apiClient.get<Initiative[]>(`${BASE_URL}/${id}/children/`);
  },

  // Team member management
  addTeamMember(initiativeId: number, personId: number) {
    return apiClient.post(`${BASE_URL}/${initiativeId}/team-members/`, {
      person_id: personId,
    });
  },

  removeTeamMember(initiativeId: number, personId: number) {
    return apiClient.delete(`${BASE_URL}/${initiativeId}/team-members/${personId}/`);
  },

  // Student management
  addStudent(initiativeId: number, personId: number) {
    return apiClient.post(`${BASE_URL}/${initiativeId}/students/`, {
      person_id: personId,
    });
  },

  removeStudent(initiativeId: number, personId: number) {
    return apiClient.delete(`${BASE_URL}/${initiativeId}/students/${personId}/`);
  },

  // Coordinator change history
  getCoordinatorChanges(initiativeId: number) {
    return apiClient.get<CoordinatorChange[]>(
      `${BASE_URL}/${initiativeId}/coordinator-changes/`
    );
  },

  // Bulk import
  importCSV(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<InitiativeImportResult>(`${BASE_URL}/import/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  importZIP(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<InitiativeImportResult>(`${BASE_URL}/import-zip/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Failed imports
  getFailedImports(params?: { page?: number; page_size?: number }) {
    return apiClient.get<PaginatedResponse<FailedImport>>(`${BASE_URL}/failed-imports/`, {
      params,
    });
  },

  retryFailedImport(id: number) {
    return apiClient.post(`${BASE_URL}/failed-imports/${id}/retry/`);
  },

  deleteFailedImport(id: number) {
    return apiClient.delete(`${BASE_URL}/failed-imports/${id}/`);
  },

  // Statistics
  getStatistics() {
    return apiClient.get<{
      total: number;
      by_type: Record<string, number>;
      active: number;
      completed: number;
    }>(`${BASE_URL}/statistics/`);
  },

  // Get initiative types
  getTypes() {
    return apiClient.get<{ types: Array<{ id: number; code: string; name: string; description: string; is_active: boolean }> }>(`${BASE_URL}/types/`);
  },
};
