#!/usr/bin/env python
"""
Test script to verify campus migration handles edge cases correctly.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep.settings')
django.setup()

from apps.organizational_group.models import Campus, OrganizationalGroup
from importlib import import_module

# Import the migration module dynamically
migration_module = import_module('apps.organizational_group.migrations.0004_migrate_campus_data')
generate_campus_code = migration_module.generate_campus_code


def test_generate_campus_code():
    """Test the generate_campus_code function with various inputs."""
    print("Testing generate_campus_code function:")
    print("=" * 60)
    
    test_cases = [
        ("Main Campus", "Expected: MAIN or MC"),
        ("North Campus", "Expected: NORTH or NC"),
        ("University of Technology", "Expected: UOT or similar"),
        ("ABC", "Expected: ABC"),
        ("A", "Expected: A"),
        ("Campus 123", "Expected: C1 or similar"),
        ("Main-Campus", "Expected: MAINCAMPUS or MC"),
        ("   Spaces   ", "Expected: SPACES or S"),
        ("", "Expected: UNKNOWN"),
        ("   ", "Expected: UNKNOWN"),
    ]
    
    for name, expected in test_cases:
        code = generate_campus_code(name, Campus)
        print(f"  Input: '{name}'")
        print(f"    Generated: {code}")
        print(f"    {expected}")
        print()


def test_migration_results():
    """Test the actual migration results in the database."""
    print("\nTesting migration results:")
    print("=" * 60)
    
    # Check all campuses were created
    campuses = Campus.objects.all().order_by('name')
    print(f"Total campuses created: {campuses.count()}")
    print("\nCampus details:")
    for campus in campuses:
        print(f"  - {campus.name} ({campus.code})")
        print(f"    Location: {campus.location or '(empty)'}")
        print(f"    Groups: {campus.group_count()}")
    
    # Check all groups have campus_id
    total_groups = OrganizationalGroup.objects.count()
    groups_with_campus = OrganizationalGroup.objects.filter(campus_id__isnull=False).count()
    groups_without_campus = OrganizationalGroup.objects.filter(campus_id__isnull=True).count()
    
    print(f"\nGroup statistics:")
    print(f"  Total groups: {total_groups}")
    print(f"  Groups with campus_id: {groups_with_campus}")
    print(f"  Groups without campus_id: {groups_without_campus}")
    
    if groups_without_campus > 0:
        print("\n  WARNING: Some groups don't have campus_id!")
        for group in OrganizationalGroup.objects.filter(campus_id__isnull=True):
            print(f"    - {group.name} (campus: '{group.campus}')")
    
    # Check for duplicate campus names (case-insensitive)
    print("\nChecking for duplicate campus names:")
    campus_names = {}
    for campus in Campus.objects.all():
        normalized = campus.name.lower()
        if normalized in campus_names:
            print(f"  WARNING: Duplicate campus name found!")
            print(f"    - {campus_names[normalized].name} ({campus_names[normalized].code})")
            print(f"    - {campus.name} ({campus.code})")
        else:
            campus_names[normalized] = campus
    
    if len(campus_names) == Campus.objects.count():
        print("  ✓ No duplicate campus names found (case-insensitive)")
    
    # Check all codes are unique and uppercase
    print("\nChecking campus codes:")
    codes = Campus.objects.values_list('code', flat=True)
    if len(codes) == len(set(codes)):
        print("  ✓ All campus codes are unique")
    else:
        print("  WARNING: Duplicate campus codes found!")
    
    all_uppercase = all(code.isupper() for code in codes)
    if all_uppercase:
        print("  ✓ All campus codes are uppercase")
    else:
        print("  WARNING: Some campus codes are not uppercase!")
        for code in codes:
            if not code.isupper():
                print(f"    - {code}")
    
    # Verify mapping integrity
    print("\nVerifying campus mapping integrity:")
    for group in OrganizationalGroup.objects.all():
        if group.campus_id:
            original_campus = group.campus
            mapped_campus = group.campus_id.name
            # Check if they match (case-insensitive)
            if original_campus.lower() != mapped_campus.lower():
                print(f"  Note: {group.name}")
                print(f"    Original: '{original_campus}'")
                print(f"    Mapped to: '{mapped_campus}'")
    
    print("\n✓ Migration verification complete!")


if __name__ == '__main__':
    test_generate_campus_code()
    test_migration_results()
