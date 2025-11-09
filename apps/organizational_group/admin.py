from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import path
from .models import (
    OrganizationalUnit as OrganizationalGroup,
    OrganizationalUnitLeadership as OrganizationalGroupLeadership,
    Campus,
    KnowledgeArea,
    Organization,
    OrganizationalType
)
from .csv_import import ImportProcessor


class OrganizationalUnitInline(admin.TabularInline):
    """
    Inline admin for organizational units within an organization.
    """
    model = OrganizationalGroup
    fk_name = 'organization'
    extra = 0
    can_delete = False
    
    fields = ['name', 'short_name', 'type', 'campus', 'knowledge_area', 'view_link']
    readonly_fields = ['name', 'short_name', 'type', 'campus', 'knowledge_area', 'view_link']
    
    def view_link(self, obj):
        """Display link to view/edit the organizational unit."""
        if obj.pk:
            url = reverse('admin:organizational_group_organizationalunit_change', args=[obj.pk])
            return format_html('<a href="{}">View/Edit</a>', url)
        return '-'
    view_link.short_description = 'Actions'
    
    def has_add_permission(self, request, obj=None):
        """Disable adding units through inline."""
        return False


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for Organization model.
    
    Displays organization information and all its organizational units.
    """
    
    list_display = [
        'name',
        'description_preview',
        'unit_count_display',
        'units_by_type_display',
        'created_at'
    ]
    
    list_display_links = ['name']
    
    search_fields = ['name', 'description']
    
    list_filter = ['created_at', 'updated_at']
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'unit_count_display',
        'units_by_type_display',
        'units_by_campus_display',
        'units_list_display',
        'demanded_initiatives_count_display',
        'demanded_initiatives_list_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Organizational Units', {
            'fields': ('unit_count_display', 'units_by_type_display', 'units_by_campus_display', 'units_list_display'),
            'description': 'Summary of organizational units in this organization.'
        }),
        ('Demanded Initiatives', {
            'fields': ('demanded_initiatives_count_display', 'demanded_initiatives_list_display'),
            'description': 'Initiatives demanded/requested by units in this organization (for Demanding Partners).'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrganizationalUnitInline]
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch."""
        return super().get_queryset(request).prefetch_related(
            'units__type',
            'units__campus',
            'units__knowledge_area',
            'units__demanded_initiatives',
            'units__demanded_initiatives__type'
        )
    
    def description_preview(self, obj):
        """Display truncated description."""
        if obj.description:
            max_length = 60
            if len(obj.description) > max_length:
                return obj.description[:max_length] + '...'
            return obj.description
        return format_html('<span style="color: #999;">No description</span>')
    description_preview.short_description = 'Description'
    
    def unit_count_display(self, obj):
        """Display count of organizational units."""
        count = obj.unit_count()
        if count > 0:
            return format_html(
                '<strong>{}</strong> unit{}',
                count,
                's' if count != 1 else ''
            )
        return format_html('<span style="color: #999;">No units</span>')
    unit_count_display.short_description = 'Units'
    
    def units_by_type_display(self, obj):
        """Display breakdown of units by type."""
        units = obj.units.all()
        if not units:
            return format_html('<span style="color: #999;">No units</span>')
        
        # Count by type
        type_counts = {}
        for unit in units:
            type_name = unit.type.name if unit.type else 'Unknown'
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Format output
        parts = [f'{count} {type_name}' for type_name, count in sorted(type_counts.items())]
        return format_html('<br>'.join(parts))
    units_by_type_display.short_description = 'Units by Type'
    
    def units_by_campus_display(self, obj):
        """Display breakdown of units by campus."""
        units = obj.units.all()
        if not units:
            return format_html('<span style="color: #999;">No units</span>')
        
        # Count by campus
        campus_counts = {}
        for unit in units:
            campus_name = unit.campus.name if unit.campus else 'Unknown'
            campus_counts[campus_name] = campus_counts.get(campus_name, 0) + 1
        
        # Format output
        parts = [f'{count} on {campus}' for campus, count in sorted(campus_counts.items())]
        return format_html('<br>'.join(parts))
    units_by_campus_display.short_description = 'Units by Campus'
    
    def units_list_display(self, obj):
        """Display list of all organizational units with links."""
        units = obj.units.all().order_by('name')
        if not units:
            return format_html('<span style="color: #999;">No organizational units</span>')
        
        links = []
        for unit in units:
            url = reverse('admin:organizational_group_organizationalunit_change', args=[unit.pk])
            type_name = unit.type.name if unit.type else 'Unknown'
            campus_name = unit.campus.name if unit.campus else 'Unknown'
            links.append(format_html(
                '<a href="{}" title="Type: {} | Campus: {}">{}</a> <span style="color: #666;">({} - {})</span>',
                url,
                type_name,
                campus_name,
                unit.name,
                type_name,
                campus_name
            ))
        
        return format_html('<br>'.join(links))
    units_list_display.short_description = 'Organizational Units List'
    
    def demanded_initiatives_count_display(self, obj):
        """Display count of initiatives demanded by units in this organization."""
        # Get all units in this organization
        units = obj.units.all()
        
        # Count total demanded initiatives across all units
        total_count = 0
        for unit in units:
            if hasattr(unit, 'demanded_initiatives'):
                total_count += unit.demanded_initiatives.count()
        
        if total_count > 0:
            return format_html(
                '<strong>{}</strong> initiative{} demanded',
                total_count,
                's' if total_count != 1 else ''
            )
        return format_html('<span style="color: #999;">No demanded initiatives</span>')
    demanded_initiatives_count_display.short_description = 'Demanded Initiatives'
    
    def demanded_initiatives_list_display(self, obj):
        """Display list of initiatives demanded by units in this organization."""
        # Get all units in this organization
        units = obj.units.all()
        
        # Collect all demanded initiatives
        initiatives_by_unit = []
        for unit in units:
            if hasattr(unit, 'demanded_initiatives'):
                demanded = unit.demanded_initiatives.all()
                if demanded:
                    initiatives_by_unit.append((unit, demanded))
        
        if not initiatives_by_unit:
            return format_html('<span style="color: #999;">No initiatives demanded by units in this organization</span>')
        
        # Format output grouped by unit
        output_parts = []
        for unit, initiatives in initiatives_by_unit:
            unit_url = reverse('admin:organizational_group_organizationalunit_change', args=[unit.pk])
            output_parts.append(format_html(
                '<strong><a href="{}">{}</a></strong> demands:',
                unit_url,
                unit.name
            ))
            
            for initiative in initiatives:
                init_url = reverse('admin:initiatives_initiative_change', args=[initiative.pk])
                output_parts.append(format_html(
                    '&nbsp;&nbsp;• <a href="{}" title="View initiative">{}</a> <span style="color: #666;">({})</span>',
                    init_url,
                    initiative.name,
                    initiative.type.name if initiative.type else 'Unknown'
                ))
        
        return format_html('<br>'.join(output_parts))
    demanded_initiatives_list_display.short_description = 'Demanded Initiatives List'


