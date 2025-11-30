#!/usr/bin/env python
"""
Test script to verify campus data migration logic.
This creates test data, runs the migration logic, and verifies results.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep.settings')
django.setup()

from apps.organizational_group.models import OrganizationalGroup, Campus
from apps.people.models import Person
from django.db import connection, models

def reset_data():
    """Clear existing test data."""
    print("Clearing existing data...")
    OrganizationalGroup.objects.all().delete()
    Campus.objects.all().delete()
    print("Data cleared.\n")

def create_test_data():
    """Create test organizational groups with various campus values."""
    print("Creating test data...")
    
    # Note: Person is not required for OrganizationalGroup creation
    # We can create groups without needing a person
    
    test_groups = [
        {'name': 'AI Research Lab', 'short_name': 'AI-LAB', 'campus': 'Main Campus', 'type': 'research', 'knowledge_area': 'Computer Science'},
        {'name': 'Robotics Lab', 'short_name': 'ROBO-LAB', 'campus': 'Main Campus', 'type': 'research', 'knowledge_area': 'Engineering'},
        {'name': 'Biology Research', 'short_name': 'BIO-RES', 'campus': 'North Campus', 'type': 'research', 'knowledge_area': 'Biology'},
        {'name': 'Extension Program', 'short_name': 'EXT-PROG', 'campus': 'South Campus', 'type': 'extension', 'knowledge_area': 'Community'},
        {'name': 'Duplicate Campus 1', 'short_name': 'DUP1', 'campus': 'East Campus', 'type': 'research', 'knowledge_area': 'Physics'},
        {'name': 'Duplicate Campus 2', 'short_name': 'DUP2', 'campus': 'East Campus', 'type': 'research', 'knowledge_area': 'Chemistry'},
        {'name': 'Special Chars Campus', 'short_name': 'SPEC', 'campus': 'West Campus - Building A', 'type': 'research', 'knowledge_area': 'Math'},
    ]
    
    # Temporarily bypass validation by directly calling parent save
    for group_data in test_groups:
        group = OrganizationalGroup(**group_data)
        # Call parent save to bypass full_clean
        models.Model.save(group)
        print(f"  Created: {group.name} (campus: '{group.campus}')")
    
    # Create one with empty campus using direct parent save
    empty_group = OrganizationalGroup(
        name='Empty Campus Group',
        short_name='EMPTY',
        campus='',
        type='research',
        knowledge_area='General'
    )
    models.Model.save(empty_group)
    print(f"  Created: {empty_group.name} (campus: '')")
    
    print(f"\nCreated {len(test_groups)} test groups\n")

def test_migration_logic():
    """Test the migration logic by simulating what the migration does."""
    print("Testing migration logic...")
    
    # Get unique campus values
    campus_values = OrganizationalGroup.objects.exclude(
        campus__isnull=True
    ).exclude(
        campus__exact=''
    ).values_list('campus', flat=True).distinct()
    
    print(f"Found {len(campus_values)} unique campus values:")
    for campus in campus_values:
        print(f"  - '{campus}'")
    
    # Import the generate_campus_code function from the migration
    import importlib
    migration_module = importlib.import_module('apps.organizational_group.migrations.0004_migrate_campus_data')
    generate_campus_code = migration_module.generate_campus_code
    
    print("\nGenerating campus codes:")
    campus_map = {}
    for campus_name in campus_values:
        if campus_name and campus_name.strip():
            code = generate_campus_code(campus_name, Campus)
            campus, created = Campus.objects.get_or_create(
                code=code,
                defaults={
                    'name': campus_name.strip(),
                    'location': ''
                }
            )
            campus_map[campus_name] = campus
            status = "Created" if created else "Existing"
            print(f"  {status}: {campus.name} -> {campus.code}")
    
    # Handle empty campus values
    groups_without_campus = OrganizationalGroup.objects.filter(
        campus__exact=''
    )
    
    if groups_without_campus.exists():
        print(f"\nFound {groups_without_campus.count()} groups without campus")
        default_code = generate_campus_code("Unknown Campus", Campus)
        default_campus, created = Campus.objects.get_or_create(
            code=default_code,
            defaults={
                'name': 'Unknown Campus',
                'location': 'Not specified'
            }
        )
        status = "Created" if created else "Existing"
        print(f"  {status} default campus: {default_campus.name} -> {default_campus.code}")
    
    # Map groups to campuses
    print("\nMapping groups to campuses:")
    for group in OrganizationalGroup.objects.all():
        if group.campus and group.campus.strip() and group.campus in campus_map:
            group.campus_id = campus_map[group.campus]
            models.Model.save(group, update_fields=['campus_id'])
            print(f"  {group.short_name} -> {campus_map[group.campus].code}")
        elif groups_without_campus.exists() and (not group.campus or not group.campus.strip()):
            group.campus_id = default_campus
            models.Model.save(group, update_fields=['campus_id'])
            print(f"  {group.short_name} -> {default_campus.code} (default)")

def verify_results():
    """Verify the migration results."""
    print("\n" + "="*60)
    print("VERIFICATION RESULTS")
    print("="*60)
    
    # Check Campus records
    campuses = Campus.objects.all().order_by('name')
    print(f"\nTotal Campus records: {campuses.count()}")
    for campus in campuses:
        group_count = campus.groups.count()
        print(f"  - {campus.name} ({campus.code}): {group_count} groups")
    
    # Check OrganizationalGroup mappings
    groups = OrganizationalGroup.objects.select_related('campus_id').all()
    print(f"\nTotal OrganizationalGroup records: {groups.count()}")
    
    mapped_count = groups.filter(campus_id__isnull=False).count()
    unmapped_count = groups.filter(campus_id__isnull=True).count()
    
    print(f"  - Mapped to campus: {mapped_count}")
    print(f"  - Not mapped: {unmapped_count}")
    
    if unmapped_count > 0:
        print("\n  WARNING: Some groups are not mapped to a campus!")
        unmapped = groups.filter(campus_id__isnull=True)
        for group in unmapped:
            print(f"    - {group.short_name} (campus: '{group.campus}')")
    
    # Verify data integrity
    print("\nData Integrity Checks:")
    
    # Check that all groups with non-empty campus are mapped
    groups_with_campus = groups.exclude(campus__exact='').exclude(campus__isnull=True)
    unmapped_with_campus = groups_with_campus.filter(campus_id__isnull=True)
    
    if unmapped_with_campus.exists():
        print(f"  ✗ FAIL: {unmapped_with_campus.count()} groups with campus value are not mapped")
    else:
        print(f"  ✓ PASS: All groups with campus values are mapped")
    
    # Check that campus codes are unique
    duplicate_codes = Campus.objects.values('code').annotate(
        count=django.db.models.Count('code')
    ).filter(count__gt=1)
    
    if duplicate_codes.exists():
        print(f"  ✗ FAIL: Found duplicate campus codes")
        for dup in duplicate_codes:
            print(f"    - Code '{dup['code']}' appears {dup['count']} times")
    else:
        print(f"  ✓ PASS: All campus codes are unique")
    
    # Check that groups with same campus name map to same Campus
    print("\n  Checking campus name consistency:")
    for campus_name in OrganizationalGroup.objects.values_list('campus', flat=True).distinct():
        if campus_name and campus_name.strip():
            campus_ids = OrganizationalGroup.objects.filter(
                campus=campus_name
            ).values_list('campus_id', flat=True).distinct()
            
            if len(campus_ids) > 1:
                print(f"    ✗ FAIL: Campus '{campus_name}' maps to multiple Campus records")
            else:
                print(f"    ✓ PASS: Campus '{campus_name}' maps to single Campus record")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    import django.db.models
    
    print("Campus Data Migration Test")
    print("="*60 + "\n")
    
    # Reset and create test data
    reset_data()
    create_test_data()
    
    # Test migration logic
    test_migration_logic()
    
    # Verify results
    verify_results()
    
    print("\nTest complete!")
