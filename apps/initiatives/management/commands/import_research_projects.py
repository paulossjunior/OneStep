"""
Django management command to import research projects from CSV.
"""

import sys
from django.core.management.base import BaseCommand, CommandError
from apps.initiatives.csv_import.processor import ResearchProjectImportProcessor


class Command(BaseCommand):
    """
    Management command to import research projects from CSV file.
    
    Usage:
        python manage.py import_research_projects <csv_file>
    """
    
    help = 'Import research projects from CSV file'
    
    def add_arguments(self, parser):
        """
        Add command arguments.
        
        Args:
            parser: Argument parser
        """
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file containing research projects'
        )
    
    def handle(self, *args, **options):
        """
        Execute the command.
        
        Args:
            args: Positional arguments
            options: Command options
        """
        csv_file = options['csv_file']
        
        # Check if file exists
        try:
            with open(csv_file, 'r') as f:
                pass
        except FileNotFoundError:
            raise CommandError(f'CSV file not found: {csv_file}')
        except Exception as e:
            raise CommandError(f'Error opening CSV file: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(f'Starting import from: {csv_file}'))
        self.stdout.write('')
        
        # Process CSV
        processor = ResearchProjectImportProcessor()
        reporter = processor.process_csv(csv_file)
        
        # Display summary
        self.stdout.write('')
        self.stdout.write(reporter.generate_summary())
        self.stdout.write('')
        
        # Display detailed errors if any
        if reporter.has_errors():
            self.stdout.write(self.style.ERROR('Errors encountered:'))
            for error in reporter.get_errors():
                self.stdout.write(
                    self.style.ERROR(f"  Row {error['row']}: {error['message']}")
                )
            self.stdout.write('')
        
        # Display skipped rows
        if reporter.skip_count > 0:
            self.stdout.write(self.style.WARNING('Skipped rows (duplicates):'))
            for skip in reporter.get_skips():
                self.stdout.write(
                    self.style.WARNING(f"  Row {skip['row']}: {skip['project']} - {skip['reason']}")
                )
            self.stdout.write('')
        
        # Display success message
        if reporter.success_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {reporter.success_count} research projects!')
            )
        
        # Return exit code
        if reporter.has_errors():
            sys.exit(1)
        else:
            sys.exit(0)
