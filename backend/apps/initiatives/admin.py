from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Initiative, InitiativeType, FailedInitiativeImport, InitiativeCoordinatorChange
from apps.core.admin import admin_site
from .csv_import.processor import ResearchProjectImportProcessor


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


class StudentInline(admin.TabularInline):
    """
    Inline admin for student relationships (many-to-many).
    
    Allows editing student assignments directly from the Initiative admin page.
    """
    model = Initiative.students.through
    extra = 1
    verbose_name = "Student"
    verbose_name_plural = "Students"
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


class UnitInline(admin.TabularInline):
    """
    Inline admin for organizational unit associations (many-to-many relationship).
    
    Allows viewing and editing unit associations directly from Initiative admin page.
    """
    model = Initiative.units.through
    extra = 1
    verbose_name = "Organizational Unit"
    verbose_name_plural = "Organizational Units"
    can_delete = True
    
    def get_queryset(self, request):
        """
        Optimize queryset for inline display.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized queryset
        """
        return super().get_queryset(request).select_related('organizationalunit')


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
        'campus_display',
        'coordinator_display',
        'demanding_partner_display',
        'knowledge_areas_display',
        'start_date_display',
        'end_date_display',
        'team_count_display',
        'student_count_display',
        'children_count_display',
        'unit_count_display',
        'external_groups_count_display',
        'hierarchy_level_display',
        'status_display'
    ]
    
    list_display_links = ['name_display']
    
    list_filter = [
        'type',
        'campus',
        'knowledge_areas',
        'demanding_partner',
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
        'student_count_display',
        'children_count_display',
        'unit_count_display',
        'partnerships_count_display',
        'external_groups_count_display',
        'external_groups_list_display',
        'knowledge_areas_count_display',
        'hierarchy_level_display',
        'coordinator_name',
        'demanding_partner_display',
        'status_display'
    ]
    
    # Form layout configuration
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'type', 'campus'),
            'description': 'Basic information about the initiative.'
        }),
        ('Knowledge Areas', {
            'fields': ('knowledge_areas',),
            'description': 'Knowledge areas associated with this initiative.'
        }),
        ('Organizations', {
            'fields': ('demanding_partner', 'demanding_partner_display', 'partnerships', 'partnerships_count_display', 'external_groups_count_display', 'external_groups_list_display'),
            'description': 'Organizational relationships: demanding partner organization, partnerships, and research groups.'
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
            'fields': ('team_count_display', 'student_count_display', 'children_count_display', 'unit_count_display', 'knowledge_areas_count_display', 'hierarchy_level_display', 'status_display'),
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
    inlines = [TeamMemberInline, StudentInline, ChildInitiativeInline, UnitInline]
    
    # Pagination and performance
    list_per_page = 25
    list_max_show_all = 100
    
    # Ordering
    ordering = ['name']
    
    # Actions
    actions = ['export_selected_initiatives', 'mark_as_completed']
    
    # Autocomplete fields
    autocomplete_fields = ['coordinator', 'parent']
    
    # Filter horizontal for many-to-many fields
    filter_horizontal = ['knowledge_areas', 'team_members', 'students', 'partnerships']
    
    # Custom changelist template
    change_list_template = 'admin/initiatives/initiative/change_list.html'
    
    def get_urls(self):
        """
        Add custom URL for CSV import.
        
        Returns:
            list: URL patterns
        """
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='initiatives_initiative_import_csv'),
        ]
        return custom_urls + urls
    
    def import_csv_view(self, request):
        """
        Handle CSV import view - supports single CSV or bulk ZIP import.
        
        Args:
            request: HTTP request object
            
        Returns:
            HttpResponse: Rendered template or redirect
        """
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, 'Please select a file to upload.')
                return redirect('..')
            
            # Check if bulk import (ZIP file)
            is_bulk = csv_file.name.lower().endswith('.zip')
            
            if is_bulk:
                # Process bulk import
                from apps.core.csv_import.bulk_handler import BulkImportHandler, BulkImportReporter
                
                bulk_handler = BulkImportHandler()
                csv_files = bulk_handler.process_upload(csv_file)
                
                if bulk_handler.has_errors():
                    for error in bulk_handler.get_errors():
                        messages.error(request, error)
                    return redirect('..')
                
                if not csv_files:
                    messages.error(request, 'No CSV files found in the uploaded ZIP.')
                    return redirect('..')
                
                # Process each CSV file
                bulk_reporter = BulkImportReporter()
                processor = ResearchProjectImportProcessor()
                
                for csv_info in csv_files:
                    file_reporter = processor.process_csv(csv_info['content'])
                    bulk_reporter.add_file_result(csv_info['name'], file_reporter)
                
                # Display bulk summary
                summary = bulk_reporter.get_summary()
                
                messages.success(
                    request,
                    f"Bulk import completed: {summary['total_files']} file(s) processed"
                )
                
                if summary['total_successes'] > 0:
                    messages.success(
                        request,
                        f"Successfully imported {summary['total_successes']} research project(s)"
                    )
                
                if summary['total_skips'] > 0:
                    messages.warning(
                        request,
                        f"Skipped {summary['total_skips']} duplicate project(s)"
                    )
                
                if summary['total_errors'] > 0:
                    messages.error(
                        request,
                        f"Encountered {summary['total_errors']} error(s) during import"
                    )
                    
                    # Show per-file error summary
                    for file_result in summary['file_results']:
                        if file_result['errors'] > 0:
                            messages.warning(
                                request,
                                f"{file_result['filename']}: {file_result['errors']} error(s)"
                            )
                
            else:
                # Single CSV import
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'Please upload a CSV file (.csv) or ZIP archive (.zip).')
                    return redirect('..')
                
                # Process CSV
                processor = ResearchProjectImportProcessor()
                reporter = processor.process_csv(csv_file)
                
                # Display success messages
                if reporter.success_count > 0:
                    messages.success(
                        request,
                        f'Successfully imported {reporter.success_count} research project(s).'
                    )
                
                # Display warning messages for skipped rows
                if reporter.skip_count > 0:
                    messages.warning(
                        request,
                        f'Skipped {reporter.skip_count} duplicate project(s).'
                    )
                
                # Display error messages (limit to first 10)
                if reporter.has_errors():
                    error_count = len(reporter.get_errors())
                    messages.error(
                        request,
                        f'Encountered {error_count} error(s) during import.'
                    )
                    
                    # Show first 10 errors
                    for error in reporter.get_errors()[:10]:
                        messages.error(
                            request,
                            f"Row {error['row']}: {error['message']}"
                        )
                    
                    if error_count > 10:
                        messages.warning(
                            request,
                            f'... and {error_count - 10} more error(s). Check logs for details.'
                        )
            
            return redirect('..')
        
        # GET request - show upload form
        context = {
            'site_title': 'Import Research Projects',
            'title': 'Import Research Projects from CSV',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        
        return render(request, 'admin/initiatives/initiative/import_csv.html', context)
    
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
            'parent',
            'type',
            'campus'
        ).prefetch_related(
            'team_members',
            'students',
            'children',
            'knowledge_areas',
            'units',
            'partnerships'
        )
        
        # Add annotations for counts to improve performance
        queryset = queryset.annotate(
            annotated_team_count=models.Count('team_members', distinct=True),
            annotated_student_count=models.Count('students', distinct=True),
            annotated_children_count=models.Count('children', distinct=True),
            annotated_unit_count=models.Count('units', distinct=True)
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
    
    def campus_display(self, obj):
        """
        Display campus with link to campus admin.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted campus with link
        """
        if obj.campus:
            url = reverse('admin:organizational_group_campus_change', args=[obj.campus.pk])
            return format_html(
                '<a href="{}" title="View campus">{}</a>',
                url,
                obj.campus.name
            )
        return format_html('<span style="color: #999;">No campus</span>')
    campus_display.short_description = 'Campus'
    campus_display.admin_order_field = 'campus__name'
    
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
    
    def knowledge_areas_display(self, obj):
        """
        Display knowledge areas as comma-separated list.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted knowledge areas
        """
        knowledge_areas = obj.knowledge_areas.all()
        if knowledge_areas:
            ka_names = [ka.name for ka in knowledge_areas]
            if len(ka_names) > 2:
                # Show first 2 and count
                display = ', '.join(ka_names[:2])
                remaining = len(ka_names) - 2
                return format_html(
                    '<span title="{}">{} <em>(+{} more)</em></span>',
                    ', '.join(ka_names),
                    display,
                    remaining
                )
            else:
                return ', '.join(ka_names)
        return format_html('<span style="color: #999;">None</span>')
    knowledge_areas_display.short_description = 'Knowledge Areas'
    
    def knowledge_areas_count_display(self, obj):
        """
        Display knowledge areas count.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted knowledge areas count
        """
        count = obj.knowledge_areas.count()
        
        if count > 0:
            ka_names = [ka.name for ka in obj.knowledge_areas.all()]
            return format_html(
                '<span title="{}">{} area{}</span>',
                ', '.join(ka_names),
                count,
                's' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No areas</span>')
    knowledge_areas_count_display.short_description = 'Knowledge Areas'
    
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
    
    def student_count_display(self, obj):
        """
        Display student count.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted student count
        """
        count = getattr(obj, 'annotated_student_count', obj.student_count)
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> student{}',
                count,
                's' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No students</span>')
    student_count_display.short_description = 'Students'
    student_count_display.admin_order_field = 'annotated_student_count'
    
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
    
    def unit_count_display(self, obj):
        """
        Display associated organizational units count.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted unit count
        """
        count = getattr(obj, 'annotated_unit_count', 0)
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> unit{}',
                count,
                's' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No units</span>')
    unit_count_display.short_description = 'Units'
    unit_count_display.admin_order_field = 'annotated_unit_count'
    
    def partnerships_count_display(self, obj):
        """
        Display partnerships count.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted partnerships count
        """
        count = obj.partnerships_count
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> partnership{}',
                count,
                's' if count != 1 else ''
            )
        else:
            return format_html('<span style="color: #999;">No partnerships</span>')
    partnerships_count_display.short_description = 'Partnerships'
    
    def demanding_partner_display(self, obj):
        """
        Display demanding partner organization with link.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted demanding partner with link
        """
        if obj.demanding_partner:
            url = reverse('admin:organizational_group_organization_change', args=[obj.demanding_partner.pk])
            return format_html(
                '<a href="{}" title="View demanding partner">{}</a>',
                url,
                obj.demanding_partner.name
            )
        return format_html('<span style="color: #999;">None</span>')
    demanding_partner_display.short_description = 'Demanding Partner'
    demanding_partner_display.admin_order_field = 'demanding_partner__name'
    
    def external_groups_count_display(self, obj):
        """
        Display count of external research groups.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted external groups count
        """
        count = obj.external_research_groups_count
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> research group{}',
                count,
                's' if count != 1 else ''
            )
        return format_html('<span style="color: #999;">No research groups</span>')
    external_groups_count_display.short_description = 'Research Groups'
    
    def external_groups_list_display(self, obj):
        """
        Display list of external research groups with links.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            str: HTML formatted list of external groups
        """
        external_groups = obj.external_research_groups.all()
        
        if external_groups:
            links = []
            for group in external_groups:
                url = reverse('admin:organizational_group_organizationalunit_change', args=[group.pk])
                links.append(format_html(
                    '<a href="{}" title="View {}">{}</a>',
                    url,
                    group.name,
                    group.name
                ))
            return format_html('<br>'.join(links))
        return format_html('<span style="color: #999;">No research groups</span>')
    external_groups_list_display.short_description = 'Research Groups'
    
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



