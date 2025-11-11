# Generated data migration to populate default scholarship types

from django.db import migrations


def create_default_scholarship_types(apps, schema_editor):
    """
    Create default scholarship types.
    
    Creates the following types:
    - Research: For research-focused scholarships
    - Extension: For extension project scholarships
    - Teaching: For teaching-related scholarships
    - Innovation: For innovation and technology development scholarships
    - Monitoring: For monitoring and evaluation scholarships
    """
    ScholarshipType = apps.get_model('scholarships', 'ScholarshipType')
    
    default_types = [
        {
            'name': 'Research Scholarship',
            'code': 'research',
            'description': 'Scholarship for students engaged in research activities and scientific investigation.',
            'is_active': True,
        },
        {
            'name': 'Extension Scholarship',
            'code': 'extension',
            'description': 'Scholarship for students participating in extension projects that connect the university with the community.',
            'is_active': True,
        },
        {
            'name': 'Teaching Scholarship',
            'code': 'teaching',
            'description': 'Scholarship for students involved in teaching support activities and educational programs.',
            'is_active': True,
        },
        {
            'name': 'Innovation Scholarship',
            'code': 'innovation',
            'description': 'Scholarship for students working on innovation projects and technology development initiatives.',
            'is_active': True,
        },
        {
            'name': 'Monitoring Scholarship',
            'code': 'monitoring',
            'description': 'Scholarship for students engaged in monitoring, evaluation, and quality assurance activities.',
            'is_active': True,
        },
    ]
    
    for type_data in default_types:
        ScholarshipType.objects.get_or_create(
            code=type_data['code'],
            defaults={
                'name': type_data['name'],
                'description': type_data['description'],
                'is_active': type_data['is_active'],
            }
        )


def remove_default_scholarship_types(apps, schema_editor):
    """
    Remove default scholarship types (reverse migration).
    
    Only removes types that have no associated scholarships.
    """
    ScholarshipType = apps.get_model('scholarships', 'ScholarshipType')
    
    default_codes = ['research', 'extension', 'teaching', 'innovation', 'monitoring']
    
    for code in default_codes:
        # Only delete if no scholarships are associated
        ScholarshipType.objects.filter(
            code=code,
            scholarships__isnull=True
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('scholarships', '0002_scholarship_and_more'),
    ]

    operations = [
        migrations.RunPython(
            create_default_scholarship_types,
            reverse_code=remove_default_scholarship_types
        ),
    ]
