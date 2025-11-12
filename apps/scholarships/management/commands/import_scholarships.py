"""
Django management command for importing scholarships from CSV files.
"""

import os
from django.core.management.base import BaseCommand, CommandError
from apps.scholarships.csv_import import ScholarshipImportProcessor


class Command(BaseCommand):
    """
    Management command to import scholarships from CSV file.
    
    Usage:
        python manage.py import_scholarships <csv_file_path>
    """
    
    help = 'Import scholarships from CSV file'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file containing scholarship data'
        )
    
    def handle(self, *args, **options):
        """Handle command execution."""
        csv_file = options['csv_file']
        
        # Validate file exists
        if not os.path.exists(csv_file):
            raise CommandError(f'File not found: {csv_file}')
        
        # Display start message
        self.stdout.write(
            self.style.SUCCESS(f'Starting import from: {csv_file}')
        )
        self.stdout.write('')
        
        # Process import
        processor = ScholarshipImportProcessor()
        reporter = processor.process_csv(csv_file)
        
        # Display summary
        self.stdout.write('')
        self.stdout.write(reporter.generate_summary())
        self.stdout.write('')
        
        # Display detailed results
        if reporter.skip_count > 0:
            self.stdout.write(
                self.style.WARNING(f'\nSkipped {reporter.skip_count} duplicate(s):')
            )
            for skip in reporter.get_skips()[:10]:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Row {skip['row']}: {skip['title']} - {skip['reason']}"
                    )
                )
            if len(reporter.get_skips()) > 10:
                self.stdout.write(
                    self.style.WARNING(f"  ... and {len(reporter.get_skips()) - 10} more")
                )
        
        if reporter.has_errors():
            self.stdout.write(
                self.style.ERROR(f'\n{reporter.error_count} error(s) occurred:')
            )
            for error in reporter.get_errors()[:10]:
                self.stdout.write(
                    self.style.ERROR(
                        f"  Row {error['row']}: {error['message']}"
                    )
                )
            if len(reporter.get_errors()) > 10:
                self.stdout.write(
                    self.style.ERROR(f"  ... and {len(reporter.get_errors()) - 10} more errors")
                )
        
        if reporter.success_count > 0:
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully imported {reporter.success_count} scholarship(s)'
                )
            )
        
        # Exit with appropriate code
        if reporter.error_count > 0 and reporter.success_count == 0:
            raise CommandError('Import failed with errors')
