// Initiative Types

export enum InitiativeType {
  PROGRAM = 'PROGRAM',
  PROJECT = 'PROJECT',
  EVENT = 'EVENT',
}

export interface Person {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  full_name?: string;
}

export interface OrganizationalGroup {
  id: number;
  name: string;
  short_name?: string;
  type: string;
}

export interface Initiative {
  id: number;
  name: string;
  description: string;
  type: InitiativeType;
  start_date: string;
  end_date: string | null;
  coordinator: Person;
  parent: Initiative | null;
  parent_id: number | null;
  team_members: Person[];
  students: Person[];
  organizational_groups: OrganizationalGroup[];
  created_at: string;
  updated_at: string;
}

export interface InitiativeFormData {
  name: string;
  description: string;
  type: InitiativeType;
  start_date: string;
  end_date: string | null;
  coordinator_id: number;
  parent_id: number | null;
  team_member_ids?: number[];
  student_ids?: number[];
  organizational_group_ids?: number[];
}

export interface InitiativeHierarchy {
  id: number;
  name: string;
  type: InitiativeType;
  coordinator: Person;
  children: InitiativeHierarchy[];
}

export interface CoordinatorChange {
  id: number;
  initiative: Initiative;
  previous_coordinator: Person;
  new_coordinator: Person;
  changed_at: string;
  changed_by: Person;
  reason?: string;
}

export interface InitiativeImportResult {
  success: boolean;
  created_count: number;
  updated_count: number;
  failed_count: number;
  errors: Array<{
    row: number;
    data: Record<string, any>;
    errors: Record<string, string[]>;
  }>;
}

export interface FailedImport {
  id: number;
  file_name: string;
  row_number: number;
  data: Record<string, any>;
  errors: Record<string, string[]>;
  created_at: string;
}

export interface InitiativeFilters {
  search?: string;
  type?: InitiativeType | '';
  coordinator_id?: number | null;
  parent_id?: number | null;
  organizational_group_id?: number | null;
  start_date_after?: string;
  start_date_before?: string;
  end_date_after?: string;
  end_date_before?: string;
  ordering?: string;
}
