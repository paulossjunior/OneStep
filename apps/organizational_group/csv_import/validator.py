"""
Data validator for CSV import.
"""

import re
from typing import Dict, List, Tuple
from django.core.validators import EmailValidator, URLValidator
from django.core.exceptions import ValidationError


class ValidationResult:
    """Result of row validation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []


class DataValidator:
    """
    Validates CSV row data before processing.
    """
    
    def __init__(self):
        self.email_validator = EmailValidator()
        self.url_validator = URLValidator()
    
    def validate_row(self, row: Dict[str, str], row_number: int) -> ValidationResult:
        """
        Validate a single CSV row.
        
        Args:
            row: Dictionary of column values
            row_number: Row number for error reporting
            
        Returns:
            ValidationResult with is_valid flag and error messages
        """
        errors = []
        
        # Validate required fields
        if not row.get('Nome', '').strip():
            errors.append('Nome (name) is required')
        
        if not row.get('Unidade', '').strip():
            errors.append('Unidade (campus) is required')
        
        if not row.get('AreaConhecimento', '').strip():
            errors.append('AreaConhecimento (knowledge area) is required')
        
        # Validate URLs if present
        if row.get('repositorio', '').strip():
            if not self.validate_url(row['repositorio']):
                errors.append(f'Invalid repository URL: {row["repositorio"]}')
        
        if row.get('Site', '').strip():
            if not self.validate_url(row['Site']):
                errors.append(f'Invalid site URL: {row["Site"]}')
        
        # Validate leader emails if present
        if row.get('Lideres', '').strip():
            leader_errors = self.validate_leaders(row['Lideres'])
            errors.extend(leader_errors)
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            self.email_validator(email.strip())
            return True
        except ValidationError:
            return False
    
    def validate_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Automatically adds https:// prefix if URL doesn't have a protocol.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            normalized_url = self.normalize_url(url)
            self.url_validator(normalized_url)
            return True
        except ValidationError:
            return False
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize URL by adding https:// prefix if no protocol is present.
        
        Args:
            url: URL to normalize
            
        Returns:
            str: Normalized URL with protocol
        """
        url = url.strip()
        if not url:
            return url
        
        # Add https:// if no protocol is present
        if not url.startswith(('http://', 'https://', 'ftp://')):
            return f'https://{url}'
        
        return url
    
    def validate_leaders(self, leaders_str: str) -> List[str]:
        """
        Validate leader format and emails.
        
        Args:
            leaders_str: Comma-separated leader entries
            
        Returns:
            List of error messages
        """
        errors = []
        
        # Parse leaders
        leader_pattern = r'(.+?)\s*\(([^)]+)\)'
        leaders = leaders_str.split(',')
        
        for leader in leaders:
            leader = leader.strip()
            if not leader:
                continue
            
            match = re.match(leader_pattern, leader)
            if not match:
                errors.append(f'Invalid leader format: {leader}. Expected "Name (email)"')
                continue
            
            name, email = match.groups()
            if not self.validate_email(email):
                errors.append(f'Invalid email for leader {name.strip()}: {email.strip()}')
        
        return errors
