from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from apps.people.models import Person


class PersonAPITestCase(APITestCase):
    """
    Test cases for Person API endpoints.
    """
    
    def setUp(self):
        """Set up test data and authentication."""
        # Create test user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test person
        self.person = Person.objects.create(
            name='John Doe',
            email='john.doe@example.com'
        )
        
        # Set up API client with authentication
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # API endpoints
        self.list_url = '/api/people/'
        self.detail_url = f'/api/people/{self.person.id}/'
    
    def test_list_people_authenticated(self):
        """Test listing people with authentication."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        
        person_data = response.data['results'][0]
        self.assertEqual(person_data['name'], 'John Doe')
        self.assertEqual(person_data['email'], 'john.doe@example.com')
    
    def test_list_people_unauthenticated(self):
        """Test listing people without authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_person_valid_data(self):
        """Test creating a person with valid data."""
        data = {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com'
        }
        
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Jane Smith')
        self.assertEqual(response.data['email'], 'jane.smith@example.com')
        
        # Verify person was created in database
        self.assertTrue(
            Person.objects.filter(email='jane.smith@example.com').exists()
        )
    
    def test_create_person_invalid_data(self):
        """Test creating a person with invalid data."""
        data = {
            'name': '',  # Empty name
            'email': 'invalid-email'  # Invalid email format
        }
        
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('email', response.data)
    
    def test_create_person_duplicate_email(self):
        """Test creating a person with duplicate email."""
        data = {
            'name': 'Another John',
            'email': 'john.doe@example.com'  # Same as existing person
        }
        
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_retrieve_person(self):
        """Test retrieving a specific person."""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['email'], 'john.doe@example.com')
        
        # Detail view should include additional fields
        self.assertIn('coordinated_initiatives', response.data)
        self.assertIn('team_initiatives', response.data)
    
    def test_retrieve_person_not_found(self):
        """Test retrieving a non-existent person."""
        response = self.client.get('/api/people/999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_person_full(self):
        """Test full update of a person."""
        data = {
            'name': 'John Updated',
            'email': 'john.updated@example.com'
        }
        
        response = self.client.put(self.detail_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Updated')
        self.assertEqual(response.data['email'], 'john.updated@example.com')
        
        # Verify update in database
        self.person.refresh_from_db()
        self.assertEqual(self.person.name, 'John Updated')
    
    def test_update_person_partial(self):
        """Test partial update of a person."""
        data = {'name': 'John Partially Updated'}
        
        response = self.client.patch(self.detail_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Partially Updated')
        self.assertEqual(response.data['email'], 'john.doe@example.com')  # Unchanged
    
    def test_update_person_invalid_data(self):
        """Test updating person with invalid data."""
        data = {'name': ''}  # Empty name
        
        response = self.client.patch(self.detail_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_delete_person(self):
        """Test deleting a person."""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify person was deleted
        self.assertFalse(
            Person.objects.filter(id=self.person.id).exists()
        )
    
    def test_search_people(self):
        """Test searching people."""
        # Create additional test data
        Person.objects.create(name='Alice Johnson', email='alice@example.com')
        Person.objects.create(name='Bob Smith', email='bob@example.com')
        
        # Search by name
        response = self.client.get(self.list_url, {'search': 'Alice'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Alice Johnson')
    
    def test_filter_people_by_name(self):
        """Test filtering people by name."""
        # Create additional test data
        Person.objects.create(name='Alice Johnson', email='alice@example.com')
        
        response = self.client.get(self.list_url, {'name': 'Alice'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Alice Johnson')
    
    def test_filter_people_by_email(self):
        """Test filtering people by email."""
        response = self.client.get(self.list_url, {'email': 'john.doe'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'john.doe@example.com')
    
    def test_ordering_people(self):
        """Test ordering people by different fields."""
        # Create additional test data
        Person.objects.create(name='Alice Johnson', email='alice@example.com')
        Person.objects.create(name='Zoe Wilson', email='zoe@example.com')
        
        # Order by name
        response = self.client.get(self.list_url, {'ordering': 'name'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [person['name'] for person in response.data['results']]
        self.assertEqual(names, ['Alice Johnson', 'John Doe', 'Zoe Wilson'])
        
        # Order by name descending
        response = self.client.get(self.list_url, {'ordering': '-name'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [person['name'] for person in response.data['results']]
        self.assertEqual(names, ['Zoe Wilson', 'John Doe', 'Alice Johnson'])
    
    def test_pagination(self):
        """Test API pagination."""
        # Create many people to test pagination
        for i in range(15):
            Person.objects.create(
                name=f'Person {i}',
                email=f'person{i}@example.com'
            )
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
    
    def test_initiatives_endpoint(self):
        """Test the custom initiatives endpoint."""
        url = f'/api/people/{self.person.id}/initiatives/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('coordinated_initiatives', response.data)
        self.assertIn('team_initiatives', response.data)
        self.assertIn('total_coordinated', response.data)
        self.assertIn('total_team_member', response.data)
    
    def test_search_endpoint(self):
        """Test the custom search endpoint."""
        url = '/api/people/search/'
        
        # Search with query
        response = self.client.get(url, {'q': 'John'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('query', response.data)
        
        # Search without query
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)