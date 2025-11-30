import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_positive_number(value):
    """
    Validate that a number is positive.
    
    Args:
        value: The number to validate
        
    Raises:
        ValidationError: If the value is not positive
    """
    if value <= 0:
        raise ValidationError(
            _('%(value)s must be a positive number.'),
            params={'value': value},
        )


def validate_future_date(value):
    """
    Validate that a date is in the future.
    
    Args:
        value: The date to validate
        
    Raises:
        ValidationError: If the date is not in the future
    """
    from datetime import date
    
    if value <= date.today():
        raise ValidationError(
            _('Date must be in the future.'),
        )


def validate_phone_number(value):
    """
    Validate phone number format.
    
    Accepts various phone number formats including:
    - +1234567890
    - (123) 456-7890
    - 123-456-7890
    - 123.456.7890
    - 123 456 7890
    
    Args:
        value: The phone number to validate
        
    Raises:
        ValidationError: If the phone number format is invalid
    """
    if not value:  # Allow empty phone numbers
        return
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', value)
    
    # Check if it's a valid format (10-15 digits, optionally starting with +)
    if not re.match(r'^\+?\d{10,15}$', cleaned):
        raise ValidationError(
            _('Enter a valid phone number (10-15 digits, optionally starting with +).'),
        )


def validate_date_range(start_date, end_date):
    """
    Validate that end_date is after start_date.
    
    Args:
        start_date: The start date
        end_date: The end date (can be None)
        
    Raises:
        ValidationError: If end_date is before start_date
    """
    if end_date and start_date and end_date < start_date:
        raise ValidationError(
            _('End date must be after start date.'),
        )


def validate_non_empty_string(value):
    """
    Validate that a string is not empty or just whitespace.
    
    Args:
        value: The string to validate
        
    Raises:
        ValidationError: If the string is empty or just whitespace
    """
    if not value or not value.strip():
        raise ValidationError(
            _('This field cannot be empty.'),
        )