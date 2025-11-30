"""
Validator for research project CSV data.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """
    Result of validation for a CSV row.
    """
    is_valid: bool
    errors: List[str]
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
    
    def add_error(self, error: str):
        """
        Add validation error.
        
        Args:
            error: Error message
        """
        self.is_valid = False
        self.errors.append(error)


class ResearchProjectValidator:
    """
    Validates research project CSV data.
    """
    
    # Required fields
    REQUIRED_FIELDS = ['Titulo', 'Coordenador', 'EmailCoordenador', 'Inicio', 'Fim']
    
    # Email regex pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def validate_row(self, row: Dict[str, str]) -> ValidationResult:
        """
        Validate a single CSV row.
        
        Args:
            row: Dictionary containing row data
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in row or not row[field]:
                result.add_error(f"Missing required field: {field}")
        
        # If required fields are missing, return early
        if not result.is_valid:
            return result
        
        # Validate email
        if not self.validate_email(row['EmailCoordenador']):
            result.add_error(f"Invalid email format: {row['EmailCoordenador']}")
        
        # Validate dates
        start_date = self.parse_date(row['Inicio'])
        if start_date is None:
            result.add_error(f"Invalid start date format: {row['Inicio']} (expected DD-MM-YY)")
        
        end_date = self.parse_date(row['Fim'])
        if end_date is None:
            result.add_error(f"Invalid end date format: {row['Fim']} (expected DD-MM-YY)")
        
        # Validate date range
        if start_date and end_date:
            if not self.validate_date_range(start_date, end_date):
                result.add_error(f"End date ({row['Fim']}) must be after or equal to start date ({row['Inicio']})")
        
        return result
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if email is valid
        """
        if not email:
            return False
        return bool(self.EMAIL_PATTERN.match(email.strip()))
    
    def validate_date(self, date_str: str) -> bool:
        """
        Validate date format (DD-MM-YY).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            bool: True if date format is valid
        """
        return self.parse_date(date_str) is not None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string in DD-MM-YY format.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        try:
            # Try DD-MM-YY format
            return datetime.strptime(date_str.strip(), '%d-%m-%y')
        except ValueError:
            return None
    
    def validate_date_range(self, start_date: datetime, end_date: datetime) -> bool:
        """
        Validate that end date is after or equal to start date.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            bool: True if date range is valid
        """
        return end_date >= start_date
