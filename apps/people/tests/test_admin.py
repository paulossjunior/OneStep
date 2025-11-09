from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from apps.people.models import Person
from apps.people.admin import PersonAdmin


class PersonAdminTestCase(TestCase):
    """
    Test cases for Person Django Admin interface.
    """
    
    def setUp(self):
        """Set up test data and admin user."""
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create test person
        self.person = Person.objects.create(
            name='John Doe',
            email='john.doe@example.com',
            phone='+1234567890'
        )
        
        # Set up client and login
        self.client = Client()
        self.client.force_login(self.admin_user)
        
        # Set up admin instance
        self.site = AdminSite()
        self.admin = PersonAdmin(Person, self.site)
    
    def test_admin_list_view(self):
        """Test Person admin list view."""
        url = reverse('admin:people_person_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'john.doe@example.com')
    
    def test_admin_add_view(self):
        """Test Person admin add view."""
        url = reverse('admin:people_person_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name')
        self.assertContains(response, 'email')
        self.assertContains(response, 'phone')
    
    def test_admin_change_view(self):
        """Test Person admin change view."""
        url = reverse('admin:people_person_change', args=[self.person.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'john.doe@example.com')
    
    def test_admin_delete_view(self):
        """Test Person admin delete view."""
        url = reverse('admin:people_person_delete', args=[self.person.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Are you sure')
    
    def test_admin_create_person(self):
        """Test creating a person through admin."""
        url = reverse('admin:people_person_add')
        data = {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'phone': '+0987654321'
        }
        
        response = self.client.post(url, data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Verify person was created
        self.assertTrue(
            Person.objects.filter(email='jane.smith@example.com').exists()
        )
    
    def test_admin_update_person(self):
        """Test updating a person through admin."""
        url = reverse('admin:people_person_change', args=[self.person.id])
        data = {
            'name': 'John Updated',
            'email': 'john.updated@example.com',
            'phone': '+1111111111'
        }
        
        response = self.client.post(url, data)
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        
        # Verify person was updated
        self.person.refresh_from_db()
        self.assertEqual(self.person.name, 'John Updated')
    
    def test_admin_delete_person(self):
        """Test deleting a person through admin."""
        person_id = self.person.id
        url = reverse('admin:people_person_delete', args=[person_id])
        
        # Confirm deletion
        response = self.client.post(url, {'post': 'yes'})
        
        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        
        # Verify person was deleted
        self.assertFalse(Person.objects.filter(id=person_id).exists())
    
    def test_admin_search_functionality(self):
        """Test admin search functionality."""
        # Create additional test data
        Person.objects.create(name='Alice Johnson', email='alice@example.com')
        Person.objects.create(name='Bob Smith', email='bob@example.com')
        
        url = reverse('admin:people_person_changelist')
        
        # Search by name
        response = self.client.get(url, {'q': 'Alice'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Johnson')
        self.assertNotContains(response, 'John Doe')
        
        # Search by email
        response = self.client.get(url, {'q': 'john.doe'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertNotContains(response, 'Alice Johnson')
    
    def test_admin_list_display_methods(self):
        """Test custom admin list display methods."""
        # Test full_name_display
        result = self.admin.full_name_display(self.person)
        self.assertEqual(result, 'John Doe')
        
        # Test phone_display
        result = self.admin.phone_display(self.person)
        self.assertEqual(result, '+1234567890')
        
        # Test phone_display with empty phone
        person_no_phone = Person(name='Test', email='test@example.com', phone='')
        result = self.admin.phone_display(person_no_phone)
        self.assertEqual(result, '-')
        
        # Test coordinated_count_display
        result = self.admin.coordinated_count_display(self.person)
        self.assertIn('None', result)
        
        # Test team_count_display
        result = self.admin.team_count_display(self.person)
        self.assertIn('None', result)
    
    def test_admin_export_action(self):
        """Test the export CSV action."""
        # Create additional test data
        Person.objects.create(name='Alice Johnson', email='alice@example.com')
        
        url = reverse('admin:people_person_changelist')
        data = {
            'action': 'export_selected_people',
            '_selected_action': [self.person.id]
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_admin_validation_errors(self):
        """Test admin form validation errors."""
        url = reverse('admin:people_person_add')
        
        # Submit invalid data
        data = {
            'name': '',  # Empty name
            'email': 'invalid-email'  # Invalid email
        }
        
        response = self.client.post(url, data)
        
        # Should stay on form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
    
    def test_admin_duplicate_email_validation(self):
        """Test admin validation for duplicate emails."""
        url = reverse('admin:people_person_add')
        
        # Try to create person with existing email
        data = {
            'name': 'Another John',
            'email': 'john.doe@example.com'  # Same as existing person
        }
        
        response = self.client.post(url, data)
        
        # Should stay on form with validation error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
    
    def test_admin_queryset_optimization(self):
        """Test that admin queryset is optimized."""
        queryset = self.admin.get_queryset(None)
        
        # Should have annotations for counts
        person = queryset.first()
        self.assertTrue(hasattr(person, 'coordinated_count'))
        self.assertTrue(hasattr(person, 'team_count'))
    
    def test_admin_fieldsets_configuration(self):
        """Test admin fieldsets are properly configured."""
        fieldsets = self.admin.fieldsets
        
        # Should have Personal Information section
        personal_info = fieldsets[0]
        self.assertEqual(personal_info[0], 'Personal Information')
        self.assertIn('name', personal_info[1]['fields'])
        self.assertIn('email', personal_info[1]['fields'])
        
        # Should have Statistics section
        statistics = fieldsets[1]
        self.assertEqual(statistics[0], 'Statistics')
        self.assertIn('collapse', statistics[1]['classes'])
    
    def test_admin_readonly_fields(self):
        """Test that readonly fields are properly configured."""
        readonly_fields = self.admin.readonly_fields
        
        self.assertIn('id', readonly_fields)
        self.assertIn('created_at', readonly_fields)
        self.assertIn('updated_at', readonly_fields)
        self.assertIn('full_name', readonly_fields)