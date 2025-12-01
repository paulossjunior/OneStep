import os
import sys
import django
from datetime import date

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep.settings')
django.setup()

from apps.initiatives.models import Initiative, InitiativeType
from apps.people.models import Person

def create_sample_data():
    # Create Types
    try:
        program_type = InitiativeType.objects.get(code="program")
    except InitiativeType.DoesNotExist:
        program_type = InitiativeType.objects.create(name="Program", code="program")

    try:
        project_type = InitiativeType.objects.get(code="project")
    except InitiativeType.DoesNotExist:
        project_type = InitiativeType.objects.create(name="Project", code="project")
    
    # Create Person
    coordinator, _ = Person.objects.get_or_create(name="John Coordinator", email="john@example.com")
    
    # Create Initiatives
    initiatives = [
        {
            "name": "Digital Transformation Program",
            "type": program_type,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "description": "A program to transform digital capabilities.",
            "coordinator": coordinator
        },
        {
            "name": "Project Alpha",
            "type": project_type,
            "start_date": date(2024, 2, 1),
            "end_date": date(2024, 6, 30),
            "description": "First phase of the alpha project.",
            "coordinator": coordinator
        },
        {
            "name": "Project Beta",
            "type": project_type,
            "start_date": date(2024, 7, 1),
            "end_date": date(2024, 11, 30),
            "description": "Second phase of the beta project.",
            "coordinator": coordinator
        }
    ]
    
    for init_data in initiatives:
        init, created = Initiative.objects.get_or_create(
            name=init_data["name"],
            defaults=init_data
        )
        if created:
            print(f"Created initiative: {init.name}")
        else:
            print(f"Initiative already exists: {init.name}")

if __name__ == "__main__":
    create_sample_data()
