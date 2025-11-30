from django.test import TestCase
from rest_framework import serializers as drf_serializers
from apps.organizational_group.models import OrganizationalGroup, OrganizationalGroupLeadership
from apps.organizational_group.serializers import (
    OrganizationalGroupLeadershipSerializer,
    OrganizationalGroupSerializer,
    OrganizationalGroupDetailSerializer,
    OrganizationalGroupCreateUpdateSerializer
)
from apps.people.models import Person
from apps.initiatives.models import Initiative, InitiativeType
from datetime import date, timedelta


class OrganizationalGroupLeadershipSerializerTestCase(TestCase):
    """
    Test cases for OrganizationalGroupLeadershipSerializer.
    """
    
    def setUp(self):
        """Set up test data."""
        self.person = Person.objects.create(
            name='Test Leader',
            email='leader@example.com'
        )
        
        self.group = OrganizationalGroup.objects.create(
            name='Test Group',
            short_name='TG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Test Area',
            campus='Test Campus'
        )
        
        self.valid_data = {
            'group': self.group.id,
            'person': self.person.id,
            'start_date': date.today().isoformat(),
            'is_active': True
        }
        
        self.leadership = OrganizationalGroupLeadership.objects.create(
            group=self.group,
            person=self.person,
            start_date=date.today(),
            is_active=True
        )
    
    def test_serialize_group_leadership(self):
        """Test serializing OrganizationalGroupLeadership with person details."""
        serializer = OrganizationalGroupLeadershipSerializer(self.leadership)
        data = serializer.data
        
        self.assertEqual(data['person'], self.person.id)
        self.assertEqual(data['person_name'], 'Test Leader')
        self.assertEqual(data['person_email'], 'leader@example.com')
        self.assertIn('person_details', data)
        self.assertEqual(data['person_details']['name'], 'Test Leader')
        self.assertEqual(data['start_date'], date.today().isoformat())
        self.assertIsNone(data['end_date'])
        self.assertTrue(data['is_active'])
    
    def test_deserialize_group_leadership(self):
        """Test deserializing OrganizationalGroupLeadership."""
        # Use a different person since self.leadership already exists
        person2 = Person.objects.create(
            name='Another Leader',
            email='another@example.com'
        )
        
        data = self.valid_data.copy()
        data['person'] = person2.id
        
        serializer = OrganizationalGroupLeadershipSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        self.assertEqual(instance.person, person2)
        self.assertEqual(instance.group, self.group)
        self.assertEqual(instance.start_date, date.today())
        self.assertTrue(instance.is_active)
    
    def test_person_details_read_only(self):
        """Test that person_name, person_email, and person_details are read-only."""
        # Use a different person since self.leadership already exists
        person2 = Person.objects.create(
            name='Another Leader',
            email='another@example.com'
        )
        
        data = self.valid_data.copy()
        data['person'] = person2.id
        data['person_name'] = 'Should Be Ignored'
        data['person_email'] = 'ignored@example.com'
        data['person_details'] = {'name': 'Ignored'}
        
        serializer = OrganizationalGroupLeadershipSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        # Should use actual person data, not the provided values
        self.assertEqual(instance.person.name, 'Another Leader')
        self.assertEqual(instance.person.email, 'another@example.com')
    
    def test_validate_active_with_end_date(self):
        """Test validation fails when is_active=True but end_date is set."""
        # Use a different person to avoid duplicate active leader validation
        person2 = Person.objects.create(
            name='Another Leader',
            email='another@example.com'
        )
        
        # Create a leadership first to get a start_date
        leadership = OrganizationalGroupLeadership.objects.create(
            group=self.group,
            person=person2,
            start_date=date.today() - timedelta(days=30),
            is_active=False,
            end_date=date.today() - timedelta(days=10)
        )
        
        # Try to update it to be active while having an end_date
        data = {
            'end_date': (date.today() - timedelta(days=10)).isoformat(),
            'is_active': True
        }
        
        serializer = OrganizationalGroupLeadershipSerializer(instance=leadership, data=data, partial=True)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('is_active', serializer.errors)
        self.assertIn('should not be marked as active', str(serializer.errors['is_active']))