@admin.register(FailedInitiativeImport)
class FailedInitiativeImportAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for FailedInitiativeImport model.
    
    Provides interface for viewing and managing failed CSV imports.
    """
    
    list_display = [
        'row_number',
        'title_display',
        'coordinator_display',
        'campus_display',
        'error_reason_short',
        'import_date',
        'resolved_display'
    ]
    
    list_filter = [
        'resolved',
        'import_date',
    ]
    
    search_fields = [
        'error_reason',
        'raw_data',
        'resolution_notes'
    ]
    
    readonly_fields = [
        'row_number',
        'error_reason',
        'raw_data_display',
        'import_date',
        'title_display',
        'coordinator_display',
        'coordinator_email_display',
        'start_date_display',
        'end_date_display',
        'campus_display'
    ]
    
    fieldsets = (
        ('Import Information', {
            'fields': ('row_number', 'import_date', 'error_reason')
        }),
        ('CSV Data', {
            'fields': (
                'title_display',
                'coordinator_display',
                'coordinator_email_display',
                'start_date_display',
                'end_date_display',
                'campus_display',
                'raw_data_display'
            ),
            'description': 'Data from the failed CSV row'
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolution_notes'),
            'description': 'Mark as resolved once the issue is fixed'
        })
    )
    
    list_per_page = 50
    ordering = ['-import_date', 'row_number']
    
    actions = ['mark_as_resolved', 'mark_as_unresolved']
    
    def title_display(self, obj):
        """Display the initiative title from raw data."""
        return obj.get_title()
    title_display.short_description = 'Title'
    
    def coordinator_display(self, obj):
        """Display the coordinator name from raw data."""
        return obj.get_coordinator()
    coordinator_display.short_description = 'Coordinator'
    
    def coordinator_email_display(self, obj):
        """Display the coordinator email from raw data."""
        return obj.get_coordinator_email()
    coordinator_email_display.short_description = 'Coordinator Email'
    
    def start_date_display(self, obj):
        """Display the start date from raw data."""
        return obj.get_start_date()
    start_date_display.short_description = 'Start Date'
    
    def end_date_display(self, obj):
        """Display the end date from raw data."""
        return obj.get_end_date()
    end_date_display.short_description = 'End Date'
    
    def campus_display(self, obj):
        """Display the campus from raw data."""
        campus = obj.get_campus()
        if campus and campus != 'Unknown':
            return campus
        return format_html('<span style="color: #999;">Not specified</span>')
    campus_display.short_description = 'Campus'
    
    def error_reason_short(self, obj):
        """Display shortened error reason."""
        if len(obj.error_reason) > 100:
            return format_html(
                '<span title="{}">{}</span>',
                obj.error_reason,
                obj.error_reason[:100] + '...'
            )
        return obj.error_reason
    error_reason_short.short_description = 'Error Reason'
    
    def resolved_display(self, obj):
        """Display resolved status with color."""
        if obj.resolved:
            return format_html(
                '<span style="color: #4CAF50; font-weight: bold;">✓ Resolved</span>'
            )
        return format_html(
            '<span style="color: #FF9800; font-weight: bold;">✗ Unresolved</span>'
        )
    resolved_display.short_description = 'Status'
    resolved_display.admin_order_field = 'resolved'
    
    def raw_data_display(self, obj):
        """Display formatted raw data."""
        formatted = obj.get_formatted_data()
        return format_html(
            '<pre style="background: #f5f5f5; padding: 10px; border: 1px solid #ddd; overflow-x: auto;">{}</pre>',
            formatted
        )
    raw_data_display.short_description = 'Raw CSV Data'
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected failed imports as resolved."""
        updated = queryset.update(resolved=True)
        self.message_user(
            request,
            f'Successfully marked {updated} failed import(s) as resolved.',
            messages.SUCCESS
        )
    mark_as_resolved.short_description = "Mark selected as resolved"
    
    def mark_as_unresolved(self, request, queryset):
        """Mark selected failed imports as unresolved."""
        updated = queryset.update(resolved=False)
        self.message_user(
            request,
            f'Successfully marked {updated} failed import(s) as unresolved.',
            messages.SUCCESS
        )
    mark_as_unresolved.short_description = "Mark selected as unresolved"
    
    def has_add_permission(self, request):
        """Disable manual addition of failed imports."""
        return False
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request)


