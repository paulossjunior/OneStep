"""
Handler for Initiative creation and duplicate detection.
"""

from typing import Optional, Tuple
from datetime import datetime
from apps.initiatives.models import Initiative, InitiativeType
from apps.people.models import Person


class InitiativeHandler:
    """
    Handles Initiative creation and duplicate detection for CSV import.
    """
    
    def __init__(self):
        self._research_project_type = None
    
    def get_research_project_type(self) -> InitiativeType:
        """
        Get or create "Research Project" InitiativeType.
        
        Returns:
            InitiativeType: Research Project type
        """
        if self._research_project_type is None:
            self._research_project_type, _ = InitiativeType.objects.get_or_create(
                code='research_project',
                defaults={
                    'name': 'Research Project',
                    'description': 'Research projects imported from CSV',
                    'is_active': True
                }
            )
        return self._research_project_type
    
    def create_or_skip_initiative(
        self,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        coordinator: Person
    ) -> Tuple[Optional[Initiative], bool]:
        """
        Create Initiative or skip if duplicate exists.
        
        Duplicate detection: same name + same coordinator
        
        Args:
            name: Initiative name
            description: Initiative description
            start_date: Start date
            end_date: End date
            coordinator: Coordinator Person
            
        Returns:
            Tuple of (Initiative or None, is_duplicate)
        """
        # Normalize name
        normalized_name = self.normalize_name(name)
        
        # Check for duplicate
        if self.is_duplicate(normalized_name, coordinator):
            return None, True
        
        # Get research project type
        project_type = self.get_research_project_type()
        
        # Create initiative
        initiative = Initiative.objects.create(
            name=normalized_name,
            description=description,
            type=project_type,
            start_date=start_date.date() if start_date else None,
            end_date=end_date.date() if end_date else None,
            coordinator=coordinator
        )
        
        return initiative, False
    
    def is_duplicate(self, name: str, coordinator: Person) -> bool:
        """
        Check if initiative is duplicate (same name + same coordinator).
        
        Args:
            name: Initiative name (normalized)
            coordinator: Coordinator Person
            
        Returns:
            bool: True if duplicate exists
        """
        return Initiative.objects.filter(
            name__iexact=name,
            coordinator=coordinator
        ).exists()
    
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
