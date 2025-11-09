"""
Handler for OrganizationalUnit and KnowledgeArea management.
"""

from typing import Optional
from django.db import IntegrityError
from django.db import models
from apps.organizational_group.models import OrganizationalUnit, KnowledgeArea


class GroupHandler:
    """
    Handles OrganizationalGroup and KnowledgeArea creation and retrieval.
    """
    
    def get_or_create_knowledge_area(self, name: str) -> Optional[KnowledgeArea]:
        """
        Get or create a KnowledgeArea by name.
        
        Args:
            name: Knowledge area name
            
        Returns:
            KnowledgeArea: Existing or newly created knowledge area, or None if name is empty
        """
        if not name or not name.strip():
            return None
        
        # Normalize name
        normalized_name = self.normalize_name(name)
        
        # Try to find existing knowledge area (case-insensitive)
        knowledge_area = KnowledgeArea.objects.filter(name__iexact=normalized_name).first()
        
        if knowledge_area:
            return knowledge_area
        
        # Create new knowledge area
        try:
            knowledge_area = KnowledgeArea.objects.create(
                name=normalized_name
            )
            return knowledge_area
        except IntegrityError:
            # Race condition - another process created it
            return KnowledgeArea.objects.filter(name__iexact=normalized_name).first()
    
    def get_organizational_unit(self, name: str) -> Optional[OrganizationalUnit]:
        """
        Get an OrganizationalUnit by name.
        
        Args:
            name: Organizational unit name
            
        Returns:
            OrganizationalUnit: Existing unit or None if not found
        """
        if not name or not name.strip():
            return None
        
        # Normalize name
        normalized_name = self.normalize_name(name)
        
        # Try to find existing unit (case-insensitive)
        # Search by both name and short_name
        unit = OrganizationalUnit.objects.filter(
            models.Q(name__iexact=normalized_name) | 
            models.Q(short_name__iexact=normalized_name)
        ).first()
        
        return unit
    
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
