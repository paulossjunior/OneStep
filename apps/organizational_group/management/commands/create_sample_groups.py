"""
Management command to create sample groups with leaders, members, and initiative associations.

Usage:
    python manage.py create_sample_groups
    python manage.py create_sample_groups --clear  # Clear existing groups first
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from apps.organizational_group.models import OrganizationalGroup, OrganizationalGroupLeadership
from apps.people.models import Person
from apps.initiatives.models import Initiative


class Command(BaseCommand):
    help = 'Create sample groups with leaders, members, and initiative associations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing groups before creating samples',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing groups...')
            OrganizationalGroup.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing groups cleared'))
        
        self.stdout.write('Creating sample groups...')
        
        with transaction.atomic():
            # Ensure we have people and initiatives to work with
            people = self._ensure_sample_people()
            initiatives = self._ensure_sample_initiatives(people)
            
            # Create sample groups
            groups = self._create_sample_groups(people, initiatives)
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully created {len(groups)} sample groups'
            ))
            
            # Display summary
            self._display_summary(groups)
    
    def _ensure_sample_people(self):
        """Ensure we have sample people to use as leaders and members."""
        people = []
        
        sample_people_data = [
            {'name': 'Dr. Maria Silva', 'email': 'maria.silva@university.edu'},
            {'name': 'Prof. João Santos', 'email': 'joao.santos@university.edu'},
            {'name': 'Dr. Ana Costa', 'email': 'ana.costa@university.edu'},
            {'name': 'Prof. Carlos Oliveira', 'email': 'carlos.oliveira@university.edu'},
            {'name': 'Dr. Patricia Lima', 'email': 'patricia.lima@university.edu'},
            {'name': 'Prof. Roberto Ferreira', 'email': 'roberto.ferreira@university.edu'},
            {'name': 'Dr. Juliana Alves', 'email': 'juliana.alves@university.edu'},
            {'name': 'Prof. Fernando Rocha', 'email': 'fernando.rocha@university.edu'},
        ]
        
        for person_data in sample_people_data:
            person, created = Person.objects.get_or_create(
                email=person_data['email'],
                defaults={'name': person_data['name']}
            )
            people.append(person)
            if created:
                self.stdout.write(f'  Created person: {person.name}')
        
        return people
    
    def _ensure_sample_initiatives(self, people):
        """Ensure we have sample initiatives to associate with groups."""
        from apps.initiatives.models import InitiativeType
        
        # Get or create initiative types
        program_type, project_type, event_type = InitiativeType.get_default_types()
        
        initiatives = []
        
        sample_initiatives_data = [
            {
                'name': 'Digital Transformation Program',
                'description': 'University-wide digital transformation initiative',
                'type': program_type,
                'start_date': date(2024, 1, 1),
                'end_date': date(2026, 12, 31),
            },
            {
                'name': 'Sustainability Research Project',
                'description': 'Research project on sustainable practices',
                'type': project_type,
                'start_date': date(2024, 6, 1),
                'end_date': date(2025, 5, 31),
            },
            {
                'name': 'Innovation Summit 2025',
                'description': 'Annual innovation and technology summit',
                'type': event_type,
                'start_date': date(2025, 3, 15),
                'end_date': date(2025, 3, 17),
            },
        ]
        
        for init_data in sample_initiatives_data:
            initiative, created = Initiative.objects.get_or_create(
                name=init_data['name'],
                defaults={
                    **init_data,
                    'coordinator': people[0]  # Use first person as coordinator
                }
            )
            initiatives.append(initiative)
            if created:
                self.stdout.write(f'  Created initiative: {initiative.name}')
        
        return initiatives
    
    def _create_sample_groups(self, people, initiatives):
        """Create sample groups with various configurations."""
        groups = []
        
        # Group 1: Research group with multiple leaders and history
        group1 = OrganizationalGroup.objects.create(
            name='Artificial Intelligence Research Lab',
            short_name='AI-Lab',
            url='https://ai-lab.university.edu',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Computer Science',
            campus='Main Campus'
        )
        
        # Add current leader
        OrganizationalGroupLeadership.objects.create(
            group=group1,
            person=people[0],
            start_date=date(2023, 1, 1),
            is_active=True
        )
        
        # Add historical leader
        OrganizationalGroupLeadership.objects.create(
            group=group1,
            person=people[1],
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
            is_active=False
        )
        
        # Add members
        group1.members.set([people[2], people[3], people[4]])
        
        # Associate with initiatives
        group1.initiatives.set([initiatives[0], initiatives[1]])
        
        groups.append(group1)
        self.stdout.write(f'  Created group: {group1.name}')
        
        # Group 2: Extension group with single leader
        group2 = OrganizationalGroup.objects.create(
            name='Community Outreach and Extension',
            short_name='COE',
            url='https://coe.university.edu',
            type=OrganizationalGroup.TYPE_EXTENSION,
            knowledge_area='Social Sciences',
            campus='North Campus'
        )
        
        OrganizationalGroupLeadership.objects.create(
            group=group2,
            person=people[2],
            start_date=date(2024, 1, 1),
            is_active=True
        )
        
        group2.members.set([people[5], people[6]])
        group2.initiatives.set([initiatives[0]])
        
        groups.append(group2)
        self.stdout.write(f'  Created group: {group2.name}')
        
        # Group 3: Research group with co-leaders
        group3 = OrganizationalGroup.objects.create(
            name='Sustainable Energy Research Center',
            short_name='SERC',
            url='https://serc.university.edu',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Engineering',
            campus='Main Campus'
        )
        
        # Add two current leaders (co-leaders)
        OrganizationalGroupLeadership.objects.create(
            group=group3,
            person=people[3],
            start_date=date(2023, 6, 1),
            is_active=True
        )
        
        OrganizationalGroupLeadership.objects.create(
            group=group3,
            person=people[4],
            start_date=date(2023, 6, 1),
            is_active=True
        )
        
        group3.members.set([people[0], people[1], people[7]])
        group3.initiatives.set([initiatives[1]])
        
        groups.append(group3)
        self.stdout.write(f'  Created group: {group3.name}')
        
        # Group 4: Extension group without URL
        group4 = OrganizationalGroup.objects.create(
            name='Health and Wellness Extension Program',
            short_name='HWEP',
            url='',
            type=OrganizationalGroup.TYPE_EXTENSION,
            knowledge_area='Health Sciences',
            campus='South Campus'
        )
        
        OrganizationalGroupLeadership.objects.create(
            group=group4,
            person=people[5],
            start_date=date(2024, 3, 1),
            is_active=True
        )
        
        group4.members.set([people[2], people[6]])
        
        groups.append(group4)
        self.stdout.write(f'  Created group: {group4.name}')
        
        # Group 5: Research group with leadership transition
        group5 = OrganizationalGroup.objects.create(
            name='Data Science and Analytics Lab',
            short_name='DSAL',
            url='https://dsal.university.edu',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Statistics',
            campus='Main Campus'
        )
        
        # Historical leader
        OrganizationalGroupLeadership.objects.create(
            group=group5,
            person=people[6],
            start_date=date(2021, 1, 1),
            end_date=date(2023, 12, 31),
            is_active=False
        )
        
        # Current leader (took over recently)
        OrganizationalGroupLeadership.objects.create(
            group=group5,
            person=people[7],
            start_date=date(2024, 1, 1),
            is_active=True
        )
        
        group5.members.set([people[0], people[3], people[5]])
        group5.initiatives.set([initiatives[0], initiatives[2]])
        
        groups.append(group5)
        self.stdout.write(f'  Created group: {group5.name}')
        
        # Group 6: Extension group on different campus
        group6 = OrganizationalGroup.objects.create(
            name='Agricultural Extension Services',
            short_name='AES',
            url='',
            type=OrganizationalGroup.TYPE_EXTENSION,
            knowledge_area='Agriculture',
            campus='Rural Campus'
        )
        
        OrganizationalGroupLeadership.objects.create(
            group=group6,
            person=people[1],
            start_date=date(2023, 9, 1),
            is_active=True
        )
        
        group6.members.set([people[4], people[7]])
        
        groups.append(group6)
        self.stdout.write(f'  Created group: {group6.name}')
        
        return groups
    
    def _display_summary(self, groups):
        """Display a summary of created groups."""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('SAMPLE GROUPS SUMMARY'))
        self.stdout.write('=' * 60)
        
        for group in groups:
            self.stdout.write(f'\n{group.name} ({group.short_name})')
            self.stdout.write(f'  Type: {group.get_type_display()}')
            self.stdout.write(f'  Campus: {group.campus}')
            self.stdout.write(f'  Knowledge Area: {group.knowledge_area}')
            self.stdout.write(f'  Current Leaders: {group.leader_count()}')
            self.stdout.write(f'  Members: {group.member_count()}')
            self.stdout.write(f'  Initiatives: {group.initiative_count()}')
            
            # Show current leaders
            current_leaders = group.get_current_leaders()
            if current_leaders.exists():
                self.stdout.write('  Leaders:')
                for leader in current_leaders:
                    self.stdout.write(f'    - {leader.name}')
        
        self.stdout.write('\n' + '=' * 60)
