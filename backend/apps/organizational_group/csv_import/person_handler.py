"""
Person handler for CSV import.
"""

import re
from typing import List, Tuple
from apps.people.models import Person
from django.core.exceptions import ValidationError


class PersonHandler:
    """
    Handles Person creation and retrieval with email-based deduplication.
    """
    
    def __init__(self):
        self.person_cache = {}
    
    def parse_leaders(self, leaders_str: str) -> List[Tuple[str, str]]:
        """
        Parse leader string into list of (name, email) tuples.
        
        Args:
            leaders_str: Comma-separated leader entries in format "Name (email)"
            
        Returns:
            List of (name, email) tuples
            
        Example:
            "John Doe (john@example.com), Jane Smith (jane@example.com)"
            -> [("John Doe", "john@example.com"), ("Jane Smith", "jane@example.com")]
        """
        if not leaders_str or not leaders_str.strip():
            return []
        
        leaders = []
        leader_pattern = r'(.+?)\s*\(([^)]+)\)'
        
        # Split by comma to handle multiple leaders
        leader_entries = leaders_str.split(',')
        
        for entry in leader_entries:
            entry = entry.strip()
            if not entry:
                continue
            
            match = re.match(leader_pattern, entry)
            if match:
                name, email = match.groups()
                leaders.append((name.strip(), email.strip()))
        
        return leaders
    
    def get_or_create_person(self, name: str, email: str) -> Person:
        """
        Get existing person or create new one.
        
        Args:
            name: Person's full name
            email: Person's email address
            
        Returns:
            Person instance
            
        Raises:
            ValidationError: If person data is invalid
        """
        name = name.strip()
        email = email.strip().lower()
        
        if not name:
            raise ValidationError('Person name cannot be empty')
        
        if not email:
            raise ValidationError('Person email cannot be empty')
        
        # Check cache first
        cache_key = email.lower()
        if cache_key in self.person_cache:
            return self.person_cache[cache_key]
        
        # Try to find existing person (case-insensitive email)
        person = Person.objects.filter(email__iexact=email).first()
        
        if person:
            # Update name if different (keep most recent)
            if person.name != name:
                person.name = name
                person.save()
            
            self.person_cache[cache_key] = person
            return person
        
        # Create new person
        person = Person.objects.create(
            name=name,
            email=email
        )
        
        self.person_cache[cache_key] = person
        return person
