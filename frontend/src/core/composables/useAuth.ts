import { useAuthStore } from '@/core/stores/auth.store';
import { storeToRefs } from 'pinia';
import type { LoginCredentials } from '@/core/types/auth.types';

export function useAuth() {
  const authStore = useAuthStore();
  
  const {
    user,
    isAuthenticated,
    isLoading,
    currentUser,
    userPermissions,
    isStaff,
    isSuperuser,
  } = storeToRefs(authStore);

  const login = async (credentials: LoginCredentials) => {
    return authStore.login(credentials);
  };

  const logout = async () => {
    return authStore.logout();
  };

  const hasPermission = (permission: string) => {
    return authStore.hasPermission(permission);
  };

  const hasAnyPermission = (permissions: string[]) => {
    return authStore.hasAnyPermission(permissions);
  };

  const hasAllPermissions = (permissions: string[]) => {
    return authStore.hasAllPermissions(permissions);
  };

  return {
    // State
    user,
    isAuthenticated,
    isLoading,
    currentUser,
    userPermissions,
    isStaff,
    isSuperuser,
    // Actions
    login,
    logout,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };
}
