# Generated migration for campus data conversion

from django.db import migrations
import re


def generate_campus_code(name, Campus):
    """
    Generate a unique campus code from name.
    
    Args:
        name (str): Campus name to generate code from
        Campus: Campus model class
        
    Returns:
        str: Unique campus code (uppercase, max 20 chars)
    """
    if not name or not name.strip():
        return "UNKNOWN"
    
    # Clean the name
    clean_name = name.strip().upper()
    
    # Remove special characters and extra spaces
    clean_name = re.sub(r'[^A-Z0-9\s]', '', clean_name)
    clean_name = re.sub(r'\s+', ' ', clean_name)
    
    # Generate code from words
    words = clean_name.split()
    if len(words) == 0:
        code = "UNKNOWN"
    elif len(words) == 1:
        # Single word: take first 20 characters
        code = words[0][:20]
    else:
        # Multiple words: take first letter of each word
        code = ''.join(word[0] for word in words if word)[:20]
        
        # If code is too short (less than 3 chars), use first word instead
        if len(code) < 3:
            code = words[0][:20]
    
    # Ensure uniqueness by appending number if needed
    base_code = code
    counter = 1
    while Campus.objects.filter(code=code).exists():
        # Append counter, ensuring total length stays within 20 chars
        suffix = str(counter)
        max_base_length = 20 - len(suffix)
        code = f"{base_code[:max_base_length]}{suffix}"
        counter += 1
    
    return code


def migrate_campus_data_forward(apps, schema_editor):
    """
    Migrate existing campus CharField data to Campus model foreign keys.
    
    This migration:
    1. Extracts unique campus values from OrganizationalGroup records
    2. Creates Campus records for each unique campus value
    3. Maps OrganizationalGroup records to Campus foreign keys
    4. Handles edge cases (empty, null, duplicate names)
    """
    OrganizationalGroup = apps.get_model('organizational_group', 'OrganizationalGroup')
    Campus = apps.get_model('organizational_group', 'Campus')
    
    # Get all unique campus values (including empty/null)
    campus_values = OrganizationalGroup.objects.values_list('campus', flat=True).distinct()
    
    # Create a mapping from campus name to Campus object
    campus_map = {}
    
    # Track campus names we've seen to handle duplicates
    seen_names = {}
    
    for campus_name in campus_values:
        # Handle empty or null campus values
        if not campus_name or not campus_name.strip():
            # Create a default "Unknown Campus" if we haven't already
            if 'UNKNOWN' not in campus_map:
                code = generate_campus_code('Unknown Campus', Campus)
                campus, created = Campus.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': 'Unknown Campus',
                        'location': ''
                    }
                )
                campus_map['UNKNOWN'] = campus
                seen_names['unknown campus'] = campus
            continue
        
        # Clean the campus name
        clean_name = campus_name.strip()
        normalized_name = clean_name.lower()
        
        # Check if we've already created a Campus for this name (case-insensitive)
        if normalized_name in seen_names:
            campus_map[campus_name] = seen_names[normalized_name]
            continue
        
        # Generate unique code for this campus
        code = generate_campus_code(clean_name, Campus)
        
        # Create Campus record
        campus, created = Campus.objects.get_or_create(
            code=code,
            defaults={
                'name': clean_name,
                'location': ''
            }
        )
        
        # Store in both maps
        campus_map[campus_name] = campus
        seen_names[normalized_name] = campus
    
    # Update all OrganizationalGroup records to use campus_id
    for group in OrganizationalGroup.objects.all():
        if not group.campus or not group.campus.strip():
            # Map empty/null campus to Unknown Campus
            group.campus_id = campus_map.get('UNKNOWN')
        else:
            # Map to the corresponding Campus object
            group.campus_id = campus_map.get(group.campus)
        
        if group.campus_id:
            group.save(update_fields=['campus_id'])


def migrate_campus_data_reverse(apps, schema_editor):
    """
    Reverse migration: populate campus CharField from Campus foreign key.
    
    This allows rolling back the migration if needed.
    """
    OrganizationalGroup = apps.get_model('organizational_group', 'OrganizationalGroup')
    
    # Restore campus CharField from campus_id relationship
    for group in OrganizationalGroup.objects.select_related('campus_id').all():
        if group.campus_id:
            group.campus = group.campus_id.name
            group.save(update_fields=['campus'])


class Migration(migrations.Migration):
    dependencies = [
        ('organizational_group', '0003_add_campus_id_field'),
    ]

    operations = [
        migrations.RunPython(
            migrate_campus_data_forward,
            reverse_code=migrate_campus_data_reverse
        ),
    ]
