"""
Management command to set up Django Admin user groups and permissions.

This command creates the necessary user groups and assigns appropriate
permissions for different roles in the OneStep system.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.people.models import Person
from apps.initiatives.models import Initiative


class Command(BaseCommand):
    help = 'Set up Django Admin user groups and permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing groups and permissions',
        )

    def handle(self, *args, **options):
        """
        Create user groups and assign permissions.
        """
        if options['reset']:
            self.stdout.write('Resetting existing groups...')
            Group.objects.filter(
                name__in=['Initiative Coordinators', 'HR Managers', 'Viewers']
            ).delete()

        # Create user groups
        coordinator_group, created = Group.objects.get_or_create(
            name='Initiative Coordinators'
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created "Initiative Coordinators" group')
            )

        hr_group, created = Group.objects.get_or_create(name='HR Managers')
        if created:
            self.stdout.write(self.style.SUCCESS('Created "HR Managers" group'))

        viewer_group, created = Group.objects.get_or_create(name='Viewers')
        if created:
            self.stdout.write(self.style.SUCCESS('Created "Viewers" group'))

        # Get content types
        person_ct = ContentType.objects.get_for_model(Person)
        initiative_ct = ContentType.objects.get_for_model(Initiative)

        # Set up Initiative Coordinators permissions
        coordinator_permissions = [
            # Initiative permissions
            Permission.objects.get(codename='add_initiative', content_type=initiative_ct),
            Permission.objects.get(codename='change_initiative', content_type=initiative_ct),
            Permission.objects.get(codename='view_initiative', content_type=initiative_ct),
            # Person view permissions (to assign coordinators and team members)
            Permission.objects.get(codename='view_person', content_type=person_ct),
        ]
        coordinator_group.permissions.set(coordinator_permissions)
        self.stdout.write('Set permissions for Initiative Coordinators')

        # Set up HR Managers permissions (full Person management)
        hr_permissions = [
            # Person permissions
            Permission.objects.get(codename='add_person', content_type=person_ct),
            Permission.objects.get(codename='change_person', content_type=person_ct),
            Permission.objects.get(codename='delete_person', content_type=person_ct),
            Permission.objects.get(codename='view_person', content_type=person_ct),
            # Initiative view permissions
            Permission.objects.get(codename='view_initiative', content_type=initiative_ct),
        ]
        hr_group.permissions.set(hr_permissions)
        self.stdout.write('Set permissions for HR Managers')

        # Set up Viewers permissions (read-only access)
        viewer_permissions = [
            Permission.objects.get(codename='view_person', content_type=person_ct),
            Permission.objects.get(codename='view_initiative', content_type=initiative_ct),
        ]
        viewer_group.permissions.set(viewer_permissions)
        self.stdout.write('Set permissions for Viewers')

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully set up admin permissions and user groups'
            )
        )
        
        # Display summary
        self.stdout.write('\nPermission Summary:')
        self.stdout.write('- Initiative Coordinators: Can manage initiatives, view people')
        self.stdout.write('- HR Managers: Can manage people, view initiatives')
        self.stdout.write('- Viewers: Can view all data (read-only)')
        self.stdout.write('\nTo assign users to groups, use the Django Admin interface.')