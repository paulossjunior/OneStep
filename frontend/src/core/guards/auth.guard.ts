import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router';
import { useAuthStore } from '@/core/stores/auth.store';

export function authGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const authStore = useAuthStore();

  if (!authStore.isAuthenticated) {
    // Redirect to login with return URL
    next({
      name: 'login',
      query: { redirect: to.fullPath },
    });
  } else {
    next();
  }
}

export function guestGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const authStore = useAuthStore();

  if (authStore.isAuthenticated) {
    // Already logged in, redirect to dashboard
    next({ name: 'dashboard' });
  } else {
    next();
  }
}

export function permissionGuard(permissions: string | string[]) {
  return (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: NavigationGuardNext
  ): void => {
    const authStore = useAuthStore();
    const requiredPermissions = Array.isArray(permissions) ? permissions : [permissions];

    if (!authStore.isAuthenticated) {
      next({
        name: 'login',
        query: { redirect: to.fullPath },
      });
      return;
    }

    if (authStore.hasAnyPermission(requiredPermissions)) {
      next();
    } else {
      // No permission - redirect to forbidden page
      next({ name: 'forbidden' });
    }
  };
}

export function staffGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const authStore = useAuthStore();

  if (!authStore.isAuthenticated) {
    next({
      name: 'login',
      query: { redirect: to.fullPath },
    });
    return;
  }

  if (authStore.isStaff || authStore.isSuperuser) {
    next();
  } else {
    next({ name: 'forbidden' });
  }
}
