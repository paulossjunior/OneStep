/**
 * Initiative Service
 * Handles all business logic and API communication for initiatives
 */

import { initiativesApi } from '../api/initiatives.api';
import type {
  Initiative,
  InitiativeFormData,
  InitiativeFilters,
  InitiativeImportResult,
  FailedImport,
  CoordinatorChange,
  InitiativeHierarchy,
} from '../types/initiative.types';
import type { PaginatedResponse } from '@/core/types/api.types';

export class InitiativeService {
  /**
   * Fetch paginated list of initiatives with filters
   */
  async getInitiatives(
    filters?: InitiativeFilters,
    page: number = 1,
    pageSize: number = 10
  ): Promise<PaginatedResponse<Initiative>> {
    try {
      const response = await initiativesApi.list({
        ...filters,
        page,
        page_size: pageSize,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching initiatives:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Fetch single initiative by ID
   */
  async getInitiative(id: number): Promise<Initiative> {
    try {
      const response = await initiativesApi.get(id);
      return response.data;
    } catch (error) {
      console.error(`Error fetching initiative ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Create new initiative
   */
  async createInitiative(data: InitiativeFormData): Promise<Initiative> {
    try {
      // Validate data before sending
      this.validateInitiativeData(data);
      
      const response = await initiativesApi.create(data);
      return response.data;
    } catch (error) {
      console.error('Error creating initiative:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Update existing initiative
   */
  async updateInitiative(
    id: number,
    data: Partial<InitiativeFormData>
  ): Promise<Initiative> {
    try {
      const response = await initiativesApi.update(id, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating initiative ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Delete initiative
   */
  async deleteInitiative(id: number): Promise<void> {
    try {
      await initiativesApi.delete(id);
    } catch (error) {
      console.error(`Error deleting initiative ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Get initiative hierarchy
   */
  async getHierarchy(id?: number): Promise<InitiativeHierarchy[]> {
    try {
      const response = await initiativesApi.getHierarchy(id);
      return response.data;
    } catch (error) {
      console.error('Error fetching hierarchy:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Get children of an initiative
   */
  async getChildren(id: number): Promise<Initiative[]> {
    try {
      const response = await initiativesApi.getChildren(id);
      return response.data;
    } catch (error) {
      console.error(`Error fetching children for initiative ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Add team member to initiative
   */
  async addTeamMember(initiativeId: number, personId: number): Promise<void> {
    try {
      await initiativesApi.addTeamMember(initiativeId, personId);
    } catch (error) {
      console.error('Error adding team member:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Remove team member from initiative
   */
  async removeTeamMember(initiativeId: number, personId: number): Promise<void> {
    try {
      await initiativesApi.removeTeamMember(initiativeId, personId);
    } catch (error) {
      console.error('Error removing team member:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Add student to initiative
   */
  async addStudent(initiativeId: number, personId: number): Promise<void> {
    try {
      await initiativesApi.addStudent(initiativeId, personId);
    } catch (error) {
      console.error('Error adding student:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Remove student from initiative
   */
  async removeStudent(initiativeId: number, personId: number): Promise<void> {
    try {
      await initiativesApi.removeStudent(initiativeId, personId);
    } catch (error) {
      console.error('Error removing student:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Get coordinator change history
   */
  async getCoordinatorChanges(initiativeId: number): Promise<CoordinatorChange[]> {
    try {
      const response = await initiativesApi.getCoordinatorChanges(initiativeId);
      return response.data;
    } catch (error) {
      console.error('Error fetching coordinator changes:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Import initiatives from CSV file
   */
  async importCSV(file: File): Promise<InitiativeImportResult> {
    try {
      // Validate file
      this.validateImportFile(file, 'csv');
      
      const response = await initiativesApi.importCSV(file);
      return response.data;
    } catch (error) {
      console.error('Error importing CSV:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Import initiatives from ZIP file
   */
  async importZIP(file: File): Promise<InitiativeImportResult> {
    try {
      // Validate file
      this.validateImportFile(file, 'zip');
      
      const response = await initiativesApi.importZIP(file);
      return response.data;
    } catch (error) {
      console.error('Error importing ZIP:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Get failed imports
   */
  async getFailedImports(
    page: number = 1,
    pageSize: number = 10
  ): Promise<PaginatedResponse<FailedImport>> {
    try {
      const response = await initiativesApi.getFailedImports({
        page,
        page_size: pageSize,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching failed imports:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Retry failed import
   */
  async retryFailedImport(id: number): Promise<void> {
    try {
      await initiativesApi.retryFailedImport(id);
    } catch (error) {
      console.error(`Error retrying failed import ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Delete failed import
   */
  async deleteFailedImport(id: number): Promise<void> {
    try {
      await initiativesApi.deleteFailedImport(id);
    } catch (error) {
      console.error(`Error deleting failed import ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Get initiative statistics
   */
  async getStatistics(): Promise<{
    total: number;
    by_type: Record<string, number>;
    active: number;
    completed: number;
  }> {
    try {
      const response = await initiativesApi.getStatistics();
      return response.data;
    } catch (error) {
      console.error('Error fetching statistics:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Validate initiative data before submission
   */
  private validateInitiativeData(data: InitiativeFormData): void {
    if (!data.name || data.name.trim().length === 0) {
      throw new Error('Initiative name is required');
    }

    if (!data.description || data.description.trim().length === 0) {
      throw new Error('Initiative description is required');
    }

    if (!data.type) {
      throw new Error('Initiative type is required');
    }

    if (!data.start_date) {
      throw new Error('Start date is required');
    }

    if (!data.coordinator_id) {
      throw new Error('Coordinator is required');
    }

    // Validate dates
    const startDate = new Date(data.start_date);
    if (isNaN(startDate.getTime())) {
      throw new Error('Invalid start date');
    }

    if (data.end_date) {
      const endDate = new Date(data.end_date);
      if (isNaN(endDate.getTime())) {
        throw new Error('Invalid end date');
      }

      if (endDate < startDate) {
        throw new Error('End date must be after start date');
      }
    }
  }

  /**
   * Validate import file
   */
  private validateImportFile(file: File, expectedType: 'csv' | 'zip'): void {
    if (!file) {
      throw new Error('No file provided');
    }

    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      throw new Error('File size exceeds 10MB limit');
    }

    const extension = file.name.split('.').pop()?.toLowerCase();
    
    if (expectedType === 'csv' && extension !== 'csv') {
      throw new Error('File must be a CSV file');
    }

    if (expectedType === 'zip' && extension !== 'zip') {
      throw new Error('File must be a ZIP file');
    }
  }

  /**
   * Handle API errors and transform them into user-friendly messages
   */
  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const data = error.response.data;

      switch (status) {
        case 400:
          return new Error(data.detail || data.message || 'Invalid request');
        case 401:
          return new Error('Unauthorized. Please login again.');
        case 403:
          return new Error('You do not have permission to perform this action');
        case 404:
          return new Error('Initiative not found');
        case 409:
          return new Error('Conflict. This initiative may already exist.');
        case 422:
          return new Error(this.formatValidationErrors(data.errors));
        case 500:
          return new Error('Server error. Please try again later.');
        default:
          return new Error(data.detail || data.message || 'An error occurred');
      }
    } else if (error.request) {
      // Request made but no response
      return new Error('Network error. Please check your connection.');
    } else {
      // Error in request setup
      return new Error(error.message || 'An unexpected error occurred');
    }
  }

  /**
   * Format validation errors from backend
   */
  private formatValidationErrors(errors: Record<string, string[]>): string {
    if (!errors) return 'Validation error';

    const messages = Object.entries(errors)
      .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
      .join('; ');

    return messages || 'Validation error';
  }
}

// Export singleton instance
export const initiativeService = new InitiativeService();
