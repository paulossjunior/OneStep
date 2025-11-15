"""
Django Admin configuration for Scholarship models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db import models
from .models import ScholarshipType, Scholarship
from .csv_import import ScholarshipImportProcessor


@admin.register(ScholarshipType)
class ScholarshipTypeAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for ScholarshipType model.
    """
    
    list_display = [
        'name',
        'code',
        'is_active',
        'scholarship_count_display',
        'created_at'
    ]
    
    list_display_links = ['name']
    
    list_filter = [
        'is_active',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'name',
        'code',
        'description'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'scholarship_count_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Statistics', {
            'fields': ('scholarship_count_display',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 25
    ordering = ['name']
    
    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            annotated_scholarship_count=models.Count('scholarships', distinct=True)
        )
        return queryset
    
    def scholarship_count_display(self, obj):
        """Display count of scholarships for this type."""
        count = getattr(obj, 'annotated_scholarship_count', obj.scholarship_count())
        
        if count > 0:
            return format_html(
                '<strong>{}</strong> scholarship{}',
                count,
                's' if count != 1 else ''
            )
        return format_html('<span style="color: #999;">No scholarships</span>')
    scholarship_count_display.short_description = 'Scholarships'
    scholarship_count_display.admin_order_field = 'annotated_scholarship_count'


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for Scholarship model.
    """
    
    # Change list template to add custom button
    change_list_template = 'admin/scholarships/scholarship/change_list.html'
    
    list_display = [
        'title',
        'type_display',
        'student_display',
        'supervisor_display',
        'campus_display',
        'value_display',
        'start_date',
        'end_date',
        'is_active_display',
        'duration_display'
    ]
    
    list_display_links = ['title']
    
    list_filter = [
        'type',
        'campus',
        'start_date',
        'end_date',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'student__first_name',
        'student__last_name',
        'student__email',
        'supervisor__first_name',
        'supervisor__last_name',
        'supervisor__email',
        'sponsor__name'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'duration_display',
        'is_active_display',
        'total_value_display'
    ]
    
    autocomplete_fields = [
        'type',
        'campus',
        'supervisor',
        'student',
        'sponsor',
        'initiative'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'type', 'campus')
        }),
        ('People', {
            'fields': ('supervisor', 'student')
        }),
        ('Financial', {
            'fields': ('value', 'total_value_display', 'sponsor')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'duration_display', 'is_active_display')
        }),
        ('Association', {
            'fields': ('initiative',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 25
    ordering = ['-start_date']
    date_hierarchy = 'start_date'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'type',
            'campus',
            'supervisor',
            'student',
            'sponsor',
            'initiative'
        )
        return queryset
    
    def type_display(self, obj):
        """Display scholarship type with color."""
        if obj.type:
            return format_html(
                '<span style="color: #2196F3; font-weight: bold;">{}</span>',
                obj.type.name
            )
        return '-'
    type_display.short_description = 'Type'
    type_display.admin_order_field = 'type__name'
    
    def student_display(self, obj):
        """Display student name with link."""
        if obj.student:
            url = reverse('admin:people_person_change', args=[obj.student.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.student.name
            )
        return '-'
    student_display.short_description = 'Student'
    student_display.admin_order_field = 'student__first_name'
    
    def supervisor_display(self, obj):
        """Display supervisor name with link."""
        if obj.supervisor:
            url = reverse('admin:people_person_change', args=[obj.supervisor.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.supervisor.name
            )
        return '-'
    supervisor_display.short_description = 'Supervisor'
    supervisor_display.admin_order_field = 'supervisor__first_name'
    
    def campus_display(self, obj):
        """Display campus name."""
        if obj.campus:
            return format_html(
                '{} <span style="color: #999;">({})</span>',
                obj.campus.name,
                obj.campus.code
            )
        return '-'
    campus_display.short_description = 'Campus'
    campus_display.admin_order_field = 'campus__name'
    
    def value_display(self, obj):
        """Display monthly value formatted."""
        if obj.value:
            formatted_value = f'{obj.value:,.2f}'
            return format_html(
                '<strong>R$ {}</strong>/month',
                formatted_value
            )
        return '-'
    value_display.short_description = 'Monthly Value'
    value_display.admin_order_field = 'value'
    
    def is_active_display(self, obj):
        """Display active status with color."""
        is_active = obj.is_active()
        if is_active:
            return format_html(
                '<span style="color: #4CAF50; font-weight: bold;">● Active</span>'
            )
        return format_html(
            '<span style="color: #999;">○ Inactive</span>'
        )
    is_active_display.short_description = 'Status'
    
    def duration_display(self, obj):
        """Display duration in months."""
        months = obj.duration_months()
        if months:
            return format_html(
                '<strong>{}</strong> month{}',
                months,
                's' if months != 1 else ''
            )
        return format_html('<span style="color: #999;">Ongoing</span>')
    duration_display.short_description = 'Duration'
    
    def total_value_display(self, obj):
        """Display total scholarship value."""
        total = obj.total_value()
        if total:
            formatted_total = f'{total:,.2f}'
            return format_html(
                '<strong>R$ {}</strong>',
                formatted_total
            )
        return '-'
    total_value_display.short_description = 'Total Value'
    
    def save_model(self, request, obj, form, change):
        """Custom save with validation."""
        obj.full_clean()
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        """Add custom URL for CSV import."""
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='scholarships_import_csv'),
        ]
        return custom_urls + urls
    
    def import_csv_view(self, request):
        """Custom view for CSV import - supports single CSV or bulk ZIP import."""
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, 'Please select a file to upload.')
                return HttpResponseRedirect(request.path)
            
            # Check if bulk import (ZIP file)
            is_bulk = csv_file.name.lower().endswith('.zip')
            
            if is_bulk:
                # Process bulk import
                try:
                    from apps.core.csv_import.bulk_handler import BulkImportHandler, BulkImportReporter
                    
                    bulk_handler = BulkImportHandler()
                    csv_files = bulk_handler.process_upload(csv_file)
                    
                    if bulk_handler.has_errors():
                        for error in bulk_handler.get_errors():
                            messages.error(request, error)
                        return HttpResponseRedirect(request.path)
                    
                    if not csv_files:
                        messages.error(request, 'No CSV files found in the uploaded ZIP.')
                        return HttpResponseRedirect(request.path)
                    
                    # Process each CSV file
                    bulk_reporter = BulkImportReporter()
                    processor = ScholarshipImportProcessor()
                    
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
                            f"Successfully imported {summary['total_successes']} scholarship(s)"
                        )
                    
                    if summary['total_skips'] > 0:
                        messages.warning(
                            request,
                            f"Skipped {summary['total_skips']} duplicate scholarship(s)"
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
                    
                    return HttpResponseRedirect('../')
                    
                except Exception as e:
                    messages.error(request, f'Error processing ZIP file: {str(e)}')
                    return HttpResponseRedirect(request.path)
            
            else:
                # Single CSV import
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'File must be a CSV file (.csv) or ZIP archive (.zip).')
                    return HttpResponseRedirect(request.path)
                
                # Process the CSV file
                try:
                    processor = ScholarshipImportProcessor()
                    reporter = processor.process_csv(csv_file)
                    
                    # Display success message
                    if reporter.success_count > 0:
                        messages.success(
                            request,
                            f'Successfully imported {reporter.success_count} scholarship(s).'
                        )
                    
                    # Display skip message
                    if reporter.skip_count > 0:
                        messages.warning(
                            request,
                            f'Skipped {reporter.skip_count} duplicate scholarship(s).'
                        )
                    
                    # Display errors
                    if reporter.has_errors():
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
            'title': 'Import Scholarships from CSV',
            'site_title': self.admin_site.site_title,
            'site_header': self.admin_site.site_header,
            'has_permission': True,
        }
        
        return render(
            request,
            'admin/scholarships/import_csv.html',
            context
        )