class OrganizationalGroupSerializerTestCase(TestCase):
    """
    Test cases for OrganizationalGroupSerializer.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create people
        self.leader = Person.objects.create(
            name='Group Leader',
            email='leader@example.com'
        )
        self.member = Person.objects.create(
            name='Group Member',
            email='member@example.com'
        )
        
        # Create initiative
        self.initiative_type, _ = InitiativeType.objects.get_or_create(
            code='program',
            defaults={'name': 'Program', 'description': 'Program type'}
        )
        self.coordinator = Person.objects.create(
            name='Coordinator',
            email='coordinator@example.com'
        )
        self.initiative = Initiative.objects.create(
            name='Test Initiative',
            description='Test initiative',
            type=self.initiative_type,
            start_date=date.today(),
            coordinator=self.coordinator
        )
        
        # Create group
        self.group = OrganizationalGroup.objects.create(
            name='Research Group Alpha',
            short_name='RGA',
            url='https://example.com/rga',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Computer Science',
            campus='Main Campus'
        )
        
        # Add leader, member, and initiative
        self.group.add_leader(self.leader)
        self.group.members.add(self.member)
        self.group.initiatives.add(self.initiative)
        
        self.valid_data = {
            'name': 'New Group',
            'short_name': 'NG',
            'url': 'https://example.com/ng',
            'type': OrganizationalGroup.TYPE_EXTENSION,
            'knowledge_area': 'Biology',
            'campus': 'North Campus'
        }
    
    def test_serialize_group_with_nested_data(self):
        """Test OrganizationalGroupSerializer serialization with nested data including initiatives."""
        serializer = OrganizationalGroupSerializer(self.group)
        data = serializer.data
        
        # Basic fields
        self.assertEqual(data['name'], 'Research Group Alpha')
        self.assertEqual(data['short_name'], 'RGA')
        self.assertEqual(data['url'], 'https://example.com/rga')
        self.assertEqual(data['type'], 'research')
        self.assertEqual(data['type_display'], 'Research')
        self.assertEqual(data['knowledge_area'], 'Computer Science')
        self.assertEqual(data['campus'], 'Main Campus')
        
        # Counts
        self.assertEqual(data['leader_count'], 1)
        self.assertEqual(data['member_count'], 1)
        self.assertEqual(data['initiative_count'], 1)
        
        # Nested current leaders
        self.assertIn('current_leaders', data)
        self.assertEqual(len(data['current_leaders']), 1)
        self.assertEqual(data['current_leaders'][0]['person_name'], 'Group Leader')
        
        # Nested members
        self.assertIn('members', data)
        self.assertEqual(len(data['members']), 1)
        self.assertEqual(data['members'][0]['name'], 'Group Member')
        
        # Nested initiatives
        self.assertIn('initiatives', data)
        self.assertEqual(len(data['initiatives']), 1)
        self.assertEqual(data['initiatives'][0]['name'], 'Test Initiative')
    
    def test_deserialize_group(self):
        """Test OrganizationalGroupSerializer deserialization and validation."""
        serializer = OrganizationalGroupSerializer(data=self.valid_data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        self.assertEqual(instance.name, 'New Group')
        self.assertEqual(instance.short_name, 'NG')
        self.assertEqual(instance.type, OrganizationalGroup.TYPE_EXTENSION)
        self.assertEqual(instance.knowledge_area, 'Biology')
        self.assertEqual(instance.campus, 'North Campus')
    
    def test_read_only_fields(self):
        """Test read-only field behavior for initiatives and other computed fields."""
        data = self.valid_data.copy()
        data['leader_count'] = 999
        data['member_count'] = 999
        data['initiative_count'] = 999
        data['current_leaders'] = []
        data['members'] = []
        data['initiatives'] = []
        
        serializer = OrganizationalGroupSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        
        # Read-only fields should not be affected
        self.assertEqual(instance.leader_count(), 0)
        self.assertEqual(instance.member_count(), 0)
        self.assertEqual(instance.initiative_count(), 0)
    
    def test_validate_empty_name(self):
        """Test validation error handling for empty name."""
        data = self.valid_data.copy()
        data['name'] = ''
        
        serializer = OrganizationalGroupSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_validate_whitespace_only_name(self):
        """Test validation error handling for whitespace-only name."""
        data = self.valid_data.copy()
        data['name'] = '   '
        
        serializer = OrganizationalGroupSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_validate_empty_short_name(self):
        """Test validation error handling for empty short_name."""
        data = self.valid_data.copy()
        data['short_name'] = ''
        
        serializer = OrganizationalGroupSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('short_name', serializer.errors)
    
    def test_validate_duplicate_short_name_campus(self):
        """Test validation error handling for duplicate short_name + campus."""
        # Create a group
        OrganizationalGroup.objects.create(
            name='Existing Group',
            short_name='EXIST',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Test',
            campus='Test Campus'
        )
        
        # Try to create another with same short_name and campus
        data = {
            'name': 'Different Name',
            'short_name': 'EXIST',
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'Test Campus'
        }
        
        serializer = OrganizationalGroupSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('short_name', serializer.errors)
        self.assertIn('already exists', str(serializer.errors['short_name']))
    
    def test_validate_allows_same_short_name_different_campus(self):
        """Test validation allows same short_name on different campuses."""
        # Create a group
        OrganizationalGroup.objects.create(
            name='Existing Group',
            short_name='EXIST',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Test',
            campus='Campus A'
        )
        
        # Create another with same short_name but different campus
        data = {
            'name': 'Different Group',
            'short_name': 'EXIST',
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'Campus B'
        }
        
        serializer = OrganizationalGroupSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_name_whitespace_cleanup(self):
        """Test that name whitespace is cleaned up."""
        data = self.valid_data.copy()
        data['name'] = '  Test Group  '
        
        serializer = OrganizationalGroupSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.name, 'Test Group')
    
    def test_short_name_whitespace_cleanup(self):
        """Test that short_name whitespace is cleaned up."""
        data = self.valid_data.copy()
        data['short_name'] = '  TEST  '
        
        serializer = OrganizationalGroupSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.short_name, 'TEST')
    
    def test_url_whitespace_cleanup(self):
        """Test that URL whitespace is cleaned up."""
        data = self.valid_data.copy()
        data['url'] = '  https://example.com  '
        
        serializer = OrganizationalGroupSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.url, 'https://example.com')
    
    def test_update_excludes_current_instance(self):
        """Test that update validation excludes current instance."""
        # Update the group with same short_name and campus should be valid
        serializer = OrganizationalGroupSerializer(
            instance=self.group,
            data={'name': 'Updated Name'},
            partial=True
        )
        
        self.assertTrue(serializer.is_valid())
    
    def test_type_display_field(self):
        """Test type_display field shows human-readable type."""
        serializer = OrganizationalGroupSerializer(self.group)
        data = serializer.data
        
        self.assertEqual(data['type'], 'research')
        self.assertEqual(data['type_display'], 'Research')


class OrganizationalGroupDetailSerializerTestCase(TestCase):
    """
    Test cases for OrganizationalGroupDetailSerializer.
    """
    
    def setUp(self):
        """Set up test data."""
        self.leader1 = Person.objects.create(
            name='Leader One',
            email='leader1@example.com'
        )
        self.leader2 = Person.objects.create(
            name='Leader Two',
            email='leader2@example.com'
        )
        
        self.group = OrganizationalGroup.objects.create(
            name='Test Group',
            short_name='TG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Test Area',
            campus='Test Campus'
        )
        
        # Add current leader
        self.group.add_leader(self.leader1)
        
        # Add historical leader
        self.group.add_leader(self.leader2, start_date=date.today() - timedelta(days=60))
        self.group.remove_leader(self.leader2, end_date=date.today() - timedelta(days=30))
    
    def test_detail_serializer_includes_leadership_history(self):
        """Test that detail serializer includes complete leadership history."""
        serializer = OrganizationalGroupDetailSerializer(self.group)
        data = serializer.data
        
        # Should include all GroupSerializer fields
        self.assertIn('name', data)
        self.assertIn('current_leaders', data)
        
        # Should include leadership history
        self.assertIn('leadership_history', data)
        self.assertEqual(len(data['leadership_history']), 2)
        
        # Verify both current and historical leaders are included
        leader_names = [l['person_name'] for l in data['leadership_history']]
        self.assertIn('Leader One', leader_names)
        self.assertIn('Leader Two', leader_names)
    
    def test_leadership_history_ordering(self):
        """Test that leadership history is ordered by start_date descending."""
        serializer = OrganizationalGroupDetailSerializer(self.group)
        data = serializer.data
        
        history = data['leadership_history']
        
        # Most recent should be first
        self.assertEqual(history[0]['person_name'], 'Leader One')
        self.assertEqual(history[1]['person_name'], 'Leader Two')


class OrganizationalGroupCreateUpdateSerializerTestCase(TestCase):
    """
    Test cases for OrganizationalGroupCreateUpdateSerializer.
    """
    
    def setUp(self):
        """Set up test data."""
        self.member1 = Person.objects.create(
            name='Member One',
            email='member1@example.com'
        )
        self.member2 = Person.objects.create(
            name='Member Two',
            email='member2@example.com'
        )
        
        self.initiative_type, _ = InitiativeType.objects.get_or_create(
            code='program',
            defaults={'name': 'Program', 'description': 'Program type'}
        )
        self.coordinator = Person.objects.create(
            name='Coordinator',
            email='coordinator@example.com'
        )
        self.initiative1 = Initiative.objects.create(
            name='Initiative One',
            type=self.initiative_type,
            start_date=date.today(),
            coordinator=self.coordinator
        )
        self.initiative2 = Initiative.objects.create(
            name='Initiative Two',
            type=self.initiative_type,
            start_date=date.today(),
            coordinator=self.coordinator
        )
        
        self.valid_data = {
            'name': 'New Group',
            'short_name': 'NG',
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test Area',
            'campus': 'Test Campus'
        }
    
    def test_create_group_with_members(self):
        """Test creating a group with member_ids."""
        data = self.valid_data.copy()
        data['member_ids'] = [self.member1.id, self.member2.id]
        
        serializer = OrganizationalGroupCreateUpdateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        self.assertEqual(instance.members.count(), 2)
        self.assertIn(self.member1, instance.members.all())
        self.assertIn(self.member2, instance.members.all())
    
    def test_create_group_with_initiatives(self):
        """Test creating a group with initiative_ids."""
        data = self.valid_data.copy()
        data['initiative_ids'] = [self.initiative1.id, self.initiative2.id]
        
        serializer = OrganizationalGroupCreateUpdateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        self.assertEqual(instance.initiatives.count(), 2)
        self.assertIn(self.initiative1, instance.initiatives.all())
        self.assertIn(self.initiative2, instance.initiatives.all())
    
    def test_create_group_with_members_and_initiatives(self):
        """Test creating a group with both member_ids and initiative_ids."""
        data = self.valid_data.copy()
        data['member_ids'] = [self.member1.id]
        data['initiative_ids'] = [self.initiative1.id]
        
        serializer = OrganizationalGroupCreateUpdateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        self.assertEqual(instance.members.count(), 1)
        self.assertEqual(instance.initiatives.count(), 1)
    
    def test_create_group_without_members_or_initiatives(self):
        """Test creating a group without member_ids or initiative_ids."""
        serializer = OrganizationalGroupCreateUpdateSerializer(data=self.valid_data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        self.assertEqual(instance.members.count(), 0)
        self.assertEqual(instance.initiatives.count(), 0)
    
    def test_update_group_members(self):
        """Test updating group members."""
        group = OrganizationalGroup.objects.create(**self.valid_data)
        group.members.add(self.member1)
        
        # Update to different member
        data = {'member_ids': [self.member2.id]}
        
        serializer = OrganizationalGroupCreateUpdateSerializer(
            instance=group,
            data=data,
            partial=True
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        self.assertEqual(instance.members.count(), 1)
        self.assertNotIn(self.member1, instance.members.all())
        self.assertIn(self.member2, instance.members.all())
    
    def test_update_group_initiatives(self):
        """Test updating group initiatives."""
        group = OrganizationalGroup.objects.create(**self.valid_data)
        group.initiatives.add(self.initiative1)
        
        # Update to different initiative
        data = {'initiative_ids': [self.initiative2.id]}
        
        serializer = OrganizationalGroupCreateUpdateSerializer(
            instance=group,
            data=data,
            partial=True
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        self.assertEqual(instance.initiatives.count(), 1)
        self.assertNotIn(self.initiative1, instance.initiatives.all())
        self.assertIn(self.initiative2, instance.initiatives.all())
    
    def test_update_group_clear_members(self):
        """Test clearing group members by passing empty list."""
        group = OrganizationalGroup.objects.create(**self.valid_data)
        group.members.add(self.member1, self.member2)
        
        # Clear members
        data = {'member_ids': []}
        
        serializer = OrganizationalGroupCreateUpdateSerializer(
            instance=group,
            data=data,
            partial=True
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        self.assertEqual(instance.members.count(), 0)
    
    def test_update_group_without_member_ids_preserves_members(self):
        """Test that not providing member_ids preserves existing members."""
        group = OrganizationalGroup.objects.create(**self.valid_data)
        group.members.add(self.member1)
        
        # Update other fields without member_ids
        data = {'name': 'Updated Name'}
        
        serializer = OrganizationalGroupCreateUpdateSerializer(
            instance=group,
            data=data,
            partial=True
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        
        # Members should be preserved
        self.assertEqual(instance.members.count(), 1)
        self.assertIn(self.member1, instance.members.all())
    
    def test_member_ids_write_only(self):
        """Test that member_ids is write-only and not in serialized output."""
        data = self.valid_data.copy()
        data['member_ids'] = [self.member1.id]
        
        serializer = OrganizationalGroupCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        
        # Serialize the instance
        output_serializer = OrganizationalGroupCreateUpdateSerializer(instance)
        output_data = output_serializer.data
        
        # member_ids should not be in output
        self.assertNotIn('member_ids', output_data)
        # But members should be present (from parent serializer)
        self.assertIn('members', output_data)
    
    def test_initiative_ids_write_only(self):
        """Test that initiative_ids is write-only and not in serialized output."""
        data = self.valid_data.copy()
        data['initiative_ids'] = [self.initiative1.id]
        
        serializer = OrganizationalGroupCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        
        # Serialize the instance
        output_serializer = OrganizationalGroupCreateUpdateSerializer(instance)
        output_data = output_serializer.data
        
        # initiative_ids should not be in output
        self.assertNotIn('initiative_ids', output_data)
        # But initiatives should be present (from parent serializer)
        self.assertIn('initiatives', output_data)
