"""
Django management command to check migration status and provide guidance.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    """
    Check if migration 0002 has been applied.
    
    Usage:
        python manage.py check_migration_status
    """
    
    help = 'Check if migration 0002_allow_same_shortname_different_campus has been applied'
    
    def handle(self, *args, **options):
        """
        Handle command execution.
        """
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        
        # Check if our migration is applied
        migration_key = ('organizational_group', '0002_allow_same_shortname_different_campus')
        
        applied_migrations = executor.loader.applied_migrations
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Migration Status Check ==='))
        self.stdout.write('')
        
        # Check organizational_group migrations
        org_group_migrations = [
            m for m in applied_migrations 
            if m[0] == 'organizational_group'
        ]
        
        self.stdout.write('Applied organizational_group migrations:')
        for app, name in sorted(org_group_migrations):
            self.stdout.write(f'  ✓ {name}')
        
        self.stdout.write('')
        
        if migration_key in applied_migrations:
            self.stdout.write(
                self.style.SUCCESS(
                    '✓ Migration 0002_allow_same_shortname_different_campus is APPLIED'
                )
            )
            self.stdout.write('')
            self.stdout.write('You can now import research groups with the same short_name on different campuses.')
            self.stdout.write('')
            self.stdout.write('To import from CSV:')
            self.stdout.write('  python manage.py import_research_groups example/research_group/research_groups.csv')
        else:
            self.stdout.write(
                self.style.ERROR(
                    '✗ Migration 0002_allow_same_shortname_different_campus is NOT APPLIED'
                )
            )
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('You need to apply the migration first:'))
            self.stdout.write('')
            self.stdout.write('  python manage.py migrate organizational_group')
            self.stdout.write('')
            self.stdout.write('After applying the migration, you can import research groups.')
        
        self.stdout.write('')
