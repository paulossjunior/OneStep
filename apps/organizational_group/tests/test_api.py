from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.organizational_group.models import OrganizationalGroup, OrganizationalGroupLeadership
from apps.people.models import Person
from apps.initiatives.models import Initiative, InitiativeType
import datetime


class GroupAPITest(APITestCase):
    """
    Test cases for Group API endpoints.
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
        
        # Create people
        self.leader1 = Person.objects.create(
            name='John Leader',
            email='john@example.com'
        )
        self.leader2 = Person.objects.create(
            name='Jane Leader',
            email='jane@example.com'
        )
        self.member1 = Person.objects.create(
            name='Bob Member',
            email='bob@example.com'
        )
        self.member2 = Person.objects.create(
            name='Alice Member',
            email='alice@example.com'
        )
        
        # Create initiative type and initiative
        self.program_type, _ = InitiativeType.objects.get_or_create(
            code='program',
            defaults={'name': 'Program', 'description': 'Program type'}
        )
        self.initiative = Initiative.objects.create(
            name='Test Initiative',
            description='A test initiative',
            type=self.program_type,
            start_date=datetime.date.today(),
            coordinator=self.leader1
        )
        
        # Create test group
        self.group = OrganizationalGroup.objects.create(
            name='Test Research Group',
            short_name='TRG',
            url='https://example.com/trg',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Computer Science',
            campus='Main Campus'
        )
        
        # Add leader
        OrganizationalGroupLeadership.objects.create(
            group=self.group,
            person=self.leader1,
            start_date=datetime.date.today(),
            is_active=True
        )
        
        # Add members
        self.group.members.add(self.member1)
        
        # Add initiative
        self.group.initiatives.add(self.initiative)
    
    def test_list_groups(self):
        """Test listing groups."""
        url = reverse('v1:group-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Research Group')
    
    def test_retrieve_group(self):
        """Test retrieving a specific group."""
        url = reverse('v1:group-detail', kwargs={'pk': self.group.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Research Group')
        self.assertEqual(response.data['short_name'], 'TRG')
        self.assertEqual(response.data['type'], OrganizationalGroup.TYPE_RESEARCH)
        
        # Check nested data
        self.assertIn('current_leaders', response.data)
        self.assertEqual(len(response.data['current_leaders']), 1)
        self.assertEqual(response.data['current_leaders'][0]['person_name'], 'John Leader')
        
        self.assertIn('members', response.data)
        self.assertEqual(len(response.data['members']), 1)
        
        self.assertIn('initiatives', response.data)
        self.assertEqual(len(response.data['initiatives']), 1)
        
        # Check counts
        self.assertEqual(response.data['leader_count'], 1)
        self.assertEqual(response.data['member_count'], 1)
        self.assertEqual(response.data['initiative_count'], 1)
        
        # Check leadership history in detail view
        self.assertIn('leadership_history', response.data)
        self.assertEqual(len(response.data['leadership_history']), 1)
    
    def test_create_group(self):
        """Test creating a new group."""
        url = reverse('v1:group-list')
        data = {
            'name': 'New Extension Group',
            'short_name': 'NEG',
            'url': 'https://example.com/neg',
            'type': OrganizationalGroup.TYPE_EXTENSION,
            'knowledge_area': 'Agriculture',
            'campus': 'North Campus',
            'member_ids': [self.member2.id],
            'initiative_ids': [self.initiative.id]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Extension Group')
        self.assertEqual(response.data['type'], OrganizationalGroup.TYPE_EXTENSION)
        
        # Verify group was created in database
        group = OrganizationalGroup.objects.get(name='New Extension Group')
        self.assertEqual(group.type, OrganizationalGroup.TYPE_EXTENSION)
        self.assertEqual(group.members.count(), 1)
        self.assertEqual(group.initiatives.count(), 1)
    
    def test_update_group(self):
        """Test updating a group."""
        url = reverse('v1:group-detail', kwargs={'pk': self.group.pk})
        data = {
            'name': 'Updated Research Group',
            'knowledge_area': 'Data Science',
            'member_ids': [self.member1.id, self.member2.id]
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Research Group')
        
        # Verify changes in database
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Updated Research Group')
        self.assertEqual(self.group.knowledge_area, 'Data Science')
        self.assertEqual(self.group.members.count(), 2)
    
    def test_delete_group(self):
        """Test deleting a group."""
        url = reverse('v1:group-detail', kwargs={'pk': self.group.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(OrganizationalGroup.objects.filter(pk=self.group.pk).exists())
    
    def test_filter_groups_by_type(self):
        """Test filtering groups by type."""
        # Create another group with different type
        OrganizationalGroup.objects.create(
            name='Extension Group',
            short_name='EG',
            type=OrganizationalGroup.TYPE_EXTENSION,
            knowledge_area='Agriculture',
            campus='Main Campus'
        )
        
        url = reverse('v1:group-list')
        response = self.client.get(url, {'type': OrganizationalGroup.TYPE_EXTENSION})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Extension Group')
    
    def test_filter_groups_by_campus(self):
        """Test filtering groups by campus."""
        # Create another group on different campus
        OrganizationalGroup.objects.create(
            name='North Campus Group',
            short_name='NCG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Biology',
            campus='North Campus'
        )
        
        url = reverse('v1:group-list')
        response = self.client.get(url, {'campus': 'North Campus'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'North Campus Group')
    
    def test_filter_groups_by_knowledge_area(self):
        """Test filtering groups by knowledge_area."""
        # Create another group with different knowledge area
        OrganizationalGroup.objects.create(
            name='Biology Group',
            short_name='BG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Biology',
            campus='Main Campus'
        )
        
        url = reverse('v1:group-list')
        response = self.client.get(url, {'knowledge_area': 'Biology'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Biology Group')
    
    def test_search_groups_by_name(self):
        """Test searching groups by name."""
        url = reverse('v1:group-list')
        response = self.client.get(url, {'search': 'Research'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Research Group')
    
    def test_search_groups_by_short_name(self):
        """Test searching groups by short_name."""
        url = reverse('v1:group-list')
        response = self.client.get(url, {'search': 'TRG'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['short_name'], 'TRG')
    
    def test_get_current_leaders(self):
        """Test custom action: current_leaders."""
        url = reverse('v1:group-current-leaders', kwargs={'pk': self.group.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['group_id'], self.group.id)
        self.assertEqual(response.data['group_name'], 'Test Research Group')
        self.assertEqual(len(response.data['current_leaders']), 1)
        self.assertEqual(response.data['current_leaders'][0]['person_name'], 'John Leader')
        self.assertEqual(response.data['leader_count'], 1)
    
    def test_add_leader(self):
        """Test custom action: add_leader."""
        url = reverse('v1:group-add-leader', kwargs={'pk': self.group.pk})
        data = {
            'person_id': self.leader2.id,
            'start_date': datetime.date.today().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('added as leader', response.data['message'])
        self.assertEqual(response.data['leader_count'], 2)
        
        # Verify in database
        leadership = OrganizationalGroupLeadership.objects.get(
            group=self.group,
            person=self.leader2,
            is_active=True
        )
        self.assertIsNotNone(leadership)
    
    def test_add_leader_missing_person_id(self):
        """Test add_leader with missing person_id."""
        url = reverse('v1:group-add-leader', kwargs={'pk': self.group.pk})
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'MISSING_PERSON_ID')
    
    def test_add_leader_person_not_found(self):
        """Test add_leader with non-existent person."""
        url = reverse('v1:group-add-leader', kwargs={'pk': self.group.pk})
        data = {'person_id': 99999}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'PERSON_NOT_FOUND')
    
    def test_add_leader_duplicate_active(self):
        """Test add_leader with person who is already an active leader."""
        url = reverse('v1:group-add-leader', kwargs={'pk': self.group.pk})
        data = {'person_id': self.leader1.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'VALIDATION_ERROR')
    
    def test_remove_leader(self):
        """Test custom action: remove_leader."""
        url = reverse('v1:group-remove-leader', kwargs={'pk': self.group.pk})
        data = {
            'person_id': self.leader1.id,
            'end_date': datetime.date.today().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('removed as leader', response.data['message'])
        self.assertEqual(response.data['leader_count'], 0)
        
        # Verify in database
        leadership = OrganizationalGroupLeadership.objects.get(
            group=self.group,
            person=self.leader1
        )
        self.assertFalse(leadership.is_active)
        self.assertIsNotNone(leadership.end_date)
    
    def test_remove_leader_missing_person_id(self):
        """Test remove_leader with missing person_id."""
        url = reverse('v1:group-remove-leader', kwargs={'pk': self.group.pk})
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'MISSING_PERSON_ID')
    
    def test_remove_leader_person_not_found(self):
        """Test remove_leader with non-existent person."""
        url = reverse('v1:group-remove-leader', kwargs={'pk': self.group.pk})
        data = {'person_id': 99999}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'PERSON_NOT_FOUND')
    
    def test_remove_leader_not_active(self):
        """Test remove_leader with person who is not an active leader."""
        url = reverse('v1:group-remove-leader', kwargs={'pk': self.group.pk})
        data = {'person_id': self.leader2.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'VALIDATION_ERROR')
    
    def test_get_leadership_history(self):
        """Test custom action: leadership_history."""
        # Add and remove a leader to create history
        leadership2 = OrganizationalGroupLeadership.objects.create(
            group=self.group,
            person=self.leader2,
            start_date=datetime.date.today() - datetime.timedelta(days=365),
            end_date=datetime.date.today() - datetime.timedelta(days=30),
            is_active=False
        )
        
        url = reverse('v1:group-leadership-history', kwargs={'pk': self.group.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['group_id'], self.group.id)
        self.assertEqual(response.data['group_name'], 'Test Research Group')
        
        # Check current leaders
        self.assertEqual(len(response.data['current_leaders']), 1)
        self.assertEqual(response.data['current_leaders'][0]['person_name'], 'John Leader')
        
        # Check historical leaders
        self.assertEqual(len(response.data['historical_leaders']), 1)
        self.assertEqual(response.data['historical_leaders'][0]['person_name'], 'Jane Leader')
        
        # Check counts
        self.assertEqual(response.data['total_current'], 1)
        self.assertEqual(response.data['total_historical'], 1)
        self.assertEqual(response.data['total_all_time'], 2)
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        self.client.force_authenticate(user=None)
        
        url = reverse('v1:group-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_group_validation_errors(self):
        """Test validation errors when creating group."""
        url = reverse('v1:group-list')
        
        # Test missing required fields
        data = {'name': 'Incomplete Group'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_group_empty_name(self):
        """Test creating group with empty name."""
        url = reverse('v1:group-list')
        data = {
            'name': '   ',
            'short_name': 'EG',
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'Main Campus'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_group_invalid_url(self):
        """Test creating group with invalid URL."""
        url = reverse('v1:group-list')
        data = {
            'name': 'Test Group',
            'short_name': 'TG',
            'url': 'not-a-valid-url',
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'Main Campus'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_group_duplicate_short_name_campus(self):
        """Test creating group with duplicate short_name + campus combination."""
        url = reverse('v1:group-list')
        data = {
            'name': 'Another Research Group',
            'short_name': 'TRG',  # Same as existing group
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'Main Campus'  # Same as existing group
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_group_same_short_name_different_campus(self):
        """Test creating group with same short_name but different campus (should succeed)."""
        url = reverse('v1:group-list')
        data = {
            'name': 'Another Research Group',
            'short_name': 'TRG',  # Same as existing group
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'North Campus'  # Different campus
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['short_name'], 'TRG')
        self.assertEqual(response.data['campus'], 'North Campus')
