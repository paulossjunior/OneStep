"""
Campus handler for CSV import.
"""

from apps.organizational_group.models import Campus
from django.core.exceptions import ValidationError


class CampusHandler:
    """
    Handles Campus creation and retrieval with deduplication.
    """
    
    def __init__(self):
        self.campus_cache = {}
    
    def get_or_create_campus(self, campus_name: str) -> Campus:
        """
        Get existing campus or create new one.
        
        Args:
            campus_name: Campus name from CSV
            
        Returns:
            Campus instance
            
        Raises:
            ValidationError: If campus data is invalid
        """
        campus_name = campus_name.strip()
        
        if not campus_name:
            raise ValidationError('Campus name cannot be empty')
        
        # Check cache first
        cache_key = campus_name.lower()
        if cache_key in self.campus_cache:
            return self.campus_cache[cache_key]
        
        # Try to find existing campus (case-insensitive)
        campus = Campus.objects.filter(name__iexact=campus_name).first()
        
        if campus:
            self.campus_cache[cache_key] = campus
            return campus
        
        # Create new campus
        code = self.generate_campus_code(campus_name)
        campus = Campus.objects.create(
            name=campus_name,
            code=code
        )
        
        self.campus_cache[cache_key] = campus
        return campus
    
    def generate_campus_code(self, campus_name: str) -> str:
        """
        Generate unique campus code from name.
        
        Args:
            campus_name: Campus name
            
        Returns:
            str: Unique campus code
        """
        # Generate base code: uppercase, remove spaces, truncate to 20 chars
        base_code = campus_name.upper().replace(' ', '')[:20]
        
        # Check if code exists
        if not Campus.objects.filter(code=base_code).exists():
            return base_code
        
        # Handle collision by appending numeric suffix
        suffix = 1
        while True:
            code = f"{base_code[:17]}{suffix:03d}"
            if not Campus.objects.filter(code=code).exists():
                return code
            suffix += 1
            if suffix > 999:
                raise ValidationError(f'Cannot generate unique code for campus: {campus_name}')