@admin.register(OrganizationalType)
class OrganizationalTypeAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for OrganizationalType model.
    """
    
    list_display = [
        'name',
        'code',
        'description_preview',
        'unit_count_display',
        'created_at'
    ]
    
    list_display_links = ['name']
    
    search_fields = ['name', 'code', 'description']
    
    list_filter = ['created_at', 'updated_at']
    
    readonly_fields = ['id', 'created_at', 'updated_at', 'unit_count_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def description_preview(self, obj):
        """Display truncated description."""
        if obj.description:
            max_length = 60
            if len(obj.description) > max_length:
                return obj.description[:max_length] + '...'
            return obj.description
        return format_html('<span style="color: #999;">No description</span>')
    description_preview.short_description = 'Description'
    
    def unit_count_display(self, obj):
        """Display count of organizational units of this type."""
        count = obj.units.count()
        if count > 0:
            return format_html(
                '<strong>{}</strong> unit{}',
                count,
                's' if count != 1 else ''
            )
        return format_html('<span style="color: #999;">No units</span>')
    unit_count_display.short_description = 'Units'


@admin.register(KnowledgeArea)
class KnowledgeAreaAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for KnowledgeArea model.
    
    Provides comprehensive administrative interface for managing KnowledgeArea entities
    with proper display, filtering, and search capabilities.
    """
    
    # List view configuration
    list_display = [
        'name',
        'description_preview',
        'group_count_display',
        'created_at'
    ]
    
    list_display_links = ['name']
    
    list_filter = [
        'created_at',
        'updated_at'
    ]
    
    # Search fields
    search_fields = [
        'name',
        'description'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'group_count_display'
    ]
    
    # Form layout configuration
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description'),
            'description': 'Basic information about the knowledge area.'
        }),
        ('Statistics', {
            'fields': ('group_count_display',),
            'classes': ('collapse',),
            'description': 'Computed statistics.'
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System-generated information and metadata.'
        })
    )
    
    # Pagination and performance
    list_per_page = 25
    list_max_show_all = 100
    
    # Ordering
    ordering = ['name']
    
    def get_queryset(self, request):
        """
        Optimize queryset with annotations for better performance.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset with annotated group count
        """
        queryset = super().get_queryset(request)
        
        # Add annotation for group count to improve performance
        queryset = queryset.annotate(
            annotated_group_count=models.Count('units', distinct=True)
        )
        
        return queryset
    
    def description_preview(self, obj):
        """
        Display truncated description.
        
        Args:
            obj (KnowledgeArea): KnowledgeArea instance
            
        Returns:
            str: Truncated description
        """
        if obj.description:
            max_length = 60
            if len(obj.description) > max_length:
                return obj.description[:max_length] + '...'
            return obj.description
        return format_html('<span style="color: #999;">No description</span>')
    description_preview.short_description = 'Description'
    
    def group_count_display(self, obj):
        """
        Display count of organizational groups in this knowledge area with HTML formatting.
        
        Args:
            obj (KnowledgeArea): KnowledgeArea instance
            
        Returns:
            str: HTML formatted group count
        """
        count = getattr(obj, 'annotated_group_count', obj.group_count())
        
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
    
    def save_model(self, request, obj, form, change):
        """
        Custom save method with additional validation.
        
        Args:
            request: HTTP request object
            obj: KnowledgeArea instance being saved
            form: Admin form instance
            change: Boolean indicating if this is an update
        """
        # Run model validation
        obj.full_clean()
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Customize form with helpful text.
        
        Args:
            request: HTTP request object
            obj: KnowledgeArea instance (None for add form)
            
        Returns:
            Form class: Customized admin form
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text to fields
        if 'name' in form.base_fields:
            form.base_fields['name'].help_text = 'Knowledge area name (must be unique, case-insensitive).'
        
        if 'description' in form.base_fields:
            form.base_fields['description'].help_text = 'Detailed description of the knowledge area (optional).'
        
        return form


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for Campus model.
    
    Provides comprehensive administrative interface for managing Campus entities
    with proper display, filtering, and search capabilities.
    """
    
    # List view configuration
    list_display = [
        'name',
        'code',
        'location',
        'group_count_display',
        'created_at'
    ]
    
    list_display_links = ['name']
    
    list_filter = [
        'created_at',
        'updated_at'
    ]
    
    # Search fields
    search_fields = [
        'name',
        'code',
        'location'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'group_count_display'
    ]
    
    # Form layout configuration
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'location'),
            'description': 'Basic information about the campus.'
        }),
        ('Statistics', {
            'fields': ('group_count_display',),
            'classes': ('collapse',),
            'description': 'Computed statistics.'
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System-generated information and metadata.'
        })
    )
    
    # Pagination and performance
    list_per_page = 25
    list_max_show_all = 100
    
    # Ordering
    ordering = ['name']
    
    def get_queryset(self, request):
        """
        Optimize queryset with annotations for better performance.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset with annotated group count
        """
        queryset = super().get_queryset(request)
        
        # Add annotation for group count to improve performance
        queryset = queryset.annotate(
            annotated_group_count=models.Count('units', distinct=True)
        )
        
        return queryset
    
    def group_count_display(self, obj):
        """
        Display count of organizational units on this campus with HTML formatting.
        
        Args:
            obj (Campus): Campus instance
            
        Returns:
            str: HTML formatted group count
        """
        count = getattr(obj, 'annotated_group_count', obj.group_count())
        
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
    
    def save_model(self, request, obj, form, change):
        """
        Custom save method with additional validation.
        
        Args:
            request: HTTP request object
            obj: Campus instance being saved
            form: Admin form instance
            change: Boolean indicating if this is an update
        """
        # Run model validation
        obj.full_clean()
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Customize form with helpful text.
        
        Args:
            request: HTTP request object
            obj: Campus instance (None for add form)
            
        Returns:
            Form class: Customized admin form
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text to fields
        if 'name' in form.base_fields:
            form.base_fields['name'].help_text = 'Full campus name.'
        
        if 'code' in form.base_fields:
            form.base_fields['code'].help_text = 'Short campus code/identifier (will be auto-uppercased).'
        
        if 'location' in form.base_fields:
            form.base_fields['location'].help_text = 'Physical location or address (optional).'
        
        return form


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
    
    # Change list template to add custom button
    change_list_template = 'admin/organizational_group/organizationalgroup/change_list.html'
    
    # List view configuration
    list_display = [
        'name',
        'short_name',
        'type_display',
        'campus_display',
        'knowledge_area_display',
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
        'knowledge_area__name',
        'campus__name',
        'campus__code'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'leader_count_display',
        'member_count_display',
        'initiative_count_display',
        'demanded_initiatives_count_display',
        'demanded_initiatives_list_display'
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
        ('Demanded Initiatives', {
            'fields': ('demanded_initiatives_count_display', 'demanded_initiatives_list_display'),
            'description': 'Initiatives demanded/requested by this organizational unit (for demanding partners).'
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
    autocomplete_fields = ['campus', 'knowledge_area']
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related and prefetch_related for better performance.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset with related data
        """
        queryset = super().get_queryset(request)
        
        # Optimize with select_related for foreign keys
        queryset = queryset.select_related('campus', 'knowledge_area')
        
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
                'organizationalunitleadership',
                filter=models.Q(organizationalunitleadership__is_active=True),
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
        if not obj.type:
            return '-'
        
        colors = {
            'research': '#2196F3',  # Blue
            'extension': '#4CAF50'  # Green
        }
        color = colors.get(obj.type.code if obj.type else None, '#666')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.type.name
        )
    type_display.short_description = 'Type'
    type_display.admin_order_field = 'type'
    
    def campus_display(self, obj):
        """
        Display campus name with code.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            str: HTML formatted campus name with code
        """
        if obj.campus:
            return format_html(
                '{} <span style="color: #999;">({})</span>',
                obj.campus.name,
                obj.campus.code
            )
        else:
            return format_html('<span style="color: #999;">No campus</span>')
    campus_display.short_description = 'Campus'
    campus_display.admin_order_field = 'campus__name'
    
    def knowledge_area_display(self, obj):
        """
        Display knowledge area name with HTML formatting.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            str: HTML formatted knowledge area name
        """
        if obj.knowledge_area:
            return format_html(
                '<strong>{}</strong>',
                obj.knowledge_area.name
            )
        else:
            return format_html('<span style="color: #999;">No knowledge area</span>')
    knowledge_area_display.short_description = 'Knowledge Area'
    knowledge_area_display.admin_order_field = 'knowledge_area__name'
    
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
    
    def demanded_initiatives_count_display(self, obj):
        """
        Display count of initiatives demanded by this organizational unit.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            str: HTML formatted demanded initiatives count
        """
        if hasattr(obj, 'demanded_initiatives'):
            count = obj.demanded_initiatives.count()
            if count > 0:
                return format_html(
                    '<strong>{}</strong> initiative{} demanded',
                    count,
                    's' if count != 1 else ''
                )
        return format_html('<span style="color: #999;">No demanded initiatives</span>')
    demanded_initiatives_count_display.short_description = 'Demanded Initiatives'
    
    def demanded_initiatives_list_display(self, obj):
        """
        Display list of initiatives demanded by this organizational unit.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            str: HTML formatted list of demanded initiatives
        """
        if not hasattr(obj, 'demanded_initiatives'):
            return format_html('<span style="color: #999;">No demanded initiatives</span>')
        
        initiatives = obj.demanded_initiatives.all().select_related('type', 'coordinator')
        
        if not initiatives:
            return format_html('<span style="color: #999;">This unit has not demanded any initiatives</span>')
        
        links = []
        for initiative in initiatives:
            url = reverse('admin:initiatives_initiative_change', args=[initiative.pk])
            type_name = initiative.type.name if initiative.type else 'Unknown'
            coordinator_name = initiative.coordinator.full_name if initiative.coordinator else 'No coordinator'
            
            links.append(format_html(
                '<a href="{}" title="Coordinator: {}">{}</a> <span style="color: #666;">({})</span>',
                url,
                coordinator_name,
                initiative.name,
                type_name
            ))
        
        return format_html('<br>'.join(links))
    demanded_initiatives_list_display.short_description = 'Demanded Initiatives List'
    
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
            form.base_fields['knowledge_area'].help_text = 'Select the knowledge area for this group. Use the search icon to find or create a knowledge area.'
        
        if 'campus' in form.base_fields:
            form.base_fields['campus'].help_text = 'University campus affiliation.'
        
        return form
    
    # Custom form widgets
    formfield_overrides = {
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget},
        models.URLField: {'widget': admin.widgets.AdminURLFieldWidget},
    }
    
    def get_urls(self):
        """
        Add custom URL for CSV import.
        
        Returns:
            List of URL patterns
        """
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='organizational_group_import_csv'),
        ]
        return custom_urls + urls
    
    def import_csv_view(self, request):
        """
        Custom view for CSV import.
        
        Args:
            request: HTTP request object
            
        Returns:
            HttpResponse: Rendered template or redirect
        """
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, 'Please select a CSV file to upload.')
                return HttpResponseRedirect(request.path)
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File must be a CSV file (.csv extension).')
                return HttpResponseRedirect(request.path)
            
            # Process the CSV file
            try:
                processor = ImportProcessor()
                reporter = processor.process_csv(csv_file)
                
                # Display success message
                if reporter.success_count > 0:
                    messages.success(
                        request,
                        f'Successfully imported {reporter.success_count} organizational group(s).'
                    )
                
                # Display skip message
                if reporter.skip_count > 0:
                    messages.warning(
                        request,
                        f'Skipped {reporter.skip_count} duplicate group(s).'
                    )
                
                # Display errors
                if reporter.has_errors:
                    messages.error(
                        request,
                        f'{reporter.error_count} error(s) occurred during import. See details below.'
                    )
                    
                    # Show first 10 errors
                    for error in reporter.get_errors()[:10]:
                        messages.error(
                            request,
                            f'Row {error["row"]}: {error["message"]}'
                        )
                    
                    if len(reporter.get_errors()) > 10:
                        messages.warning(
                            request,
                            f'... and {len(reporter.get_errors()) - 10} more error(s).'
                        )
                
                # Redirect back to changelist
                return HttpResponseRedirect('../')
            
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
                return HttpResponseRedirect(request.path)
        
        # Show upload form
        context = {
            'title': 'Import Research Groups from CSV',
            'site_title': self.admin_site.site_title,
            'site_header': self.admin_site.site_header,
            'has_permission': True,
        }
        
        return render(
            request,
            'admin/organizational_group/import_csv.html',
            context
        )
