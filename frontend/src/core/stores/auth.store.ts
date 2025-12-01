import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/core/api/client';
import type { User, LoginCredentials } from '@/core/types/auth.types';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(localStorage.getItem('access_token'));
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'));
  const isLoading = ref(false);

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value);
  const currentUser = computed(() => user.value);
  const userPermissions = computed(() => user.value?.permissions || []);
  const isStaff = computed(() => user.value?.is_staff || false);
  const isSuperuser = computed(() => user.value?.is_superuser || false);

  // Actions
  async function login(credentials: LoginCredentials): Promise<void> {
    isLoading.value = true;

    try {
      const formData = new FormData();
      formData.append('grant_type', 'password');
      formData.append('client_id', (import.meta as any).env.VITE_OAUTH_CLIENT_ID);
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await apiClient.post('/o/token/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { access_token, refresh_token } = response.data;

      // Store tokens
      accessToken.value = access_token;
      refreshToken.value = refresh_token;

      // Persist to localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Fetch user data
      await fetchCurrentUser();
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout(): Promise<void> {
    try {
      // Optional: Call logout endpoint
      if (refreshToken.value) {
        await apiClient.post('/auth/logout/', {
          refresh: refreshToken.value,
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear state
      user.value = null;
      accessToken.value = null;
      refreshToken.value = null;

      // Clear localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  async function refreshAccessToken(): Promise<void> {
    if (!refreshToken.value) {
      throw new Error('No refresh token available');
    }

    try {
      const formData = new FormData();
      formData.append('grant_type', 'refresh_token');
      formData.append('client_id', (import.meta as any).env.VITE_OAUTH_CLIENT_ID);
      formData.append('refresh_token', refreshToken.value);

      const response = await apiClient.post('/o/token/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { access_token, refresh_token: new_refresh_token } = response.data;
      accessToken.value = access_token;
      localStorage.setItem('access_token', access_token);

      if (new_refresh_token) {
        refreshToken.value = new_refresh_token;
        localStorage.setItem('refresh_token', new_refresh_token);
      }
    } catch (error) {
      // Refresh failed - logout user
      await logout();
      throw error;
    }
  }

  async function fetchCurrentUser(): Promise<void> {
    if (!accessToken.value) {
      return;
    }

    try {
      const response = await apiClient.get<User>('/auth/me/');
      user.value = response.data;
      localStorage.setItem('user', JSON.stringify(response.data));
    } catch (error) {
      console.error('Failed to fetch user:', error);
      await logout();
    }
  }

  function initializeAuth(): void {
    const storedUser = localStorage.getItem('user');

    if (storedUser && accessToken.value) {
      try {
        user.value = JSON.parse(storedUser);
        // Optionally fetch fresh user data
        fetchCurrentUser();
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        logout();
      }
    }
  }

  function hasPermission(permission: string): boolean {
    return userPermissions.value.includes(permission) || isSuperuser.value;
  }

  function hasAnyPermission(permissions: string[]): boolean {
    return permissions.some(p => hasPermission(p));
  }

  function hasAllPermissions(permissions: string[]): boolean {
    return permissions.every(p => hasPermission(p));
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    // Getters
    isAuthenticated,
    currentUser,
    userPermissions,
    isStaff,
    isSuperuser,
    // Actions
    login,
    logout,
    refreshAccessToken,
    fetchCurrentUser,
    initializeAuth,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };
});