# Register with custom admin site
admin_site.register(FailedInitiativeImport, FailedInitiativeImportAdmin)



@admin.register(InitiativeCoordinatorChange)
class InitiativeCoordinatorChangeAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for InitiativeCoordinatorChange model.
    
    Provides interface for viewing coordinator change history.
    """
    
    list_display = [
        'initiative_display',
        'previous_coordinator_display',
        'new_coordinator_display',
        'change_date',
        'changed_by'
    ]
    
    list_filter = [
        'change_date',
        'changed_by',
    ]
    
    search_fields = [
        'initiative__name',
        'previous_coordinator__name',
        'new_coordinator__name',
        'change_reason',
        'changed_by'
    ]
    
    readonly_fields = [
        'initiative',
        'previous_coordinator',
        'new_coordinator',
        'change_date',
        'change_reason',
        'changed_by'
    ]
    
    fieldsets = (
        ('Change Information', {
            'fields': ('initiative', 'change_date', 'changed_by')
        }),
        ('Coordinator Change', {
            'fields': ('previous_coordinator', 'new_coordinator', 'change_reason')
        })
    )
    
    list_per_page = 50
    ordering = ['-change_date']
    
    def initiative_display(self, obj):
        """Display initiative with link."""
        if obj.initiative:
            url = reverse('admin:initiatives_initiative_change', args=[obj.initiative.pk])
            return format_html(
                '<a href="{}" title="View initiative">{}</a>',
                url,
                obj.initiative.name
            )
        return format_html('<span style="color: #999;">Unknown</span>')
    initiative_display.short_description = 'Initiative'
    initiative_display.admin_order_field = 'initiative__name'
    
    def previous_coordinator_display(self, obj):
        """Display previous coordinator with link."""
        if obj.previous_coordinator:
            url = reverse('admin:people_person_change', args=[obj.previous_coordinator.pk])
            return format_html(
                '<a href="{}" title="View person">{}</a>',
                url,
                obj.previous_coordinator.full_name
            )
        return format_html('<span style="color: #999;">Unknown</span>')
    previous_coordinator_display.short_description = 'Previous Coordinator'
    previous_coordinator_display.admin_order_field = 'previous_coordinator__name'
    
    def new_coordinator_display(self, obj):
        """Display new coordinator with link."""
        if obj.new_coordinator:
            url = reverse('admin:people_person_change', args=[obj.new_coordinator.pk])
            return format_html(
                '<a href="{}" title="View person">{}</a>',
                url,
                obj.new_coordinator.full_name
            )
        return format_html('<span style="color: #999;">Unknown</span>')
    new_coordinator_display.short_description = 'New Coordinator'
    new_coordinator_display.admin_order_field = 'new_coordinator__name'
    
    def has_add_permission(self, request):
        """Disable manual addition of coordinator changes."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete coordinator change records."""
        return request.user.is_superuser
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related(
            'initiative',
            'previous_coordinator',
            'new_coordinator'
        )


# Register with custom admin site
admin_site.register(InitiativeCoordinatorChange, InitiativeCoordinatorChangeAdmin)
