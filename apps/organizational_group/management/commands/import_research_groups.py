"""
Django management command for importing research groups from CSV files.
"""

import os
from django.core.management.base import BaseCommand, CommandError
from apps.organizational_group.csv_import import ImportProcessor


class Command(BaseCommand):
    """
    Management command to import research groups from CSV file.
    
    Usage:
        python manage.py import_research_groups <csv_file_path>
    """
    
    help = 'Import research groups from CSV file'
    
    def add_arguments(self, parser):
        """
        Add command arguments.
        
        Args:
            parser: Argument parser
        """
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file containing research group data'
        )
    
    def handle(self, *args, **options):
        """
        Handle command execution.
        
        Args:
            args: Positional arguments
            options: Command options
        """
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
        processor = ImportProcessor()
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
            for skip in reporter.get_skips():
                self.stdout.write(
                    self.style.WARNING(
                        f"  Row {skip['row']}: {skip['group']} - {skip['reason']}"
                    )
                )
        
        if reporter.has_errors():
            self.stdout.write(
                self.style.ERROR(f'\n{reporter.error_count} error(s) occurred:')
            )
            for error in reporter.get_errors():
                self.stdout.write(
                    self.style.ERROR(
                        f"  Row {error['row']}: {error['message']}"
                    )
                )
        
        if reporter.success_count > 0:
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully imported {reporter.success_count} research group(s)'
                )
            )
        
        # Exit with appropriate code
        if reporter.error_count > 0 and reporter.success_count == 0:
            raise CommandError('Import failed with errors')
