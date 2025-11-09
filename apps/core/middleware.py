import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests and response times.
    """
    
    def process_request(self, request):
        """
        Log incoming requests and start timing.
        """
        request.start_time = time.time()
        
        # Log API requests (but not admin or static files)
        if request.path.startswith('/api/'):
            logger.info(
                f"API Request: {request.method} {request.path} "
                f"from {request.META.get('REMOTE_ADDR', 'unknown')}"
            )
    
    def process_response(self, request, response):
        """
        Log response times for API requests.
        """
        if hasattr(request, 'start_time') and request.path.startswith('/api/'):
            duration = time.time() - request.start_time
            logger.info(
                f"API Response: {request.method} {request.path} "
                f"- {response.status_code} in {duration:.3f}s"
            )
            
            # Log slow requests (over 1 second)
            if duration > 1.0:
                logger.warning(
                    f"Slow API request: {request.method} {request.path} "
                    f"took {duration:.3f}s"
                )
        
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to all responses.
        """
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add API-specific headers
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to implement rate limiting for API endpoints.
    Uses Django cache to track request counts per IP address.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limits: requests per minute
        self.rate_limits = {
            'default': 60,  # 60 requests per minute for general API
            'auth': 10,     # 10 requests per minute for auth endpoints
            'admin': 30,    # 30 requests per minute for admin
        }
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Check rate limits before processing the request.
        """
        # Skip rate limiting during tests
        if hasattr(settings, 'TESTING') and settings.TESTING:
            return None
        
        # Skip rate limiting for non-API requests in DEBUG mode
        if settings.DEBUG and not request.path.startswith('/api/'):
            return None
        
        # Get client IP address
        client_ip = self.get_client_ip(request)
        
        # Determine rate limit based on endpoint
        rate_limit = self.get_rate_limit(request.path)
        
        # Create cache key
        cache_key = f"rate_limit:{client_ip}:{request.path.split('/')[1]}"
        
        # Get current request count
        current_requests = cache.get(cache_key, 0)
        
        # Check if rate limit exceeded
        if current_requests >= rate_limit:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip} on {request.path}"
            )
            return JsonResponse({
                'error': {
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded. Please try again later.',
                    'details': {
                        'limit': rate_limit,
                        'window': '1 minute'
                    }
                }
            }, status=429)
        
        # Increment request count
        cache.set(cache_key, current_requests + 1, 60)  # 60 seconds window
        
        return None
    
    def get_client_ip(self, request):
        """
        Get the client IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_rate_limit(self, path):
        """
        Determine the appropriate rate limit based on the request path.
        """
        if '/auth/' in path:
            return self.rate_limits['auth']
        elif '/admin/' in path:
            return self.rate_limits['admin']
        else:
            return self.rate_limits['default']