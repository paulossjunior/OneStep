// Core API Types

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
  detail?: string;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface QueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  [key: string]: any;
}

export interface BulkImportResponse {
  success: boolean;
  created_count: number;
  updated_count: number;
  failed_count: number;
  errors: Array<{
    row: number;
    errors: Record<string, string[]>;
  }>;
}
