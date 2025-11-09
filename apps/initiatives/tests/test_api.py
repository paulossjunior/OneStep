from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.initiatives.models import Initiative, InitiativeType
from apps.people.models import Person
import datetime
import json


class InitiativeAPITest(APITestCase):
    """
    Test cases for Initiative API endpoints.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create initiative types (use get_or_create to avoid conflicts with migration data)
        self.program_type, _ = InitiativeType.objects.get_or_create(
            code='program',
            defaults={'name': 'Program', 'description': 'Program type'}
        )
        self.project_type, _ = InitiativeType.objects.get_or_create(
            code='project',
            defaults={'name': 'Project', 'description': 'Project type'}
        )
        
        # Create people
        self.coordinator = Person.objects.create(
            name='John Coordinator',
            email='john@example.com'
        )
        self.team_member = Person.objects.create(
            name='Jane Member',
            email='jane@example.com'
        )
        
        # Create test initiative
        self.initiative = Initiative.objects.create(
            name='Test Initiative',
            description='A test initiative',
            type=self.program_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator
        )
        self.initiative.team_members.add(self.team_member)
    
    def test_list_initiatives(self):
        """Test listing initiatives."""
        url = reverse('initiative-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Initiative')
    
    def test_retrieve_initiative(self):
        """Test retrieving a specific initiative."""
        url = reverse('initiative-detail', kwargs={'pk': self.initiative.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Initiative')
        
        # Check nested data in detail view
        self.assertIn('type', response.data)
        self.assertEqual(response.data['type']['name'], 'Program')
        
        self.assertIn('coordinator', response.data)
        self.assertEqual(response.data['coordinator']['name'], 'John Coordinator')
        
        self.assertIn('team_members', response.data)
        self.assertEqual(len(response.data['team_members']), 1)
    
    def test_create_initiative(self):
        """Test creating a new initiative."""
        url = reverse('initiative-list')
        data = {
            'name': 'New Initiative',
            'description': 'A new test initiative',
            'type': self.project_type.id,
            'start_date': datetime.date.today().isoformat(),
            'coordinator': self.coordinator.id,
            'team_member_ids': [self.team_member.id]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Initiative')
        self.assertEqual(response.data['type_name'], 'Project')
        
        # Verify initiative was created in database
        initiative = Initiative.objects.get(name='New Initiative')
        self.assertEqual(initiative.type, self.project_type)
        self.assertEqual(initiative.team_members.count(), 1)
    
    def test_update_initiative(self):
        """Test updating an initiative."""
        url = reverse('initiative-detail', kwargs={'pk': self.initiative.pk})
        data = {
            'name': 'Updated Initiative',
            'description': 'Updated description',
            'team_member_ids': []  # Remove team members
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Initiative')
        
        # Verify changes in database
        self.initiative.refresh_from_db()
        self.assertEqual(self.initiative.name, 'Updated Initiative')
        self.assertEqual(self.initiative.team_members.count(), 0)
    
    def test_delete_initiative(self):
        """Test deleting an initiative."""
        url = reverse('initiative-detail', kwargs={'pk': self.initiative.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Initiative.objects.filter(pk=self.initiative.pk).exists())
    
    def test_delete_initiative_with_children_warning(self):
        """Test deleting initiative with children shows warning."""
        # Create child initiative
        child = Initiative.objects.create(
            name='Child Initiative',
            type=self.project_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator,
            parent=self.initiative
        )
        
        url = reverse('initiative-detail', kwargs={'pk': self.initiative.pk})
        response = self.client.delete(url)
        
        # Should return warning instead of deleting
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('warning', response.data)
        self.assertIn('CASCADE_DELETION', response.data['warning']['code'])
        
        # Initiative should still exist
        self.assertTrue(Initiative.objects.filter(pk=self.initiative.pk).exists())
    
    def test_force_delete_initiative(self):
        """Test force deleting initiative with children."""
        # Create child initiative
        child = Initiative.objects.create(
            name='Child Initiative',
            type=self.project_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator,
            parent=self.initiative
        )
        
        url = reverse('initiative-force-delete', kwargs={'pk': self.initiative.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Initiative.objects.filter(pk=self.initiative.pk).exists())
        self.assertFalse(Initiative.objects.filter(pk=child.pk).exists())
    
    def test_get_initiative_hierarchy(self):
        """Test getting initiative hierarchy."""
        # Create parent
        parent = Initiative.objects.create(
            name='Parent Initiative',
            type=self.program_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator
        )
        
        # Update current initiative to be child of parent
        self.initiative.parent = parent
        self.initiative.save()
        
        # Create grandchild
        grandchild = Initiative.objects.create(
            name='Grandchild Initiative',
            type=self.project_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator,
            parent=self.initiative
        )
        
        url = reverse('initiative-hierarchy', kwargs={'pk': self.initiative.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check ancestors
        self.assertEqual(len(response.data['ancestors']), 1)
        self.assertEqual(response.data['ancestors'][0]['name'], 'Parent Initiative')
        
        # Check descendants
        self.assertEqual(len(response.data['descendants']), 1)
        self.assertEqual(response.data['descendants'][0]['name'], 'Grandchild Initiative')
    
    def test_add_team_member(self):
        """Test adding team member to initiative."""
        new_member = Person.objects.create(
            name='New Member',
            email='new@example.com'
        )
        
        url = reverse('initiative-add-team-member', kwargs={'pk': self.initiative.pk})
        data = {'person_id': new_member.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('added as team member', response.data['message'])
        
        # Verify in database
        self.assertIn(new_member, self.initiative.team_members.all())
    
    def test_remove_team_member(self):
        """Test removing team member from initiative."""
        url = reverse('initiative-remove-team-member', kwargs={'pk': self.initiative.pk})
        data = {'person_id': self.team_member.id}
        
        response = self.client.delete(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('removed from team', response.data['message'])
        
        # Verify in database
        self.assertNotIn(self.team_member, self.initiative.team_members.all())
    
    def test_get_initiative_types(self):
        """Test getting available initiative types."""
        url = reverse('initiative-types')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('types', response.data)
        self.assertEqual(len(response.data['types']), 2)
        
        # Check type data
        type_names = [t['name'] for t in response.data['types']]
        self.assertIn('Program', type_names)
        self.assertIn('Project', type_names)
    
    def test_search_initiatives(self):
        """Test searching initiatives."""
        url = reverse('initiative-search')
        response = self.client.get(url, {'q': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Initiative')
    
    def test_filter_initiatives_by_type(self):
        """Test filtering initiatives by type."""
        # Create another initiative with different type
        Initiative.objects.create(
            name='Project Initiative',
            type=self.project_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator
        )
        
        url = reverse('initiative-list')
        response = self.client.get(url, {'type': self.project_type.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Project Initiative')
    
    def test_filter_initiatives_by_coordinator(self):
        """Test filtering initiatives by coordinator."""
        url = reverse('initiative-list')
        response = self.client.get(url, {'coordinator': self.coordinator.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['coordinator_name'], 'John Coordinator')
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        self.client.force_authenticate(user=None)
        
        url = reverse('initiative-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_initiative_validation_errors(self):
        """Test validation errors when creating initiative."""
        url = reverse('initiative-list')
        
        # Test missing required fields
        data = {'name': 'Incomplete Initiative'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        # Test invalid date range
        data = {
            'name': 'Invalid Initiative',
            'type': self.project_type.id,
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
            'coordinator': self.coordinator.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)