"""
OrganizationalGroup handler for CSV import.
"""

from typing import Tuple, List
from datetime import date
from apps.organizational_group.models import (
    OrganizationalUnit as OrganizationalGroup,
    OrganizationalUnitLeadership as OrganizationalGroupLeadership,
    Campus,
    KnowledgeArea,
    Organization,
    OrganizationalType
)
from apps.people.models import Person
from django.core.exceptions import ValidationError


class GroupHandler:
    """
    Handles OrganizationalGroup creation with deduplication and leadership assignment.
    """
    
    def get_or_create_research_type(self) -> OrganizationalType:
        """
        Get or create Research organizational type.
        
        Returns:
            OrganizationalType: Research type instance
        """
        org_type, _ = OrganizationalType.objects.get_or_create(
            code='research',
            defaults={
                'name': 'Research',
                'description': 'Research groups'
            }
        )
        return org_type
    
    def get_or_create_default_organization(self) -> Organization:
        """
        Get or create default organization for imports.
        
        Returns:
            Organization: Default organization instance
        """
        org, _ = Organization.objects.get_or_create(
            name='Default Organization',
            defaults={
                'description': 'Default organization for imported groups'
            }
        )
        return org
    
    def create_or_skip_group(
        self,
        short_name: str,
        name: str,
        campus: Campus,
        knowledge_area: KnowledgeArea,
        repository_url: str = "",
        site_url: str = ""
    ) -> Tuple[OrganizationalGroup, bool]:
        """
        Create group or skip if duplicate exists.
        
        Args:
            short_name: Group abbreviation (Sigla)
            name: Full group name
            campus: Campus instance
            knowledge_area: KnowledgeArea instance
            repository_url: Optional repository URL
            site_url: Optional website URL (not used, for compatibility)
            
        Returns:
            Tuple of (group_instance, created_flag)
            
        Raises:
            ValidationError: If group data is invalid
        """
        name = name.strip()
        
        if not name:
            raise ValidationError('Group name cannot be empty')
        
        # Generate short_name from name if empty
        if not short_name or not short_name.strip():
            short_name = self._generate_short_name(name, campus)
        else:
            short_name = short_name.strip()
        
        # Get or create required foreign key instances
        research_type = self.get_or_create_research_type()
        organization = self.get_or_create_default_organization()
        
        # Check for duplicate (short_name + campus + organization combination)
        # Allow same short_name on different campuses
        existing_group = OrganizationalGroup.objects.filter(
            short_name__iexact=short_name,
            campus=campus,
            organization=organization
        ).first()
        
        if existing_group:
            return existing_group, False
        
        # Create new group
        # Note: We bypass full_clean validation due to database schema conflicts
        # The old 'type' VARCHAR column conflicts with the new 'type_id' foreign key
        group = OrganizationalGroup(
            name=name,
            short_name=short_name,
            url=repository_url.strip() if repository_url else "",
            type=research_type,
            organization=organization,
            knowledge_area=knowledge_area,
            campus=campus
        )
        # Save without calling full_clean() to avoid validation errors from schema conflicts
        super(OrganizationalGroup, group).save()
        
        return group, True
    
    def _generate_short_name(self, name: str, campus: Campus = None) -> str:
        """
        Generate short_name from full name by creating an acronym.
        
        Creates an acronym from the first letters of each significant word,
        optionally combined with campus code for uniqueness.
        
        Args:
            name: Full group name
            campus: Optional Campus instance to append code
            
        Returns:
            str: Generated short name (e.g., "ADSM" or "ADSM-VIT")
        """
        if not name or not name.strip():
            return "non-informed"
        
        # Words to ignore when creating acronym (common articles, prepositions, conjunctions)
        ignore_words = {
            'a', 'o', 'as', 'os', 'de', 'da', 'do', 'das', 'dos', 'em', 'no', 'na', 'nos', 'nas',
            'e', 'ou', 'para', 'com', 'por', 'sobre', 'entre', 'sem', 'sob', 'ao', 'aos',
            'the', 'of', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from'
        }
        
        # Split name into words and filter
        words = name.strip().split()
        significant_words = [
            word for word in words 
            if word.lower() not in ignore_words and len(word) > 0
        ]
        
        # If no significant words, use all words
        if not significant_words:
            significant_words = words
        
        # Create acronym from first letter of each significant word
        acronym = ''.join(word[0].upper() for word in significant_words if word)
        
        # Limit acronym length to reasonable size (max 10 characters)
        if len(acronym) > 10:
            acronym = acronym[:10]
        
        # If acronym is too short (less than 2 chars), use first 2-4 chars of first word
        if len(acronym) < 2 and significant_words:
            first_word = significant_words[0].upper()
            acronym = first_word[:min(4, len(first_word))]
        
        # Append campus code if provided for uniqueness
        if campus and campus.code:
            campus_code = campus.code.strip().upper()[:3]  # Max 3 chars from campus code
            acronym = f"{acronym}-{campus_code}"
        
        return acronym
    
    def assign_leaders(
        self,
        group: OrganizationalGroup,
        leaders: List[Person]
    ) -> None:
        """
        Assign leaders to group through OrganizationalGroupLeadership.
        
        Args:
            group: OrganizationalGroup instance
            leaders: List of Person instances to assign as leaders
        """
        today = date.today()
        
        for person in leaders:
            # Check if person is already an active leader
            existing_leadership = OrganizationalGroupLeadership.objects.filter(
                unit=group,
                person=person,
                is_active=True
            ).first()
            
            if existing_leadership:
                # Already a leader, skip
                continue
            
            # Create new leadership
            # Bypass full_clean validation due to database schema conflicts
            leadership = OrganizationalGroupLeadership(
                unit=group,
                person=person,
                start_date=today,
                is_active=True
            )
            super(OrganizationalGroupLeadership, leadership).save()
