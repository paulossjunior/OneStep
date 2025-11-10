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
    
    def get_or_create_external_research_group(self, name: str, knowledge_area: Optional[KnowledgeArea] = None) -> Optional[OrganizationalUnit]:
        """
        Get or create an external research group (OrganizationalUnit).
        
        Args:
            name: External research group name
            knowledge_area: Optional knowledge area to associate
            
        Returns:
            OrganizationalUnit: Existing or newly created unit, or None if name is empty
        """
        if not name or not name.strip():
            return None
        
        # Normalize name
        normalized_name = self.normalize_name(name)
        
        # Try to find existing unit (case-insensitive)
        unit = OrganizationalUnit.objects.filter(
            models.Q(name__iexact=normalized_name) | 
            models.Q(short_name__iexact=normalized_name)
        ).first()
        
        if unit:
            return unit
        
        # Create new external research group
        try:
            from apps.organizational_group.models import Organization, OrganizationalType, Campus
            
            # Get or create default organization for external groups
            organization, _ = Organization.objects.get_or_create(
                name='External Organizations',
                defaults={'description': 'External research groups and organizations'}
            )
            
            # Get or create Research type
            org_type, _ = OrganizationalType.objects.get_or_create(
                code='research',
                defaults={
                    'name': 'Research',
                    'description': 'Research groups'
                }
            )
            
            # Get or create default campus for external groups
            campus, _ = Campus.objects.get_or_create(
                code='EXTERNAL',
                defaults={
                    'name': 'External',
                    'location': 'External organizations'
                }
            )
            
            # Generate short name from full name
            short_name = self.generate_short_name(normalized_name)
            
            # Create the unit
            unit = OrganizationalUnit(
                name=normalized_name,
                short_name=short_name,
                type=org_type,
                organization=organization,
                campus=campus,
                knowledge_area=knowledge_area
            )
            # Save without calling full_clean() to avoid validation errors from schema conflicts
            super(OrganizationalUnit, unit).save()
            
            return unit
            
        except IntegrityError:
            # Race condition - another process created it
            return OrganizationalUnit.objects.filter(
                models.Q(name__iexact=normalized_name) | 
                models.Q(short_name__iexact=normalized_name)
            ).first()
    
    def get_or_create_demanding_partner_organization(self, name: str) -> Optional['Organization']:
        """
        Get or create a demanding partner organization (Organization).
        
        Args:
            name: Demanding partner organization name
            
        Returns:
            Organization: Existing or newly created organization, or None if name is empty
        """
        if not name or not name.strip():
            return None
        
        # Normalize name
        normalized_name = self.normalize_name(name)
        
        # Try to find existing organization (case-insensitive)
        from apps.organizational_group.models import Organization
        
        organization = Organization.objects.filter(name__iexact=normalized_name).first()
        
        if organization:
            return organization
        
        # Create new demanding partner organization
        try:
            organization = Organization.objects.create(
                name=normalized_name,
                description='Organization that demands or requests initiatives'
            )
            return organization
            
        except IntegrityError:
            # Race condition - another process created it
            return Organization.objects.filter(name__iexact=normalized_name).first()
    
    def generate_short_name(self, name: str) -> str:
        """
        Generate a short name from full name.
        
        Args:
            name: Full name
            
        Returns:
            str: Short name (acronym or truncated)
        """
        if not name:
            return "EXT"
        
        # Try to create acronym from words
        words = name.split()
        if len(words) > 1:
            acronym = ''.join([word[0].upper() for word in words if word])
            return acronym[:20]  # Limit to 20 characters
        
        # If single word, truncate
        return name[:20].upper()
    
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
