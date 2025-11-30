import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { computed, type Ref } from 'vue';
import { initiativesApi } from '../api/initiatives.api';
import type { InitiativeFormData, InitiativeFilters } from '../types/initiative.types';
import { useNotifications } from '@/core/composables/useNotifications';

export function useInitiatives(filters?: Ref<InitiativeFilters>) {
  const queryClient = useQueryClient();
  const { success, error } = useNotifications();

  // List initiatives
  const {
    data: initiatives,
    isLoading,
    isError,
    error: queryError,
    refetch,
  } = useQuery({
    queryKey: ['initiatives', filters],
    queryFn: () => initiativesApi.list(filters?.value),
  });

  const items = computed(() => initiatives.value?.data.results || []);
  const total = computed(() => initiatives.value?.data.count || 0);
  const hasNext = computed(() => !!initiatives.value?.data.next);
  const hasPrevious = computed(() => !!initiatives.value?.data.previous);

  // Create initiative
  const createMutation = useMutation({
    mutationFn: (data: InitiativeFormData) => initiativesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiatives'] });
      success('Initiative created successfully');
    },
    onError: (err: any) => {
      error(err.message || 'Failed to create initiative');
    },
  });

  // Update initiative
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<InitiativeFormData> }) =>
      initiativesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiatives'] });
      success('Initiative updated successfully');
    },
    onError: (err: any) => {
      error(err.message || 'Failed to update initiative');
    },
  });

  // Delete initiative
  const deleteMutation = useMutation({
    mutationFn: (id: number) => initiativesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiatives'] });
      success('Initiative deleted successfully');
    },
    onError: (err: any) => {
      error(err.message || 'Failed to delete initiative');
    },
  });

  return {
    // Data
    items,
    total,
    hasNext,
    hasPrevious,
    isLoading,
    isError,
    queryError,
    // Actions
    refetch,
    create: createMutation.mutateAsync,
    update: updateMutation.mutateAsync,
    delete: deleteMutation.mutateAsync,
    // Mutation states
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

export function useInitiative(id: Ref<number | null>) {
  const queryClient = useQueryClient();
  const { success, error } = useNotifications();

  const {
    data: initiative,
    isLoading,
    isError,
    error: queryError,
    refetch,
  } = useQuery({
    queryKey: ['initiative', id],
    queryFn: () => initiativesApi.get(id.value!),
    enabled: computed(() => !!id.value),
  });

  // Add team member
  const addTeamMemberMutation = useMutation({
    mutationFn: (personId: number) => initiativesApi.addTeamMember(id.value!, personId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiative', id] });
      success('Team member added successfully');
    },
    onError: (err: any) => {
      error(err.message || 'Failed to add team member');
    },
  });

  // Remove team member
  const removeTeamMemberMutation = useMutation({
    mutationFn: (personId: number) => initiativesApi.removeTeamMember(id.value!, personId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiative', id] });
      success('Team member removed successfully');
    },
    onError: (err: any) => {
      error(err.message || 'Failed to remove team member');
    },
  });

  // Add student
  const addStudentMutation = useMutation({
    mutationFn: (personId: number) => initiativesApi.addStudent(id.value!, personId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiative', id] });
      success('Student added successfully');
    },
    onError: (err: any) => {
      error(err.message || 'Failed to add student');
    },
  });

  // Remove student
  const removeStudentMutation = useMutation({
    mutationFn: (personId: number) => initiativesApi.removeStudent(id.value!, personId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiative', id] });
      success('Student removed successfully');
    },
    onError: (err: any) => {
      error(err.message || 'Failed to remove student');
    },
  });

  return {
    // Data
    initiative: computed(() => initiative.value?.data),
    isLoading,
    isError,
    queryError,
    // Actions
    refetch,
    addTeamMember: addTeamMemberMutation.mutateAsync,
    removeTeamMember: removeTeamMemberMutation.mutateAsync,
    addStudent: addStudentMutation.mutateAsync,
    removeStudent: removeStudentMutation.mutateAsync,
  };
}
