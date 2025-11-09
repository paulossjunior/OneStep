"""
Handler for Person creation and deduplication.
"""

from typing import List, Optional
from django.db import IntegrityError
from apps.people.models import Person, PersonEmail


class PersonHandler:
    """
    Handles Person creation and deduplication for CSV import.
    """
    
    def get_or_create_person(self, name: str, email: Optional[str] = None) -> Person:
        """
        Get or create a Person with deduplication.
        
        For coordinators (with email):
        - Deduplicate by email (case-insensitive) via PersonEmail
        
        For team members/students (may not have email):
        - If email provided, deduplicate by email via PersonEmail
        - If no email, deduplicate by name only
        
        Args:
            name: Person's name
            email: Person's email (optional)
            
        Returns:
            Person: Existing or newly created Person
        """
        # Normalize name
        normalized_name = self.normalize_name(name)
        
        if email and email.strip():
            # Deduplicate by email (case-insensitive)
            normalized_email = email.lower().strip()
            
            # Check if email already exists
            person_email = PersonEmail.objects.filter(email__iexact=normalized_email).first()
            
            if person_email:
                person = person_email.person
                # Update name if different (keep most recent)
                if person.name != normalized_name:
                    person.name = normalized_name
                    person.save()
                return person
            
            # Check if person exists by name
            person = Person.objects.filter(name__iexact=normalized_name).first()
            
            if person:
                # Person exists, add email if not already present
                try:
                    PersonEmail.objects.create(
                        person=person,
                        email=normalized_email,
                        is_primary=not person.emails.exists()  # First email is primary
                    )
                except IntegrityError:
                    # Email was just added by another process
                    pass
                return person
            
            # Create new person with email
            try:
                person = Person.objects.create(
                    name=normalized_name,
                    email=normalized_email  # Set primary email on person
                )
                # Also create PersonEmail record
                PersonEmail.objects.create(
                    person=person,
                    email=normalized_email,
                    is_primary=True
                )
                return person
            except IntegrityError:
                # Race condition - another process created it
                person_email = PersonEmail.objects.filter(email__iexact=normalized_email).first()
                if person_email:
                    return person_email.person
                # Fallback to name lookup
                return Person.objects.filter(name__iexact=normalized_name).first()
        else:
            # No email - deduplicate by name only
            person = Person.objects.filter(name__iexact=normalized_name).first()
            
            if person:
                return person
            
            # Create new person without email
            try:
                person = Person.objects.create(
                    name=normalized_name,
                    email=None
                )
                return person
            except IntegrityError:
                # Race condition - try to find by name again
                person = Person.objects.filter(name__iexact=normalized_name).first()
                if person:
                    return person
                raise Exception(f"Could not create person with name: {normalized_name}")
    
    def normalize_name(self, name: str) -> str:
        """
        Normalize name to Title Case.
        
        Args:
            name: Name to normalize
            
        Returns:
            str: Normalized name in Title Case
        """
        if not name:
            return ""
        
        # Strip whitespace and convert to title case
        return name.strip().title()
    
    def parse_people_list(self, people_str: str) -> List[str]:
        """
        Parse semicolon-separated list of people names.
        
        Args:
            people_str: Semicolon-separated string of names
            
        Returns:
            List of names (empty names filtered out)
        """
        if not people_str:
            return []
        
        # Split by semicolon and filter empty names
        names = [name.strip() for name in people_str.split(';')]
        return [name for name in names if name]
