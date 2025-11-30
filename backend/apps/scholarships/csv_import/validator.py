"""
Validator for scholarship CSV data.
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal, InvalidOperation


class ValidationResult:
    """Result of validation."""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
    
    def add_error(self, error: str):
        """Add validation error."""
        self.is_valid = False
        self.errors.append(error)


class ScholarshipValidator:
    """
    Validates scholarship CSV data.
    """
    
    def validate_row(self, row: dict) -> ValidationResult:
        """
        Validate a single CSV row.
        
        Args:
            row: Dictionary containing row data
            
        Returns:
            ValidationResult: Validation result with errors if any
        """
        result = ValidationResult()
        
        # Note: Valor is optional - if empty, will default to 0
        
        if not row.get('Inicio'):
            result.add_error("Inicio (start date) is required")
        
        if not row.get('Orientador'):
            result.add_error("Orientador (supervisor) is required")
        
        if not row.get('Orientado'):
            result.add_error("Orientado (student) is required")
        
        if not row.get('CampusExecucao'):
            result.add_error("CampusExecucao (campus) is required")
        
        # Validate value format (if provided)
        if row.get('Valor') and row.get('Valor').strip():
            try:
                self.parse_value(row['Valor'])
            except (ValueError, InvalidOperation) as e:
                result.add_error(f"Invalid Valor format: {str(e)}")
        
        # Validate date formats
        if row.get('Inicio'):
            try:
                self.parse_date(row['Inicio'])
            except ValueError as e:
                result.add_error(f"Invalid Inicio date format: {str(e)}")
        
        if row.get('Fim'):
            try:
                self.parse_date(row['Fim'])
            except ValueError as e:
                result.add_error(f"Invalid Fim date format: {str(e)}")
        
        return result
    
    def parse_date(self, date_str: str) -> Optional[datetime.date]:
        """
        Parse date string in DD-MM-YY format.
        
        Args:
            date_str: Date string
            
        Returns:
            date object or None
        """
        if not date_str or not date_str.strip():
            return None
        
        # Try DD-MM-YY format
        try:
            dt = datetime.strptime(date_str.strip(), '%d-%m-%y')
            return dt.date()
        except ValueError:
            pass
        
        # Try DD/MM/YYYY format
        try:
            dt = datetime.strptime(date_str.strip(), '%d/%m/%Y')
            return dt.date()
        except ValueError:
            pass
        
        # Try YYYY-MM-DD format
        try:
            dt = datetime.strptime(date_str.strip(), '%Y-%m-%d')
            return dt.date()
        except ValueError:
            raise ValueError(f"Date '{date_str}' must be in DD-MM-YY, DD/MM/YYYY, or YYYY-MM-DD format")
    
    def parse_value(self, value_str: str) -> Decimal:
        """
        Parse monetary value string.
        
        Args:
            value_str: Value string (e.g., "300,00" or "300.00")
            
        Returns:
            Decimal value (0 if empty or blank)
        """
        if not value_str or not value_str.strip():
            return Decimal('0')
        
        # Remove currency symbols and spaces
        cleaned = value_str.strip().replace('R$', '').replace(' ', '')
        
        # Replace comma with dot for decimal
        cleaned = cleaned.replace(',', '.')
        
        try:
            value = Decimal(cleaned)
            if value < 0:
                raise ValueError("Value cannot be negative")
            return value
        except InvalidOperation:
            raise ValueError(f"Invalid value format: {value_str}")
