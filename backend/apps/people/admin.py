from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Person, PersonEmail
from apps.core.admin import admin_site


class PersonEmailInline(admin.TabularInline):
    """
    Inline admin for person emails.
    
    Allows managing multiple email addresses for a person.
    """
    model = PersonEmail
    extra = 1
    verbose_name = "Email Address"
    verbose_name_plural = "Email Addresses"
    can_delete = True
    
    fields = ['email', 'is_primary']
    
    def get_queryset(self, request):
        """
        Optimize queryset for inline display.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset
        """
        return super().get_queryset(request).select_related('person')


class InitiativeInline(admin.TabularInline):
    """
    Inline admin for team initiatives (many-to-many relationship).
    
    Allows viewing and managing initiative team memberships from Person admin.
    """
    from apps.initiatives.models import Initiative
    model = Initiative.team_members.through
    extra = 0
    verbose_name = "Team Initiative"
    verbose_name_plural = "Team Initiatives"
    can_delete = True
    
    fields = ['initiative']
    readonly_fields = []
    
    def get_queryset(self, request):
        """
        Optimize queryset for inline display.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset
        """
        return super().get_queryset(request).select_related('initiative')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for Person model.
    
    Provides comprehensive administrative interface for managing Person entities
    with optimized list views, search functionality, and detailed form layouts.
    """
    
    # List view configuration
    list_display = [
        'full_name_display',
        'email',
        'coordinated_count_display',
        'team_count_display',
        'created_at_display'
    ]
    
    list_display_links = ['full_name_display', 'email']
    
    list_filter = [
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'name',
        'email'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'coordinated_count_display',
        'team_count_display',
        'full_name'
    ]
    
    # Form layout configuration
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email'),
            'description': 'Basic personal information for the person.'
        }),
        ('Statistics', {
            'fields': ('coordinated_count_display', 'team_count_display'),
            'classes': ('collapse',),
            'description': 'Statistics about initiatives this person is involved in.'
        }),
        ('System Information', {
            'fields': ('id', 'full_name', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System-generated information and metadata.'
        })
    )
    
    # Inline configuration
    inlines = [PersonEmailInline, InitiativeInline]
    
    # Pagination and performance
    list_per_page = 25
    list_max_show_all = 100
    
    # Ordering
    ordering = ['name']
    
    # Actions
    actions = ['export_selected_people']
    
    def get_queryset(self, request):
        """
        Optimize queryset with prefetch_related for better performance.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset with related data
        """
        queryset = super().get_queryset(request)
        
        # Add annotations for counts to improve performance
        queryset = queryset.annotate(
            coordinated_count=models.Count('coordinated_initiatives', distinct=True),
            team_count=models.Count('team_initiatives', distinct=True)
        )
        
        # Prefetch related data when available
        try:
            queryset = queryset.prefetch_related(
                'coordinated_initiatives',
                'team_initiatives'
            )
        except:
            # Handle case where Initiative model is not yet available
            pass
        
        return queryset
    
    # Custom display methods
    def full_name_display(self, obj):
        """
        Display full name with proper formatting.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            str: Formatted full name
        """
        return obj.full_name
    full_name_display.short_description = 'Full Name'
    full_name_display.admin_order_field = 'name'
    

    
    def coordinated_count_display(self, obj):
        """
        Display count of coordinated initiatives with link.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            str: HTML formatted count with optional link
        """
        try:
            count = getattr(obj, 'coordinated_count', 0)
            if count == 0:
                count = obj.get_coordinated_initiatives_count()
            
            if count > 0:
                # When Initiative admin is available, this can link to filtered list
                return format_html(
                    '<strong>{}</strong> initiative{}',
                    count,
                    's' if count != 1 else ''
                )
            else:
                return format_html('<span style="color: #999;">None</span>')
        except:
            return format_html('<span style="color: #999;">-</span>')
    
    coordinated_count_display.short_description = 'Coordinated'
    coordinated_count_display.admin_order_field = 'coordinated_count'
    
    def team_count_display(self, obj):
        """
        Display count of team memberships with link.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            str: HTML formatted count with optional link
        """
        try:
            count = getattr(obj, 'team_count', 0)
            if count == 0:
                count = obj.get_team_initiatives_count()
            
            if count > 0:
                # When Initiative admin is available, this can link to filtered list
                return format_html(
                    '<strong>{}</strong> membership{}',
                    count,
                    's' if count != 1 else ''
                )
            else:
                return format_html('<span style="color: #999;">None</span>')
        except:
            return format_html('<span style="color: #999;">-</span>')
    
    team_count_display.short_description = 'Team Member'
    team_count_display.admin_order_field = 'team_count'
    
    def created_at_display(self, obj):
        """
        Display creation date with proper formatting.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            str: Formatted creation date
        """
        return obj.created_at.strftime('%Y-%m-%d %H:%M') if obj.created_at else '-'
    created_at_display.short_description = 'Created'
    created_at_display.admin_order_field = 'created_at'
    
    # Custom actions
    def export_selected_people(self, request, queryset):
        """
        Export selected people to CSV format.
        
        Args:
            request: HTTP request object
            queryset: Selected Person objects
            
        Returns:
            HttpResponse: CSV file response
        """
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="people_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Email',
            'Coordinated Initiatives', 'Team Memberships', 'Created At'
        ])
        
        for person in queryset:
            writer.writerow([
                person.id,
                person.name,
                person.email,
                person.get_coordinated_initiatives_count(),
                person.get_team_initiatives_count(),
                person.created_at.strftime('%Y-%m-%d %H:%M:%S') if person.created_at else ''
            ])
        
        return response
    
    export_selected_people.short_description = "Export selected people to CSV"
    
    # Form validation
    def save_model(self, request, obj, form, change):
        """
        Custom save method with additional validation.
        
        Args:
            request: HTTP request object
            obj: Person instance being saved
            form: Admin form instance
            change: Boolean indicating if this is an update
        """
        # Run model validation
        obj.full_clean()
        super().save_model(request, obj, form, change)
    
    # Custom form widgets and help text
    formfield_overrides = {
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget},
        models.EmailField: {'widget': admin.widgets.AdminEmailInputWidget},
    }
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Customize form based on user permissions and object state.
        
        Args:
            request: HTTP request object
            obj: Person instance (None for add form)
            
        Returns:
            Form class: Customized admin form
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text to fields
        if 'email' in form.base_fields:
            form.base_fields['email'].help_text = 'Email address must be unique across all people.'
        
        return form
    
    def has_delete_permission(self, request, obj=None):
        """
        Check if user can delete person based on relationships and permissions.
        
        Args:
            request: HTTP request object
            obj: Person instance
            
        Returns:
            bool: Whether deletion is allowed
        """
        # Check base permissions first
        if not super().has_delete_permission(request, obj):
            return False
        
        # Only HR Managers and superusers can delete people
        if not (request.user.is_superuser or 
                request.user.groups.filter(name='HR Managers').exists()):
            return False
        
        if obj and hasattr(obj, 'coordinated_initiatives'):
            # Don't allow deletion if person coordinates initiatives
            if obj.coordinated_initiatives.exists():
                return False
        
        return True
    
    def has_change_permission(self, request, obj=None):
        """
        Check if user can modify person based on permissions.
        
        Args:
            request: HTTP request object
            obj: Person instance
            
        Returns:
            bool: Whether modification is allowed
        """
        # Check base permissions first
        if not super().has_change_permission(request, obj):
            return False
        
        # HR Managers and superusers can modify all people
        if (request.user.is_superuser or 
            request.user.groups.filter(name='HR Managers').exists()):
            return True
        
        # Users can modify their own person record if it exists
        if obj and hasattr(obj, 'email') and obj.email == request.user.email:
            return True
        
        return False
    
    def has_add_permission(self, request):
        """
        Check if user can add new people.
        
        Args:
            request: HTTP request object
            
        Returns:
            bool: Whether addition is allowed
        """
        # Check base permissions first
        if not super().has_add_permission(request):
            return False
        
        # Only HR Managers and superusers can add people
        return (request.user.is_superuser or 
                request.user.groups.filter(name='HR Managers').exists())
    
    def delete_model(self, request, obj):
        """
        Custom delete method with relationship checks.
        
        Args:
            request: HTTP request object
            obj: Person instance to delete
        """
        # Check for coordinated initiatives
        if hasattr(obj, 'coordinated_initiatives') and obj.coordinated_initiatives.exists():
            from django.contrib import messages
            messages.error(
                request,
                f'Cannot delete {obj.full_name} because they coordinate one or more initiatives.'
            )
            return
        
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """
        Custom bulk delete method with relationship checks.
        
        Args:
            request: HTTP request object
            queryset: QuerySet of Person objects to delete
        """
        # Check each person for coordinated initiatives
        blocked_people = []
        for person in queryset:
            if hasattr(person, 'coordinated_initiatives') and person.coordinated_initiatives.exists():
                blocked_people.append(person.full_name)
        
        if blocked_people:
            from django.contrib import messages
            messages.error(
                request,
                f'Cannot delete the following people because they coordinate initiatives: {", ".join(blocked_people)}'
            )
            return
        
        super().delete_queryset(request, queryset)


# Register with custom admin site
admin_site.register(Person, PersonAdmin)