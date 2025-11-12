"""
Handlers for creating/retrieving related entities.
"""

from typing import Optional
from decimal import Decimal
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from apps.scholarships.models import ScholarshipType
from apps.people.models import Person
from apps.organizational_group.models import Campus, Organization
from apps.initiatives.models import Initiative


class ScholarshipTypeHandler:
    """Handles ScholarshipType creation and retrieval."""
    
    def get_or_create_type(self, name: str) -> Optional[ScholarshipType]:
        """
        Get or create a scholarship type by name.
        
        Args:
            name: Type name (e.g., "Pibic", "Pibic-Jr")
            
        Returns:
            ScholarshipType instance or None
        """
        if not name or not name.strip():
            return None
        
        # Normalize name
        normalized_name = name.strip().title()
        
        # Generate code from name
        code = normalized_name.lower().replace(' ', '_').replace('-', '_')
        
        # Try to find existing type (case-insensitive)
        scholarship_type = ScholarshipType.objects.filter(name__iexact=normalized_name).first()
        
        if scholarship_type:
            return scholarship_type
        
        # Create new type
        try:
            scholarship_type = ScholarshipType.objects.create(
                name=normalized_name,
                code=code,
                description=f'{normalized_name} scholarship type',
                is_active=True
            )
            return scholarship_type
        except IntegrityError:
            # Race condition
            return ScholarshipType.objects.filter(name__iexact=normalized_name).first()


class PersonHandler:
    """Handles Person creation and retrieval."""
    
    def get_or_create_person(self, name: str, email: str) -> Optional[Person]:
        """
        Get or create a person by email.
        
        Args:
            name: Person's full name
            email: Person's email address
            
        Returns:
            Person instance or None
        """
        if not email or not email.strip():
            return None
        
        email = email.strip().lower()
        
        # Try to find existing person by email
        person = Person.objects.filter(email__iexact=email).first()
        
        if person:
            return person
        
        # Normalize name
        full_name = name.strip().title()
        
        # Create new person
        try:
            person = Person.objects.create(
                name=full_name,
                email=email
            )
            return person
        except (IntegrityError, ValidationError):
            # Race condition or validation error
            return Person.objects.filter(email__iexact=email).first()


class CampusHandler:
    """Handles Campus creation and retrieval."""
    
    def get_or_create_campus(self, name: str) -> Optional[Campus]:
        """
        Get or create a campus by name.
        
        Args:
            name: Campus name
            
        Returns:
            Campus instance or None
        """
        if not name or not name.strip():
            return None
        
        # Normalize name
        normalized_name = name.strip().title()
        
        # Try to find existing campus (case-insensitive)
        campus = Campus.objects.filter(name__iexact=normalized_name).first()
        
        if campus:
            return campus
        
        # Generate code from name
        code = normalized_name[:3].upper()
        
        # Create new campus
        try:
            campus = Campus.objects.create(
                name=normalized_name,
                code=code,
                location=f'{normalized_name} campus'
            )
            return campus
        except IntegrityError:
            # Race condition or code conflict
            # Try with different code
            code = normalized_name[:4].upper()
            try:
                campus = Campus.objects.create(
                    name=normalized_name,
                    code=code,
                    location=f'{normalized_name} campus'
                )
                return campus
            except IntegrityError:
                return Campus.objects.filter(name__iexact=normalized_name).first()


class OrganizationHandler:
    """Handles Organization (Sponsor) creation and retrieval."""
    
    def get_or_create_organization(self, name: str) -> Optional[Organization]:
        """
        Get or create an organization by name.
        
        Args:
            name: Organization name
            
        Returns:
            Organization instance or None
        """
        if not name or not name.strip():
            return None
        
        # Normalize name
        normalized_name = name.strip().title()
        
        # Try to find existing organization (case-insensitive)
        organization = Organization.objects.filter(name__iexact=normalized_name).first()
        
        if organization:
            return organization
        
        # Create new organization
        try:
            organization = Organization.objects.create(
                name=normalized_name,
                description=f'{normalized_name} - Scholarship sponsor'
            )
            return organization
        except IntegrityError:
            # Race condition
            return Organization.objects.filter(name__iexact=normalized_name).first()


class InitiativeHandler:
    """Handles Initiative lookup."""
    
    def get_initiative_by_name(self, name: str) -> Optional[Initiative]:
        """
        Get an initiative by name.
        
        Args:
            name: Initiative name
            
        Returns:
            Initiative instance or None
        """
        if not name or not name.strip():
            return None
        
        # Normalize name
        normalized_name = name.strip()
        
        # Try to find existing initiative (case-insensitive)
        initiative = Initiative.objects.filter(name__iexact=normalized_name).first()
        
        return initiative
