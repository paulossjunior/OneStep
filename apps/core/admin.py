"""
Core admin configuration for OneStep project.

This module provides enhanced admin interface configuration including
security features, custom branding, and user management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import reverse
from django.conf import settings


class OneStepAdminSite(AdminSite):
    """
    Custom admin site with enhanced security and branding.
    """
    site_header = settings.ADMIN_SITE_HEADER
    site_title = settings.ADMIN_SITE_TITLE
    index_title = settings.ADMIN_INDEX_TITLE
    
    def has_permission(self, request):
        """
        Enhanced permission check for admin access.
        """
        return (
            request.user.is_active and 
            request.user.is_staff and
            (request.user.is_superuser or request.user.groups.exists())
        )
    
    def index(self, request, extra_context=None):
        """
        Enhanced admin index with additional context.
        """
        extra_context = extra_context or {}
        
        # Add system statistics
        from apps.people.models import Person
        from apps.initiatives.models import Initiative
        
        extra_context.update({
            'total_people': Person.objects.count(),
            'total_initiatives': Initiative.objects.count(),
            'active_initiatives': Initiative.objects.filter(
                end_date__isnull=True
            ).count(),
            'user_groups': request.user.groups.all() if request.user.is_authenticated else [],
        })
        
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = OneStepAdminSite(name='onestep_admin')


class EnhancedUserAdmin(BaseUserAdmin):
    """
    Enhanced User admin with additional security features.
    """
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'is_staff', 'is_active', 'get_groups', 'last_login'
    )
    list_filter = BaseUserAdmin.list_filter + ('groups',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    # Override fieldsets to avoid duplicates
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_groups(self, obj):
        """Display user groups in list view."""
        groups = obj.groups.all()
        if groups:
            return ', '.join([group.name for group in groups])
        return 'No groups'
    get_groups.short_description = 'Groups'
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related."""
        return super().get_queryset(request).prefetch_related('groups')


class EnhancedGroupAdmin(admin.ModelAdmin):
    """
    Enhanced Group admin with permission management.
    """
    list_display = ('name', 'get_user_count', 'get_permissions_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    
    def get_user_count(self, obj):
        """Display number of users in group."""
        return obj.user_set.count()
    get_user_count.short_description = 'Users'
    
    def get_permissions_count(self, obj):
        """Display number of permissions in group."""
        return obj.permissions.count()
    get_permissions_count.short_description = 'Permissions'
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related."""
        return super().get_queryset(request).prefetch_related('permissions', 'user_set')


# Register models with custom admin site
admin_site.register(User, EnhancedUserAdmin)
admin_site.register(Group, EnhancedGroupAdmin)

# Also register with default admin site for compatibility
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, EnhancedUserAdmin)
admin.site.register(Group, EnhancedGroupAdmin)