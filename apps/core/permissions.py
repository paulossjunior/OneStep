from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to unauthenticated users
    and full access to authenticated users.
    """
    
    def has_permission(self, request, view):
        # Read permissions for any request,
        # Write permissions only for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes that the model has a 'created_by' field.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return hasattr(obj, 'created_by') and obj.created_by == request.user


class IsCoordinatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission for Initiative objects.
    Only coordinators can modify their initiatives.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the coordinator
        return hasattr(obj, 'coordinator') and obj.coordinator.email == request.user.email


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    
    def has_permission(self, request, view):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for admin users
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsAuthenticatedAndActive(permissions.BasePermission):
    """
    Custom permission to only allow authenticated and active users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active
        )


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to authenticated users
    and write access only to staff users.
    """
    
    def has_permission(self, request, view):
        # Must be authenticated
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False
        
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for staff users
        return request.user.is_staff


class IsSuperuserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to authenticated users
    and write access only to superusers.
    """
    
    def has_permission(self, request, view):
        # Must be authenticated
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False
        
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for superusers
        return request.user.is_superuser


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to allow owners and staff to access objects.
    Assumes that the model has a 'created_by' field or similar ownership field.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active
        )
    
    def has_object_permission(self, request, view, obj):
        # Staff users have full access
        if request.user.is_staff:
            return True
        
        # Check ownership based on different possible fields
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        if hasattr(obj, 'coordinator') and hasattr(obj.coordinator, 'email'):
            return obj.coordinator.email == request.user.email
        
        if hasattr(obj, 'email') and obj.email == request.user.email:
            return True
        
        return False


class CanManageInitiatives(permissions.BasePermission):
    """
    Custom permission for Initiative management.
    Allows coordinators to manage their initiatives and staff to manage all.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active
        )
    
    def has_object_permission(self, request, view, obj):
        # Staff users can manage all initiatives
        if request.user.is_staff:
            return True
        
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions for coordinators of the initiative
        if hasattr(obj, 'coordinator') and hasattr(obj.coordinator, 'email'):
            return obj.coordinator.email == request.user.email
        
        return False