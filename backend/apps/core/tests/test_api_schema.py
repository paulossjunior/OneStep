"""
Test cases for API schema generation and documentation.

This test suite validates:
- OpenAPI schema generation succeeds
- Schema complies with OpenAPI 3.0 specification
- All critical endpoints are documented
- Swagger UI and ReDoc interfaces are accessible
- JWT authentication is properly documented
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import json


class SchemaValidationTest(TestCase):
    """
    Test cases for validating OpenAPI schema generation and compliance.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
        # Set SERVER_NAME to avoid ALLOWED_HOSTS issues in tests
        self.client.defaults['SERVER_NAME'] = 'testserver'
        
        # Create test user for authenticated requests
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def _get_schema(self):
        """Helper method to get schema as JSON."""
        response = self.client.get('/api/schema/', HTTP_ACCEPT='application/json')
        return json.loads(response.content)
    
    def test_schema_generation_succeeds(self):
        """Test that OpenAPI schema generates without errors."""
        response = self.client.get('/api/schema/', HTTP_ACCEPT='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('application/json', response['Content-Type'])
        
        # Verify response contains valid JSON
        schema = json.loads(response.content)
        self.assertIsInstance(schema, dict)
    
    def test_openapi_3_compliance(self):
        """Test that schema complies with OpenAPI 3.0 specification."""
        schema = self._get_schema()
        
        # Check required OpenAPI 3.0 fields
        self.assertIn('openapi', schema)
        self.assertTrue(schema['openapi'].startswith('3.0'))
        
        self.assertIn('info', schema)
        self.assertIn('title', schema['info'])
        self.assertIn('version', schema['info'])
        
        self.assertIn('paths', schema)
        self.assertIsInstance(schema['paths'], dict)
        
        self.assertIn('components', schema)
        self.assertIsInstance(schema['components'], dict)
    
    def test_schema_metadata(self):
        """Test that schema contains correct project metadata."""
        schema = self._get_schema()
        
        # Verify project information
        self.assertEqual(schema['info']['title'], 'OneStep API')
        self.assertEqual(schema['info']['version'], '1.0.0')
        self.assertIn('description', schema['info'])
        self.assertIn('initiatives', schema['info']['description'].lower())
    
    def test_critical_endpoints_documented(self):
        """Test that all critical API endpoints are documented in schema."""
        schema = self._get_schema()
        paths = schema['paths']
        
        # Critical Initiative endpoints
        self.assertIn('/api/initiatives/', paths)
        self.assertIn('/api/initiatives/{id}/', paths)
        
        # Critical People endpoints
        self.assertIn('/api/people/', paths)
        self.assertIn('/api/people/{id}/', paths)
        
        # Verify HTTP methods are documented
        initiatives_list = paths['/api/initiatives/']
        self.assertIn('get', initiatives_list)
        self.assertIn('post', initiatives_list)
        
        initiatives_detail = paths['/api/initiatives/{id}/']
        self.assertIn('get', initiatives_detail)
        self.assertIn('put', initiatives_detail)
        self.assertIn('patch', initiatives_detail)
        self.assertIn('delete', initiatives_detail)
    
    def test_custom_actions_documented(self):
        """Test that custom ViewSet actions are documented."""
        schema = self._get_schema()
        paths = schema['paths']
        
        # Initiative custom actions
        self.assertIn('/api/initiatives/{id}/hierarchy/', paths)
        self.assertIn('/api/initiatives/{id}/add_team_member/', paths)
        self.assertIn('/api/initiatives/{id}/remove_team_member/', paths)
        self.assertIn('/api/initiatives/types/', paths)
        self.assertIn('/api/initiatives/search/', paths)
        
        # People custom actions
        self.assertIn('/api/people/{id}/initiatives/', paths)
        self.assertIn('/api/people/search/', paths)
    
    def test_endpoint_operations_have_descriptions(self):
        """Test that endpoints have operation summaries and descriptions."""
        schema = self._get_schema()
        paths = schema['paths']
        
        # Check initiatives list endpoint
        initiatives_list_get = paths['/api/initiatives/']['get']
        self.assertIn('summary', initiatives_list_get)
        self.assertIn('description', initiatives_list_get)
        self.assertIn('tags', initiatives_list_get)
        
        # Check people list endpoint
        people_list_get = paths['/api/people/']['get']
        self.assertIn('summary', people_list_get)
        self.assertIn('description', people_list_get)
        self.assertIn('tags', people_list_get)
    
    def test_schema_components_defined(self):
        """Test that schema components (models) are properly defined."""
        schema = self._get_schema()
        components = schema['components']
        
        # Check that schemas are defined
        self.assertIn('schemas', components)
        schemas = components['schemas']
        
        # Verify key model schemas exist
        # Note: Schema names may vary based on serializer naming
        schema_names = list(schemas.keys())
        
        # Check for Initiative-related schemas
        initiative_schemas = [s for s in schema_names if 'Initiative' in s]
        self.assertGreater(len(initiative_schemas), 0, 
                          "Initiative schemas should be defined")
        
        # Check for Person-related schemas
        person_schemas = [s for s in schema_names if 'Person' in s]
        self.assertGreater(len(person_schemas), 0,
                          "Person schemas should be defined")
    
    def test_request_response_schemas_linked(self):
        """Test that endpoints link to request/response schemas."""
        schema = self._get_schema()
        paths = schema['paths']
        
        # Check POST endpoint has requestBody
        initiatives_post = paths['/api/initiatives/']['post']
        self.assertIn('requestBody', initiatives_post)
        self.assertIn('content', initiatives_post['requestBody'])
        
        # Check GET endpoint has responses
        initiatives_get = paths['/api/initiatives/']['get']
        self.assertIn('responses', initiatives_get)
        self.assertIn('200', initiatives_get['responses'])
    
    def test_parameters_documented(self):
        """Test that query parameters are documented."""
        schema = self._get_schema()
        paths = schema['paths']
        
        # Check list endpoints have pagination and filtering parameters
        initiatives_list_get = paths['/api/initiatives/']['get']
        
        if 'parameters' in initiatives_list_get:
            parameters = initiatives_list_get['parameters']
            param_names = [p['name'] for p in parameters]
            
            # Common parameters that should be documented
            # Note: Exact parameters depend on ViewSet configuration
            self.assertIsInstance(parameters, list)
            self.assertGreater(len(parameters), 0,
                             "List endpoints should have parameters documented")


class UIAccessibilityTest(TestCase):
    """
    Test cases for validating documentation UI accessibility.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
    
    def test_swagger_ui_loads_successfully(self):
        """Test that Swagger UI interface loads successfully."""
        response = self.client.get('/api/docs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        
        # Verify Swagger UI content is present
        content = response.content.decode('utf-8')
        self.assertIn('swagger-ui', content.lower())
    
    def test_redoc_ui_loads_successfully(self):
        """Test that ReDoc interface loads successfully."""
        response = self.client.get('/api/redoc/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        
        # Verify ReDoc content is present
        content = response.content.decode('utf-8')
        self.assertIn('redoc', content.lower())
    
    def test_schema_endpoint_returns_valid_json(self):
        """Test that schema endpoint returns valid JSON."""
        response = self.client.get('/api/schema/', HTTP_ACCEPT='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify JSON is valid and parseable
        try:
            schema = json.loads(response.content)
            self.assertIsInstance(schema, dict)
        except json.JSONDecodeError:
            self.fail("Schema endpoint did not return valid JSON")
    
    def test_schema_format_parameter(self):
        """Test that schema can be retrieved in different formats."""
        # Test JSON format (default)
        response = self.client.get('/api/schema/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test YAML format if supported
        response = self.client.get('/api/schema/?format=yaml', HTTP_ACCEPT='application/yaml')
        # Should either return YAML or redirect/default to JSON
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_406_NOT_ACCEPTABLE])


class AuthenticationDocumentationTest(TestCase):
    """
    Test cases for validating JWT authentication documentation.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
    
    def _get_schema(self):
        """Helper method to get schema as JSON."""
        response = self.client.get('/api/schema/', HTTP_ACCEPT='application/json')
        return json.loads(response.content)
    
    def test_jwt_security_scheme_in_schema(self):
        """Test that JWT security scheme is defined in schema."""
        schema = self._get_schema()
        
        # Check security schemes are defined
        self.assertIn('components', schema)
        self.assertIn('securitySchemes', schema['components'])
        
        security_schemes = schema['components']['securitySchemes']
        
        # Verify JWT auth is defined
        self.assertIn('jwtAuth', security_schemes)
        jwt_scheme = security_schemes['jwtAuth']
        
        # Verify JWT scheme properties
        self.assertEqual(jwt_scheme['type'], 'http')
        self.assertEqual(jwt_scheme['scheme'], 'bearer')
        self.assertIn('bearerFormat', jwt_scheme)
        self.assertEqual(jwt_scheme['bearerFormat'], 'JWT')
    
    def test_protected_endpoints_show_auth_requirements(self):
        """Test that protected endpoints indicate authentication requirements."""
        schema = self._get_schema()
        paths = schema['paths']
        
        # Check that protected endpoints have security requirements
        # Most API endpoints should require authentication
        initiatives_list_get = paths['/api/initiatives/']['get']
        
        # Security can be defined at operation level or globally
        # Check if security is defined at operation level
        has_operation_security = 'security' in initiatives_list_get
        
        # Check if security is defined globally
        has_global_security = 'security' in schema
        
        # At least one should be true
        self.assertTrue(
            has_operation_security or has_global_security,
            "Protected endpoints should have security requirements defined"
        )
        
        # If operation-level security exists, verify it references jwtAuth
        if has_operation_security:
            security = initiatives_list_get['security']
            self.assertIsInstance(security, list)
            if len(security) > 0:
                # Check if any security requirement includes jwtAuth
                has_jwt = any('jwtAuth' in req for req in security)
                self.assertTrue(has_jwt, "Security should include jwtAuth")
    
    def test_authentication_description_present(self):
        """Test that JWT authentication has descriptive information."""
        schema = self._get_schema()
        
        security_schemes = schema['components']['securitySchemes']
        jwt_scheme = security_schemes['jwtAuth']
        
        # Verify description is present and informative
        self.assertIn('description', jwt_scheme)
        description = jwt_scheme['description'].lower()
        
        # Description should mention JWT and how to obtain tokens
        self.assertIn('jwt', description)
        self.assertIn('token', description)
    
    def test_global_security_configuration(self):
        """Test that global security configuration is properly set."""
        schema = self._get_schema()
        
        # Check if global security is defined
        if 'security' in schema:
            security = schema['security']
            self.assertIsInstance(security, list)
            
            # Verify jwtAuth is in global security
            if len(security) > 0:
                has_jwt = any('jwtAuth' in req for req in security)
                self.assertTrue(has_jwt, 
                              "Global security should include jwtAuth")
