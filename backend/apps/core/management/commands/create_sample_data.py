from django.core.management.base import BaseCommand
from django.db import transaction
from apps.people.models import Person
from apps.initiatives.models import Initiative, InitiativeType
from apps.organizational_group.models import OrganizationalGroup, OrganizationalGroupLeadership
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--people',
            type=int,
            default=10,
            help='Number of people to create (default: 10)'
        )
        parser.add_argument(
            '--initiatives',
            type=int,
            default=15,
            help='Number of initiatives to create (default: 15)'
        )
        parser.add_argument(
            '--groups',
            type=int,
            default=8,
            help='Number of groups to create (default: 8)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new sample data'
        )

    def handle(self, *args, **options):
        """
        Create sample data for the OneStep system.
        """
        people_count = options['people']
        initiatives_count = options['initiatives']
        groups_count = options['groups']
        clear_data = options['clear']

        self.stdout.write(
            self.style.SUCCESS(
                f'Creating sample data: {people_count} people, {initiatives_count} initiatives, {groups_count} groups'
            )
        )

        try:
            with transaction.atomic():
                if clear_data:
                    self.clear_existing_data()
                
                # Ensure initiative types exist
                self.create_initiative_types()
                
                # Create sample people
                people = self.create_sample_people(people_count)
                
                # Create sample initiatives
                initiatives = self.create_sample_initiatives(initiatives_count, people)
                
                # Add team members to initiatives
                self.assign_team_members(initiatives, people)
                
                # Create sample groups
                groups = self.create_sample_groups(groups_count, people, initiatives)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {len(people)} people, {len(initiatives)} initiatives, and {len(groups)} groups'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample data: {str(e)}')
            )
            raise

    def clear_existing_data(self):
        """Clear existing sample data."""
        self.stdout.write('Clearing existing data...')
        
        # Clear in order of dependencies
        OrganizationalGroup.objects.all().delete()
        Initiative.objects.all().delete()
        Person.objects.all().delete()
        
        self.stdout.write(self.style.WARNING('Existing data cleared'))

    def create_initiative_types(self):
        """Ensure initiative types exist."""
        InitiativeType.get_default_types()
        self.stdout.write('Initiative types ensured')

    def create_sample_people(self, count):
        """Create sample people."""
        self.stdout.write(f'Creating {count} people...')
        
        sample_names = [
            'Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson',
            'Emma Brown', 'Frank Miller', 'Grace Lee', 'Henry Taylor',
            'Ivy Chen', 'Jack Anderson', 'Kate Martinez', 'Liam Garcia',
            'Maya Patel', 'Noah Rodriguez', 'Olivia Thompson', 'Paul White',
            'Quinn Jackson', 'Rachel Kim', 'Sam Williams', 'Tara Jones'
        ]
        
        people = []
        for i in range(count):
            if i < len(sample_names):
                name = sample_names[i]
            else:
                name = f'Person {i + 1}'
            
            # Generate email from name
            email_name = name.lower().replace(' ', '.')
            email = f'{email_name}@onestep.example.com'
            
            person = Person.objects.create(
                name=name,
                email=email
            )
            people.append(person)
        
        self.stdout.write(f'Created {len(people)} people')
        return people

    def create_sample_initiatives(self, count, people):
        """Create sample initiatives."""
        self.stdout.write(f'Creating {count} initiatives...')
        
        # Get initiative types
        program_type = InitiativeType.objects.get(code='program')
        project_type = InitiativeType.objects.get(code='project')
        event_type = InitiativeType.objects.get(code='event')
        
        initiative_templates = [
            # Programs
            {
                'name': 'Digital Transformation Program',
                'description': 'Comprehensive digital transformation initiative to modernize our technology stack and processes.',
                'type': program_type,
                'duration_days': 365
            },
            {
                'name': 'Employee Development Program',
                'description': 'Multi-year program to enhance employee skills and career development opportunities.',
                'type': program_type,
                'duration_days': 730
            },
            {
                'name': 'Sustainability Initiative',
                'description': 'Organization-wide program to reduce environmental impact and promote sustainable practices.',
                'type': program_type,
                'duration_days': 545
            },
            
            # Projects
            {
                'name': 'Customer Portal Development',
                'description': 'Build a new customer-facing portal for self-service and account management.',
                'type': project_type,
                'duration_days': 120
            },
            {
                'name': 'Data Migration Project',
                'description': 'Migrate legacy data systems to new cloud-based infrastructure.',
                'type': project_type,
                'duration_days': 90
            },
            {
                'name': 'Mobile App Development',
                'description': 'Develop native mobile applications for iOS and Android platforms.',
                'type': project_type,
                'duration_days': 180
            },
            {
                'name': 'Security Audit Implementation',
                'description': 'Implement security recommendations from recent audit findings.',
                'type': project_type,
                'duration_days': 60
            },
            {
                'name': 'API Integration Project',
                'description': 'Integrate with third-party APIs to enhance system functionality.',
                'type': project_type,
                'duration_days': 75
            },
            
            # Events
            {
                'name': 'Annual Company Conference',
                'description': 'Three-day conference featuring keynotes, workshops, and networking sessions.',
                'type': event_type,
                'duration_days': 3
            },
            {
                'name': 'Quarterly All-Hands Meeting',
                'description': 'Company-wide meeting to share updates and strategic direction.',
                'type': event_type,
                'duration_days': 1
            },
            {
                'name': 'Product Launch Event',
                'description': 'Launch event for new product line with media and customer presentations.',
                'type': event_type,
                'duration_days': 2
            },
            {
                'name': 'Team Building Workshop',
                'description': 'Interactive workshop focused on team collaboration and communication.',
                'type': event_type,
                'duration_days': 1
            },
            {
                'name': 'Training Bootcamp',
                'description': 'Intensive training program for new technologies and methodologies.',
                'type': event_type,
                'duration_days': 5
            }
        ]
        
        initiatives = []
        today = date.today()
        
        for i in range(count):
            if i < len(initiative_templates):
                template = initiative_templates[i]
            else:
                # Generate additional initiatives
                template = {
                    'name': f'Initiative {i + 1}',
                    'description': f'Sample initiative number {i + 1} for testing and development.',
                    'type': random.choice([program_type, project_type, event_type]),
                    'duration_days': random.randint(30, 365)
                }
            
            # Random start date within the next 6 months
            start_offset = random.randint(0, 180)
            start_date = today + timedelta(days=start_offset)
            end_date = start_date + timedelta(days=template['duration_days'])
            
            # Random coordinator
            coordinator = random.choice(people)
            
            initiative = Initiative.objects.create(
                name=template['name'],
                description=template['description'],
                type=template['type'],
                start_date=start_date,
                end_date=end_date,
                coordinator=coordinator
            )
            initiatives.append(initiative)
        
        # Create some hierarchical relationships (parent-child)
        self.create_hierarchical_relationships(initiatives)
        
        self.stdout.write(f'Created {len(initiatives)} initiatives')
        return initiatives

    def create_hierarchical_relationships(self, initiatives):
        """Create parent-child relationships between initiatives."""
        programs = [i for i in initiatives if i.type.code == 'program']
        projects = [i for i in initiatives if i.type.code == 'project']
        
        # Assign some projects to programs
        for program in programs[:3]:  # Only first 3 programs
            # Assign 2-4 projects to each program
            num_projects = min(random.randint(2, 4), len(projects))
            assigned_projects = random.sample(projects, num_projects)
            
            for project in assigned_projects:
                if not project.parent:  # Only assign if not already assigned
                    project.parent = program
                    project.save()
                    projects.remove(project)  # Remove from available projects
        
        self.stdout.write('Created hierarchical relationships')

    def assign_team_members(self, initiatives, people):
        """Assign team members to initiatives."""
        self.stdout.write('Assigning team members...')
        
        for initiative in initiatives:
            # Assign 2-6 team members per initiative
            num_members = random.randint(2, min(6, len(people)))
            
            # Exclude coordinator from team members selection
            available_people = [p for p in people if p != initiative.coordinator]
            
            if len(available_people) >= num_members:
                team_members = random.sample(available_people, num_members)
                initiative.team_members.set(team_members)
        
        self.stdout.write('Team members assigned')

    def create_sample_groups(self, count, people, initiatives):
        """Create sample groups."""
        self.stdout.write(f'Creating {count} groups...')
        
        group_templates = [
            {
                'name': 'Artificial Intelligence Research Lab',
                'short_name': 'AI-LAB',
                'url': 'https://ai-lab.university.edu',
                'type': 'research',
                'knowledge_area': 'Computer Science',
                'campus': 'Main Campus'
            },
            {
                'name': 'Sustainable Agriculture Extension',
                'short_name': 'SAE',
                'url': 'https://sae.university.edu',
                'type': 'extension',
                'knowledge_area': 'Agricultural Sciences',
                'campus': 'North Campus'
            },
            {
                'name': 'Biomedical Engineering Research Group',
                'short_name': 'BERG',
                'url': 'https://berg.university.edu',
                'type': 'research',
                'knowledge_area': 'Biomedical Engineering',
                'campus': 'Medical Campus'
            },
            {
                'name': 'Community Health Outreach',
                'short_name': 'CHO',
                'url': '',
                'type': 'extension',
                'knowledge_area': 'Public Health',
                'campus': 'Main Campus'
            },
            {
                'name': 'Quantum Computing Lab',
                'short_name': 'QC-LAB',
                'url': 'https://quantum.university.edu',
                'type': 'research',
                'knowledge_area': 'Physics',
                'campus': 'Main Campus'
            },
            {
                'name': 'Environmental Science Research Center',
                'short_name': 'ESRC',
                'url': 'https://esrc.university.edu',
                'type': 'research',
                'knowledge_area': 'Environmental Science',
                'campus': 'North Campus'
            },
            {
                'name': 'Data Science and Analytics Lab',
                'short_name': 'DSAL',
                'url': 'https://dsal.university.edu',
                'type': 'research',
                'knowledge_area': 'Data Science',
                'campus': 'Main Campus'
            },
            {
                'name': 'Rural Development Extension',
                'short_name': 'RDE',
                'url': '',
                'type': 'extension',
                'knowledge_area': 'Rural Development',
                'campus': 'South Campus'
            }
        ]
        
        campuses = ['Main Campus', 'North Campus', 'South Campus', 'Medical Campus']
        knowledge_areas = [
            'Computer Science', 'Agricultural Sciences', 'Biomedical Engineering',
            'Public Health', 'Physics', 'Environmental Science', 'Data Science',
            'Rural Development', 'Chemistry', 'Biology'
        ]
        
        groups = []
        for i in range(count):
            if i < len(group_templates):
                template = group_templates[i]
            else:
                # Generate additional groups
                group_type = random.choice(['research', 'extension'])
                template = {
                    'name': f'{random.choice(knowledge_areas)} {group_type.title()} Group {i + 1}',
                    'short_name': f'GRP{i + 1}',
                    'url': f'https://group{i + 1}.university.edu' if random.random() > 0.3 else '',
                    'type': group_type,
                    'knowledge_area': random.choice(knowledge_areas),
                    'campus': random.choice(campuses)
                }
            
            group = OrganizationalGroup.objects.create(
                name=template['name'],
                short_name=template['short_name'],
                url=template['url'],
                type=template['type'],
                knowledge_area=template['knowledge_area'],
                campus=template['campus']
            )
            groups.append(group)
            
            # Add leaders (1-2 leaders per group)
            num_leaders = random.randint(1, 2)
            leaders = random.sample(people, num_leaders)
            
            for idx, leader in enumerate(leaders):
                # First leader started earlier
                if idx == 0:
                    start_date = date.today() - timedelta(days=random.randint(180, 730))
                else:
                    start_date = date.today() - timedelta(days=random.randint(30, 180))
                
                OrganizationalGroupLeadership.objects.create(
                    group=group,
                    person=leader,
                    start_date=start_date,
                    end_date=None,
                    is_active=True
                )
            
            # Add some historical leaders (30% chance)
            if random.random() < 0.3:
                available_people = [p for p in people if p not in leaders]
                if available_people:
                    past_leader = random.choice(available_people)
                    end_date = date.today() - timedelta(days=random.randint(30, 365))
                    start_date = end_date - timedelta(days=random.randint(180, 730))
                    
                    OrganizationalGroupLeadership.objects.create(
                        group=group,
                        person=past_leader,
                        start_date=start_date,
                        end_date=end_date,
                        is_active=False
                    )
            
            # Add members (2-5 members per group)
            num_members = random.randint(2, min(5, len(people)))
            # Exclude leaders from members
            available_people = [p for p in people if p not in leaders]
            
            if len(available_people) >= num_members:
                members = random.sample(available_people, num_members)
                group.members.set(members)
            
            # Associate with initiatives (1-3 initiatives per group, 50% chance)
            if initiatives and random.random() < 0.5:
                num_initiatives = random.randint(1, min(3, len(initiatives)))
                group_initiatives = random.sample(initiatives, num_initiatives)
                group.initiatives.set(group_initiatives)
        
        self.stdout.write(f'Created {len(groups)} groups with leaders, members, and initiative associations')
        return groups