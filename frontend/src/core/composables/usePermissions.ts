import { computed } from 'vue';
import { useAuth } from './useAuth';

export function usePermissions() {
  const { userPermissions, isStaff, isSuperuser } = useAuth();

  const can = (permission: string): boolean => {
    if (isSuperuser.value) return true;
    return userPermissions.value.includes(permission);
  };

  const canAny = (permissions: string[]): boolean => {
    if (isSuperuser.value) return true;
    return permissions.some(p => userPermissions.value.includes(p));
  };

  const canAll = (permissions: string[]): boolean => {
    if (isSuperuser.value) return true;
    return permissions.every(p => userPermissions.value.includes(p));
  };

  const canCreate = (resource: string): boolean => {
    return can(`${resource}.add_${resource}`);
  };

  const canView = (resource: string): boolean => {
    return can(`${resource}.view_${resource}`);
  };

  const canEdit = (resource: string): boolean => {
    return can(`${resource}.change_${resource}`);
  };

  const canDelete = (resource: string): boolean => {
    return can(`${resource}.delete_${resource}`);
  };

  const canManage = (resource: string): boolean => {
    return canAll([
      `${resource}.add_${resource}`,
      `${resource}.change_${resource}`,
      `${resource}.delete_${resource}`,
    ]);
  };

  return {
    can,
    canAny,
    canAll,
    canCreate,
    canView,
    canEdit,
    canDelete,
    canManage,
    isStaff,
    isSuperuser,
  };
}
