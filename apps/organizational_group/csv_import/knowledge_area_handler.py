"""
KnowledgeArea handler for CSV import.
"""

from apps.organizational_group.models import KnowledgeArea
from django.core.exceptions import ValidationError


class KnowledgeAreaHandler:
    """
    Handles KnowledgeArea creation and retrieval with deduplication.
    """
    
    def __init__(self):
        self.knowledge_area_cache = {}
    
    def get_or_create_knowledge_area(self, knowledge_area_name: str) -> KnowledgeArea:
        """
        Get existing knowledge area or create new one.
        
        Args:
            knowledge_area_name: Knowledge area name from CSV
            
        Returns:
            KnowledgeArea instance
            
        Raises:
            ValidationError: If knowledge area data is invalid
        """
        knowledge_area_name = knowledge_area_name.strip()
        
        if not knowledge_area_name:
            raise ValidationError('Knowledge area name cannot be empty')
        
        # Check cache first
        cache_key = knowledge_area_name.lower()
        if cache_key in self.knowledge_area_cache:
            return self.knowledge_area_cache[cache_key]
        
        # Try to find existing knowledge area (case-insensitive)
        knowledge_area = KnowledgeArea.objects.filter(name__iexact=knowledge_area_name).first()
        
        if knowledge_area:
            self.knowledge_area_cache[cache_key] = knowledge_area
            return knowledge_area
        
        # Create new knowledge area
        knowledge_area = KnowledgeArea.objects.create(
            name=knowledge_area_name
        )
        
        self.knowledge_area_cache[cache_key] = knowledge_area
        return knowledge_area
