"""
OrganizationalGroup handler for CSV import.
"""

from typing import Tuple, List
from datetime import date
from apps.organizational_group.models import OrganizationalGroup, OrganizationalGroupLeadership, Campus, KnowledgeArea
from apps.people.models import Person
from django.core.exceptions import ValidationError


class GroupHandler:
    """
    Handles OrganizationalGroup creation with deduplication and leadership assignment.
    """
    
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
            short_name = self._generate_short_name(name)
        else:
            short_name = short_name.strip()
        
        # Check for duplicate (short_name + campus combination)
        existing_group = OrganizationalGroup.objects.filter(
            short_name__iexact=short_name,
            campus=campus
        ).first()
        
        if existing_group:
            return existing_group, False
        
        # Create new group
        group = OrganizationalGroup.objects.create(
            name=name,
            short_name=short_name,
            url=repository_url.strip() if repository_url else "",
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area=knowledge_area,
            campus=campus
        )
        
        return group, True
    
    def _generate_short_name(self, name: str) -> str:
        """
        Generate short_name from full name.
        
        When short_name is not provided, defaults to "non-informed".
        
        Args:
            name: Full group name
            
        Returns:
            str: "non-informed" as default value
        """
        return "non-informed"
    
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
                group=group,
                person=person,
                is_active=True
            ).first()
            
            if existing_leadership:
                # Already a leader, skip
                continue
            
            # Create new leadership
            OrganizationalGroupLeadership.objects.create(
                group=group,
                person=person,
                start_date=today,
                is_active=True
            )
