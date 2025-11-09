from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from .models import OrganizationalGroup, OrganizationalGroupLeadership


class OrganizationalGroupLeadershipInline(admin.TabularInline):
    """
    Inline admin for managing leaders with history.
    
    Allows editing leadership relationships directly from the OrganizationalGroup admin page,
    including historical tracking with start/end dates.
    """
    model = OrganizationalGroupLeadership
    extra = 1
    verbose_name = "Leader"
    verbose_name_plural = "Leaders"
    can_delete = True
    
    fields = ['person', 'start_date', 'end_date', 'is_active']
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


class OrganizationalGroupMemberInline(admin.TabularInline):
    """
    Inline admin for managing members.
    
    Allows editing member assignments directly from the OrganizationalGroup admin page.
    """
    model = OrganizationalGroup.members.through
    extra = 1
    verbose_name = "Member"
    verbose_name_plural = "Members"
    can_delete = True
    
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


class OrganizationalGroupInitiativeInline(admin.TabularInline):
    """
    Inline admin for managing initiative associations.
    
    Allows editing initiative associations directly from the OrganizationalGroup admin page.
    """
    model = OrganizationalGroup.initiatives.through
    extra = 1
    verbose_name = "Initiative"
    verbose_name_plural = "Initiatives"
    can_delete = True
    
    autocomplete_fields = ['initiative']
    
    def get_queryset(self, request):
        """
        Optimize queryset for inline display.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset
        """
        return super().get_queryset(request).select_related('initiative')


@admin.register(OrganizationalGroup)
class OrganizationalGroupAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for OrganizationalGroup model.
    
    Provides comprehensive administrative interface for managing OrganizationalGroup entities
    with leaders, members, and initiative associations.
    """
    
    # List view configuration
    list_display = [
        'name',
        'short_name',
        'type_display',
        'campus',
        'knowledge_area',
        'leader_count_display',
        'member_count_display',
        'initiative_count_display',
        'created_at'
    ]
    
    list_display_links = ['name']
    
    list_filter = [
        'type',
        'campus',
        'knowledge_area',
        'created_at',
        'updated_at'
    ]
    
    # Search fields required for autocomplete functionality
    search_fields = [
        'name',
        'short_name',
        'knowledge_area',
        'campus'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'leader_count_display',
        'member_count_display',
        'initiative_count_display'
    ]
    
    # Form layout configuration
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_name', 'url'),
            'description': 'Basic information about the group.'
        }),
        ('Classification', {
            'fields': ('type', 'knowledge_area', 'campus'),
            'description': 'Group classification and affiliation.'
        }),
        ('Statistics', {
            'fields': ('leader_count_display', 'member_count_display', 'initiative_count_display'),
            'classes': ('collapse',),
            'description': 'Computed statistics.'
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System-generated information and metadata.'
        })
    )
    
    # Inline configuration
    inlines = [OrganizationalGroupLeadershipInline, OrganizationalGroupMemberInline, OrganizationalGroupInitiativeInline]
    
    # Pagination and performance
    list_per_page = 25
    list_max_show_all = 100
    
    # Ordering
    ordering = ['name']
    
    # Autocomplete fields
    autocomplete_fields = []
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related and prefetch_related for better performance.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset with related data
        """
        queryset = super().get_queryset(request)
        
        # Optimize with prefetch_related
        queryset = queryset.prefetch_related(
            'leaders',
            'members',
            'initiatives'
        )
        
        # Add annotations for counts to improve performance
        queryset = queryset.annotate(
            annotated_member_count=models.Count('members', distinct=True),
            annotated_initiative_count=models.Count('initiatives', distinct=True),
            annotated_leader_count=models.Count(
                'organizationalgroupleadership',
                filter=models.Q(organizationalgroupleadership__is_active=True),
                distinct=True
            )
        )
        
        return queryset
    
    # Custom display methods
    def type_display(self, obj):
        """
        Display group type with color coding.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            str: HTML formatted type with color
        """
        colors = {
            'research': '#2196F3',  # Blue
            'extension': '#4CAF50'  # Green
        }
        color = colors.get(obj.type, '#666')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_type_display()
        )
    type_display.short_description = 'Type'
    type_display.admin_order_field = 'type'
    
    def leader_count_display(self, obj):
        """
        Display current leader count.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            str: HTML formatted leader count
        """
        count = getattr(obj, 'annotated_leader_count', obj.leader_count())
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> leader{}',
                count,
                's' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No leaders</span>')
    leader_count_display.short_description = 'Leaders'
    leader_count_display.admin_order_field = 'annotated_leader_count'
    
    def member_count_display(self, obj):
        """
        Display member count.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            str: HTML formatted member count
        """
        count = getattr(obj, 'annotated_member_count', obj.member_count())
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> member{}',
                count,
                's' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No members</span>')
    member_count_display.short_description = 'Members'
    member_count_display.admin_order_field = 'annotated_member_count'
    
    def initiative_count_display(self, obj):
        """
        Display initiative count.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            str: HTML formatted initiative count
        """
        count = getattr(obj, 'annotated_initiative_count', obj.initiative_count())
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> initiative{}',
                count,
                's' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No initiatives</span>')
    initiative_count_display.short_description = 'Initiatives'
    initiative_count_display.admin_order_field = 'annotated_initiative_count'
    
    # Form validation and customization
    def save_model(self, request, obj, form, change):
        """
        Custom save method with additional validation.
        
        Args:
            request: HTTP request object
            obj: OrganizationalGroup instance being saved
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
            obj: OrganizationalGroup instance (None for add form)
            
        Returns:
            Form class: Customized admin form
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text to fields
        if 'url' in form.base_fields:
            form.base_fields['url'].help_text = 'Group website URL (optional).'
        
        if 'type' in form.base_fields:
            form.base_fields['type'].help_text = 'Select the type of group (Research or Extension).'
        
        if 'knowledge_area' in form.base_fields:
            form.base_fields['knowledge_area'].help_text = 'Field of study or research domain.'
        
        if 'campus' in form.base_fields:
            form.base_fields['campus'].help_text = 'University campus affiliation.'
        
        return form
    
    # Custom form widgets
    formfield_overrides = {
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget},
        models.URLField: {'widget': admin.widgets.AdminURLFieldWidget},
    }
