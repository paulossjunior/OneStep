from django.core.management.base import BaseCommand
from apps.people.models import Person
from apps.initiatives.models import Initiative, InitiativeType


class Command(BaseCommand):
    help = 'Show current database status and data counts'

    def handle(self, *args, **options):
        """
        Display current database status.
        """
        self.stdout.write(
            self.style.SUCCESS('=== OneStep Database Status ===')
        )
        
        # Count entities
        people_count = Person.objects.count()
        initiatives_count = Initiative.objects.count()
        initiative_types_count = InitiativeType.objects.count()
        
        self.stdout.write(f'People: {people_count}')
        self.stdout.write(f'Initiatives: {initiatives_count}')
        self.stdout.write(f'Initiative Types: {initiative_types_count}')
        
        if people_count > 0:
            self.stdout.write('\n--- Recent People ---')
            for person in Person.objects.all()[:5]:
                self.stdout.write(f'  • {person.name} ({person.email})')
        
        if initiatives_count > 0:
            self.stdout.write('\n--- Recent Initiatives ---')
            for initiative in Initiative.objects.all()[:5]:
                coordinator_name = initiative.coordinator.name if initiative.coordinator else 'No coordinator'
                self.stdout.write(f'  • {initiative.name} - {initiative.type.name} (Coordinator: {coordinator_name})')
        
        # Show relationships
        if initiatives_count > 0:
            self.stdout.write('\n--- Initiative Relationships ---')
            programs = Initiative.objects.filter(type__code='program')
            for program in programs:
                children = program.children.all()
                if children:
                    self.stdout.write(f'  Program: {program.name}')
                    for child in children:
                        self.stdout.write(f'    └─ {child.name} ({child.type.name})')
        
        self.stdout.write(
            self.style.SUCCESS('\n=== End Status ===')
        )