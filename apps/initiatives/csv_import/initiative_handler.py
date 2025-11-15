"""
Handler for Initiative creation and duplicate detection.
"""

from typing import Optional, Tuple
from datetime import datetime
from apps.initiatives.models import Initiative, InitiativeType, InitiativeCoordinatorChange
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
    
    def create_or_get_initiative(
        self,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        coordinator: Person,
        campus=None
    ) -> Tuple[Initiative, bool, bool]:
        """
        Create Initiative or get existing if duplicate exists.
        Also checks for coordinator changes.
        
        Duplicate detection: same name (different coordinator allowed)
        
        Args:
            name: Initiative name
            description: Initiative description
            start_date: Start date
            end_date: End date
            coordinator: Coordinator Person
            campus: Campus where initiative is performed (optional)
            
        Returns:
            Tuple of (Initiative, is_existing, coordinator_changed)
            - Initiative: The created or existing initiative
            - is_existing: True if initiative already existed, False if newly created
            - coordinator_changed: True if coordinator was changed, False otherwise
        """
        # Normalize name
        normalized_name = self.normalize_name(name)
        
        # Check for existing initiative with same coordinator
        existing_initiative = self.get_existing_initiative(normalized_name, coordinator)
        if existing_initiative:
            return existing_initiative, True, False
        
        # Check for existing initiative with different coordinator (by name only)
        existing_with_different_coordinator = self.get_initiative_by_name(normalized_name)
        if existing_with_different_coordinator:
            # Coordinator has changed
            previous_coordinator = existing_with_different_coordinator.coordinator
            
            # Track the coordinator change
            InitiativeCoordinatorChange.objects.create(
                initiative=existing_with_different_coordinator,
                previous_coordinator=previous_coordinator,
                new_coordinator=coordinator,
                change_reason=f"CSV import detected coordinator change from {previous_coordinator.full_name} to {coordinator.full_name}",
                changed_by='CSV Import'
            )
            
            # Update the coordinator
            existing_with_different_coordinator.coordinator = coordinator
            existing_with_different_coordinator.save()
            
            return existing_with_different_coordinator, True, True
        
        # Get research project type
        project_type = self.get_research_project_type()
        
        # Create initiative
        initiative = Initiative.objects.create(
            name=normalized_name,
            description=description,
            type=project_type,
            start_date=start_date.date() if start_date else None,
            end_date=end_date.date() if end_date else None,
            coordinator=coordinator,
            campus=campus
        )
        
        return initiative, False, False
    
    def get_existing_initiative(self, name: str, coordinator: Person) -> Optional[Initiative]:
        """
        Get existing initiative with same name and coordinator.
        
        Args:
            name: Initiative name (normalized)
            coordinator: Coordinator Person
            
        Returns:
            Initiative: Existing initiative or None
        """
        return Initiative.objects.filter(
            name__iexact=name,
            coordinator=coordinator
        ).first()
    
    def get_initiative_by_name(self, name: str) -> Optional[Initiative]:
        """
        Get existing initiative by name only (regardless of coordinator).
        
        Args:
            name: Initiative name (normalized)
            
        Returns:
            Initiative: Existing initiative or None
        """
        return Initiative.objects.filter(name__iexact=name).first()
    
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
