from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Initiative, InitiativeType
from apps.core.admin import admin_site


@admin.register(InitiativeType)
class InitiativeTypeAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for InitiativeType model.
    
    Provides administrative interface for managing initiative types.
    """
    
    list_display = ['name', 'code', 'is_active', 'initiative_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'initiative_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Statistics', {
            'fields': ('initiative_count',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """
        Optimize queryset with annotations.
        """
        return super().get_queryset(request).annotate(
            initiative_count=models.Count('initiative', distinct=True)
        )
    
    def initiative_count(self, obj):
        """
        Display count of initiatives using this type.
        """
        count = getattr(obj, 'initiative_count', 0)
        if count > 0:
            return format_html('<strong>{}</strong>', count)
        return format_html('<span style="color: #999;">0</span>')
    initiative_count.short_description = 'Initiatives'
    initiative_count.admin_order_field = 'initiative_count'


class TeamMemberInline(admin.TabularInline):
    """
    Inline admin for team member relationships (many-to-many).
    
    Allows editing team member assignments directly from the Initiative admin page.
    """
    model = Initiative.team_members.through
    extra = 1
    verbose_name = "Team Member"
    verbose_name_plural = "Team Members"
    can_delete = True
    
    # Customize the display
    autocomplete_fields = ['person']
    
    def get_queryset(self, request):
        """
        Optimize queryset for inline display.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset
        """
        return super().get_queryset(request).select_related('person')


class ChildInitiativeInline(admin.TabularInline):
    """
    Inline admin for child initiatives (hierarchical relationship).
    
    Allows viewing and editing child initiatives directly from parent Initiative admin page.
    """
    model = Initiative
    fk_name = 'parent'
    extra = 0
    verbose_name = "Child Initiative"
    verbose_name_plural = "Child Initiatives"
    can_delete = False  # Prevent accidental deletion
    
    fields = ['name', 'type', 'start_date', 'end_date', 'coordinator']
    readonly_fields = ['name', 'type', 'start_date', 'end_date', 'coordinator']
    
    def has_add_permission(self, request, obj=None):
        """
        Disable adding child initiatives through inline.
        
        Args:
            request: HTTP request object
            obj: Parent initiative instance
            
        Returns:
            bool: Always False to prevent inline addition
        """
        return False


class GroupInline(admin.TabularInline):
    """
    Inline admin for group associations (many-to-many relationship).
    
    Allows viewing and editing group associations directly from Initiative admin page.
    """
    model = Initiative.groups.through
    extra = 1
    verbose_name = "Group"
    verbose_name_plural = "Groups"
    can_delete = True
    
    def get_queryset(self, request):
        """
        Optimize queryset for inline display.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset
        """
        return super().get_queryset(request).select_related('organizationalgroup')


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for Initiative model.
    
    Provides comprehensive administrative interface for managing Initiative entities
    with hierarchical relationships, team management, and detailed form layouts.
    """
    
    # List view configuration
    list_display = [
        'name_display',
        'type_display',
        'coordinator_display',
        'start_date_display',
        'end_date_display',
        'team_count_display',
        'children_count_display',
        'group_count_display',
        'hierarchy_level_display',
        'status_display'
    ]
    
    list_display_links = ['name_display']
    
    list_filter = [
        'type',
        'start_date',
        'end_date',
        'coordinator',
        'created_at',
        'updated_at',
        ('parent', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'name',
        'description',
        'coordinator__name',
        'parent__name'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'team_count_display',
        'children_count_display',
        'group_count_display',
        'hierarchy_level_display',
        'coordinator_name',
        'status_display'
    ]
    
    # Form layout configuration
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'type'),
            'description': 'Basic information about the initiative.'
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date'),
            'description': 'Initiative timeline and duration.'
        }),
        ('Relationships', {
            'fields': ('parent', 'coordinator', 'coordinator_name'),
            'description': 'Hierarchical and coordination relationships.'
        }),
        ('Statistics', {
            'fields': ('team_count_display', 'children_count_display', 'group_count_display', 'hierarchy_level_display', 'status_display'),
            'classes': ('collapse',),
            'description': 'Computed statistics and status information.'
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System-generated information and metadata.'
        })
    )
    
    # Inline configuration
    inlines = [TeamMemberInline, ChildInitiativeInline, GroupInline]
    
    # Pagination and performance
    list_per_page = 25
    list_max_show_all = 100
    
    # Ordering
    ordering = ['name']
    
    # Actions
    actions = ['export_selected_initiatives', 'mark_as_completed']
    
    # Autocomplete fields
    autocomplete_fields = ['coordinator', 'parent']
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related and prefetch_related for better performance.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset with related data
        """
        queryset = super().get_queryset(request)
        
        # Optimize with select_related and prefetch_related
        queryset = queryset.select_related(
            'coordinator',
            'parent'
        ).prefetch_related(
            'team_members',
            'children'
        )
        
        # Add annotations for counts to improve performance
        queryset = queryset.annotate(
            annotated_team_count=models.Count('team_members', distinct=True),
            annotated_children_count=models.Count('children', distinct=True),
            annotated_group_count=models.Count('groups', distinct=True)
        )
        
        return queryset
    
    # Custom display methods
    def name_display(self, obj):
        """
        Display initiative name with hierarchy indication.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: Formatted name with hierarchy indicators
        """
        level = obj.get_hierarchy_level()
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * level
        hierarchy_indicator = '└─ ' if level > 0 else ''
        
        return format_html(
            '{}{}<strong>{}</strong>',
            mark_safe(indent),
            hierarchy_indicator,
            obj.name
        )
    name_display.short_description = 'Name'
    name_display.admin_order_field = 'name'
    
    def type_display(self, obj):
        """
        Display initiative type with color coding.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted type with color
        """
        colors = {
            'program': '#2196F3',  # Blue
            'project': '#4CAF50',  # Green
            'event': '#FF9800'     # Orange
        }
        color = colors.get(obj.type.code if obj.type else 'unknown', '#666')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.type.name if obj.type else 'No Type'
        )
    type_display.short_description = 'Type'
    type_display.admin_order_field = 'type__name'
    
    def coordinator_display(self, obj):
        """
        Display coordinator with link to person admin.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted coordinator with link
        """
        if obj.coordinator:
            url = reverse('admin:people_person_change', args=[obj.coordinator.pk])
            return format_html(
                '<a href="{}" title="Edit coordinator">{}</a>',
                url,
                obj.coordinator.full_name
            )
        return format_html('<span style="color: #999;">No coordinator</span>')
    coordinator_display.short_description = 'Coordinator'
    coordinator_display.admin_order_field = 'coordinator__name'
    
    def start_date_display(self, obj):
        """
        Display start date with formatting.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: Formatted start date
        """
        if obj.start_date:
            return obj.start_date.strftime('%Y-%m-%d')
        return format_html('<span style="color: #999;">Not set</span>')
    start_date_display.short_description = 'Start Date'
    start_date_display.admin_order_field = 'start_date'
    
    def end_date_display(self, obj):
        """
        Display end date with formatting.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: Formatted end date or indication if ongoing
        """
        if obj.end_date:
            return obj.end_date.strftime('%Y-%m-%d')
        return format_html('<em style="color: #666;">Ongoing</em>')
    end_date_display.short_description = 'End Date'
    end_date_display.admin_order_field = 'end_date'
    
    def team_count_display(self, obj):
        """
        Display team member count with link.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted team count
        """
        count = getattr(obj, 'annotated_team_count', obj.team_count)
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> member{}',
                count,
                's' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No members</span>')
    team_count_display.short_description = 'Team Size'
    team_count_display.admin_order_field = 'annotated_team_count'
    
    def children_count_display(self, obj):
        """
        Display child initiatives count.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted children count
        """
        count = getattr(obj, 'annotated_children_count', obj.children_count)
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> child{}',
                count,
                'ren' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No children</span>')
    children_count_display.short_description = 'Sub-Initiatives'
    children_count_display.admin_order_field = 'annotated_children_count'
    
    def group_count_display(self, obj):
        """
        Display associated groups count.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted group count
        """
        count = getattr(obj, 'annotated_group_count', 0)
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> group{}',
                count,
                's' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No groups</span>')
    group_count_display.short_description = 'Groups'
    group_count_display.admin_order_field = 'annotated_group_count'
    
    def hierarchy_level_display(self, obj):
        """
        Display hierarchy level.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted hierarchy level
        """
        level = obj.get_hierarchy_level()
        if level == 0:
            return format_html('<strong style="color: #2196F3;">Root</strong>')
        else:
            return format_html('Level <strong>{}</strong>', level)
    hierarchy_level_display.short_description = 'Level'
    
    def status_display(self, obj):
        """
        Display initiative status based on dates.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted status
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        # Handle None start_date
        if not obj.start_date:
            return format_html('<span style="color: #999; font-weight: bold;">Not Scheduled</span>')
        
        if obj.start_date > today:
            return format_html('<span style="color: #FF9800; font-weight: bold;">Upcoming</span>')
        elif obj.end_date and obj.end_date < today:
            return format_html('<span style="color: #666; font-weight: bold;">Completed</span>')
        else:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">Active</span>')
    status_display.short_description = 'Status'
    
    # Custom actions
    def export_selected_initiatives(self, request, queryset):
        """
        Export selected initiatives to CSV format.
        
        Args:
            request: HTTP request object
            queryset: Selected Initiative objects
            
        Returns:
            HttpResponse: CSV file response
        """
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="initiatives_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Type', 'Description', 'Start Date', 'End Date',
            'Coordinator', 'Team Size', 'Children Count', 'Hierarchy Level',
            'Parent', 'Created At'
        ])
        
        for initiative in queryset:
            writer.writerow([
                initiative.id,
                initiative.name,
                initiative.get_type_display(),
                initiative.description,
                initiative.start_date.strftime('%Y-%m-%d') if initiative.start_date else '',
                initiative.end_date.strftime('%Y-%m-%d') if initiative.end_date else '',
                initiative.coordinator.full_name if initiative.coordinator else '',
                initiative.team_count,
                initiative.children_count,
                initiative.get_hierarchy_level(),
                initiative.parent.name if initiative.parent else '',
                initiative.created_at.strftime('%Y-%m-%d %H:%M:%S') if initiative.created_at else ''
            ])
        
        return response
    export_selected_initiatives.short_description = "Export selected initiatives to CSV"
    
    def mark_as_completed(self, request, queryset):
        """
        Mark selected initiatives as completed by setting end_date to today.
        
        Args:
            request: HTTP request object
            queryset: Selected Initiative objects
        """
        from django.utils import timezone
        from django.contrib import messages
        
        today = timezone.now().date()
        updated_count = 0
        
        for initiative in queryset:
            if not initiative.end_date or initiative.end_date > today:
                initiative.end_date = today
                initiative.save()
                updated_count += 1
        
        if updated_count > 0:
            messages.success(
                request,
                f'Successfully marked {updated_count} initiative(s) as completed.'
            )
        else:
            messages.info(request, 'No initiatives were updated.')
    mark_as_completed.short_description = "Mark selected initiatives as completed"
    
    # Form validation and customization
    def save_model(self, request, obj, form, change):
        """
        Custom save method with additional validation.
        
        Args:
            request: HTTP request object
            obj: Initiative instance being saved
            form: Admin form instance
            change: Boolean indicating if this is an update
        """
        # Run model validation
        obj.full_clean()
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Customize form based on user permissions and object state.
        
        Args:
            request: HTTP request object
            obj: Initiative instance (None for add form)
            
        Returns:
            Form class: Customized admin form
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text to fields
        if 'parent' in form.base_fields:
            form.base_fields['parent'].help_text = 'Select parent initiative for hierarchical structure. Leave empty for root-level initiatives.'
        
        if 'end_date' in form.base_fields:
            form.base_fields['end_date'].help_text = 'Leave empty for ongoing initiatives.'
        
        if 'coordinator' in form.base_fields:
            form.base_fields['coordinator'].help_text = 'Person responsible for coordinating this initiative.'
        
        return form
    
    def delete_model(self, request, obj):
        """
        Custom delete method with cascade warnings.
        
        Args:
            request: HTTP request object
            obj: Initiative instance to delete
        """
        children_count = obj.children.count()
        
        if children_count > 0:
            from django.contrib import messages
            messages.warning(
                request,
                f'Deleting "{obj.name}" will also delete {children_count} child initiative(s).'
            )
        
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """
        Custom bulk delete method with cascade warnings.
        
        Args:
            request: HTTP request object
            queryset: QuerySet of Initiative objects to delete
        """
        total_children = sum(initiative.children.count() for initiative in queryset)
        
        if total_children > 0:
            from django.contrib import messages
            messages.warning(
                request,
                f'Bulk deletion will also delete {total_children} child initiative(s).'
            )
        
        super().delete_queryset(request, queryset)
    
    def has_change_permission(self, request, obj=None):
        """
        Check if user can modify initiative based on permissions.
        
        Args:
            request: HTTP request object
            obj: Initiative instance
            
        Returns:
            bool: Whether modification is allowed
        """
        # Check base permissions first
        if not super().has_change_permission(request, obj):
            return False
        
        # Superusers can modify all initiatives
        if request.user.is_superuser:
            return True
        
        # Initiative Coordinators can modify initiatives they coordinate
        if (request.user.groups.filter(name='Initiative Coordinators').exists() and
            obj and obj.coordinator and obj.coordinator.email == request.user.email):
            return True
        
        # Staff users can modify all initiatives
        if request.user.is_staff:
            return True
        
        return False
    
    def has_delete_permission(self, request, obj=None):
        """
        Check if user can delete initiative based on permissions.
        
        Args:
            request: HTTP request object
            obj: Initiative instance
            
        Returns:
            bool: Whether deletion is allowed
        """
        # Check base permissions first
        if not super().has_delete_permission(request, obj):
            return False
        
        # Only superusers and staff can delete initiatives
        return request.user.is_superuser or request.user.is_staff
    
    def has_add_permission(self, request):
        """
        Check if user can add new initiatives.
        
        Args:
            request: HTTP request object
            
        Returns:
            bool: Whether addition is allowed
        """
        # Check base permissions first
        if not super().has_add_permission(request):
            return False
        
        # Initiative Coordinators, staff, and superusers can add initiatives
        return (request.user.is_superuser or 
                request.user.is_staff or
                request.user.groups.filter(name='Initiative Coordinators').exists())
    
    def get_queryset(self, request):
        """
        Filter queryset based on user permissions.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Filtered queryset based on permissions
        """
        queryset = super().get_queryset(request)
        
        # Superusers and staff see all initiatives
        if request.user.is_superuser or request.user.is_staff:
            return queryset
        
        # Initiative Coordinators see only their initiatives
        if request.user.groups.filter(name='Initiative Coordinators').exists():
            return queryset.filter(coordinator__email=request.user.email)
        
        # Viewers see all initiatives (read-only)
        if request.user.groups.filter(name='Viewers').exists():
            return queryset
        
        # Default: no access
        return queryset.none()
    
    # Custom form widgets
    formfield_overrides = {
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget},
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 4})},
        models.DateField: {'widget': admin.widgets.AdminDateWidget},
    }
    
    def get_readonly_fields(self, request, obj=None):
        """
        Customize readonly fields based on object state.
        
        Args:
            request: HTTP request object
            obj: Initiative instance
            
        Returns:
            tuple: Readonly field names
        """
        readonly = list(self.readonly_fields)
        
        # Make certain fields readonly after creation
        if obj and obj.pk:
            # Don't make any additional fields readonly for now
            pass
        
        return readonly

# Register with custom admin site
admin_site.register(Initiative, InitiativeAdmin)
admin_site.register(InitiativeType, InitiativeTypeAdmin)