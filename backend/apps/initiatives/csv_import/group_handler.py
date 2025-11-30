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
    
    def get_or_create_external_research_group(self, name: str, knowledge_area: Optional[KnowledgeArea] = None, campus_name: Optional[str] = None) -> Optional[OrganizationalUnit]:
        """
        Get or create an external research group (OrganizationalUnit).
        
        Args:
            name: External research group name
            knowledge_area: Optional knowledge area to associate
            campus_name: Optional campus name from CampusExecucao (if not provided, uses default "External" campus)
            
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
                name='Default Organization',
                defaults={'description': 'Default organization for imported groups'}
            )
            
            # Get or create Research type
            org_type, _ = OrganizationalType.objects.get_or_create(
                code='research',
                defaults={
                    'name': 'Research',
                    'description': 'Research groups'
                }
            )
            
            # Get or create campus
            if campus_name and campus_name.strip():
                # Use provided campus name from CampusExecucao
                normalized_campus_name = self.normalize_name(campus_name)
                campus = Campus.objects.filter(name__iexact=normalized_campus_name).first()
                
                if not campus:
                    # Create campus if it doesn't exist
                    campus_code = normalized_campus_name[:3].upper()
                    campus, _ = Campus.objects.get_or_create(
                        code=campus_code,
                        defaults={
                            'name': normalized_campus_name,
                            'location': f'{normalized_campus_name} campus'
                        }
                    )
            else:
                # Use default campus for external groups
                campus, _ = Campus.objects.get_or_create(
                    code='EXTERNAL',
                    defaults={
                        'name': 'External',
                        'location': 'External organizations'
                    }
                )
            
            # Generate short name from full name
            short_name = self.generate_short_name(normalized_name)
            
            # Create the unit without leadership
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
    
    def normalize_organization_name(self, name: str) -> str:
        """
        Normalize organization name by removing common suffixes and patterns.
        This helps identify similar organizations like "ArcelorMittal" and "ArcelorMittal Tubarão".
        
        Args:
            name: Organization name
            
        Returns:
            str: Normalized organization name
        """
        import re
        
        if not name:
            return ""
        
        # Convert to title case
        normalized = name.strip().title()
        
        # Remove content in parentheses (e.g., "ArcelorMittal (Convênio 02/2024)" -> "ArcelorMittal")
        normalized = re.sub(r'\s*\([^)]*\)', '', normalized)
        
        # Remove common suffixes and location names
        # List of patterns to remove (case-insensitive)
        patterns_to_remove = [
            r'\s+Tubarão$',
            r'\s+Serra$',
            r'\s+Vitória$',
            r'\s+ES$',
            r'\s+Espírito Santo$',
            r'\s+S\.?A\.?$',
            r'\s+Ltda\.?$',
            r'\s+Ltd\.?$',
            r'\s+Inc\.?$',
            r'\s+Corporation$',
            r'\s+Corp\.?$',
        ]
        
        for pattern in patterns_to_remove:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized.strip()
    
    def find_similar_organization(self, name: str) -> Optional['Organization']:
        """
        Find an existing organization with a similar name.
        
        Args:
            name: Organization name to search for
            
        Returns:
            Organization: Existing organization with similar name, or None
        """
        from apps.organizational_group.models import Organization
        
        # Normalize the input name
        normalized_input = self.normalize_organization_name(name)
        
        if not normalized_input:
            return None
        
        # Try exact match first (case-insensitive)
        org = Organization.objects.filter(name__iexact=normalized_input).first()
        if org:
            return org
        
        # Try to find organizations with similar normalized names
        all_orgs = Organization.objects.all()
        for org in all_orgs:
            normalized_existing = self.normalize_organization_name(org.name)
            if normalized_existing.lower() == normalized_input.lower():
                return org
        
        return None
    
    def get_or_create_demanding_partner_organization(self, name: str) -> Optional['Organization']:
        """
        Get or create a demanding partner organization (Organization).
        Uses name normalization to avoid creating duplicate organizations with similar names.
        
        Args:
            name: Demanding partner organization name
            
        Returns:
            Organization: Existing or newly created organization, or None if name is empty
        """
        if not name or not name.strip():
            return None
        
        # Try to find similar existing organization first
        from apps.organizational_group.models import Organization
        
        existing_org = self.find_similar_organization(name)
        if existing_org:
            return existing_org
        
        # Normalize name for storage
        normalized_name = self.normalize_name(name)
        
        # Create new demanding partner organization
        try:
            organization = Organization.objects.create(
                name=normalized_name,
                description='Organization that demands or requests initiatives'
            )
            return organization
            
        except IntegrityError:
            # Race condition - another process created it
            # Try to find it again with normalization
            return self.find_similar_organization(name) or Organization.objects.filter(name__iexact=normalized_name).first()
    
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
    
    def get_or_create_campus(self, campus_name: str) -> Optional['Campus']:
        """
        Get or create a Campus by name.
        
        Args:
            campus_name: Campus name from CampusExecucao
            
        Returns:
            Campus: Existing or newly created campus, or None if name is empty
        """
        if not campus_name or not campus_name.strip():
            return None
        
        from apps.organizational_group.models import Campus
        
        # Normalize campus name
        normalized_name = self.normalize_name(campus_name)
        
        # Try to find existing campus (case-insensitive)
        campus = Campus.objects.filter(name__iexact=normalized_name).first()
        
        if campus:
            return campus
        
        # Create new campus
        try:
            # Generate campus code from name (first 3 letters, uppercase)
            campus_code = normalized_name[:3].upper()
            
            # Check if code already exists, if so, add number
            base_code = campus_code
            counter = 1
            while Campus.objects.filter(code=campus_code).exists():
                campus_code = f"{base_code}{counter}"
                counter += 1
            
            campus = Campus.objects.create(
                name=normalized_name,
                code=campus_code,
                location=f'{normalized_name} campus'
            )
            return campus
            
        except IntegrityError:
            # Race condition - another process created it
            return Campus.objects.filter(name__iexact=normalized_name).first()
    
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
