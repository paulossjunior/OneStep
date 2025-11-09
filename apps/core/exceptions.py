from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    
    Args:
        exc: The exception instance
        context: The context in which the exception occurred
        
    Returns:
        Response: Formatted error response
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the error response format
        custom_response_data = {
            'error': {
                'code': exc.__class__.__name__.upper(),
                'message': 'An error occurred',
                'details': response.data
            }
        }
        
        # Set appropriate error messages based on status code
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['error']['message'] = 'Invalid data provided'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['error']['message'] = 'Authentication required'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['error']['message'] = 'Access denied'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['error']['message'] = 'Resource not found'
        elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            custom_response_data['error']['message'] = 'Rate limit exceeded'
        elif response.status_code >= 500:
            custom_response_data['error']['message'] = 'Internal server error'
            # Log server errors
            logger.error(f"Server error: {exc}", exc_info=True)
        
        response.data = custom_response_data
        return response
    
    # Handle Django validation errors
    if isinstance(exc, DjangoValidationError):
        custom_response_data = {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid data provided',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else {'non_field_errors': exc.messages}
            }
        }
        return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle database integrity errors
    if isinstance(exc, IntegrityError):
        custom_response_data = {
            'error': {
                'code': 'INTEGRITY_ERROR',
                'message': 'Database constraint violation',
                'details': {'non_field_errors': ['This operation violates database constraints']}
            }
        }
        return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # For unhandled exceptions, log and return generic error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return Response({
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred',
            'details': {}
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)