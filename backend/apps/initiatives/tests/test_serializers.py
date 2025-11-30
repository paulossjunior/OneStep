from django.test import TestCase
from rest_framework.test import APITestCase
from apps.initiatives.models import Initiative, InitiativeType
from apps.initiatives.serializers import (
    InitiativeTypeSerializer,
    InitiativeSerializer,
    InitiativeDetailSerializer,
    InitiativeCreateUpdateSerializer
)
from apps.people.models import Person
import datetime


class InitiativeTypeSerializerTest(TestCase):
    """
    Test cases for InitiativeTypeSerializer.
    """
    
    def setUp(self):
        """Set up test data."""
        self.type_data = {
            'name': 'Test Type',
            'code': 'test',
            'description': 'A test initiative type',
            'is_active': True
        }
        self.initiative_type = InitiativeType.objects.create(**self.type_data)
    
    def test_serialize_initiative_type(self):
        """Test serializing InitiativeType."""
        serializer = InitiativeTypeSerializer(self.initiative_type)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Type')
        self.assertEqual(data['code'], 'test')
        self.assertEqual(data['description'], 'A test initiative type')
        self.assertTrue(data['is_active'])
    
    def test_deserialize_initiative_type(self):
        """Test deserializing InitiativeType."""
        data = {
            'name': 'New Type',
            'code': 'new',
            'description': 'A new type',
            'is_active': True
        }
        serializer = InitiativeTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        instance = serializer.save()
        self.assertEqual(instance.name, 'New Type')
        self.assertEqual(instance.code, 'new')


class InitiativeSerializerTest(TestCase):
    """
    Test cases for Initiative serializers.
    """
    
    def setUp(self):
        """Set up test data."""
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
        
        # Create initiative
        self.initiative = Initiative.objects.create(
            name='Test Initiative',
            description='A test initiative',
            type=self.program_type,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=30),
            coordinator=self.coordinator
        )
        self.initiative.team_members.add(self.team_member)
    
    def test_serialize_initiative(self):
        """Test serializing Initiative with basic serializer."""
        serializer = InitiativeSerializer(self.initiative)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Initiative')
        self.assertEqual(data['type_name'], 'Program')
        self.assertEqual(data['type_code'], 'program')
        self.assertEqual(data['coordinator_name'], 'John Coordinator')
        self.assertEqual(data['team_count'], 1)
        self.assertEqual(data['children_count'], 0)
        self.assertEqual(data['hierarchy_level'], 0)
    
    def test_serialize_initiative_detail(self):
        """Test serializing Initiative with detail serializer."""
        serializer = InitiativeDetailSerializer(self.initiative)
        data = serializer.data
        
        # Check nested type data
        self.assertIn('type', data)
        self.assertEqual(data['type']['name'], 'Program')
        self.assertEqual(data['type']['code'], 'program')
        
        # Check nested coordinator data
        self.assertIn('coordinator', data)
        self.assertEqual(data['coordinator']['name'], 'John Coordinator')
        
        # Check nested team members
        self.assertIn('team_members', data)
        self.assertEqual(len(data['team_members']), 1)
        self.assertEqual(data['team_members'][0]['name'], 'Jane Member')
    
    def test_deserialize_initiative(self):
        """Test deserializing Initiative."""
        data = {
            'name': 'New Initiative',
            'description': 'A new initiative',
            'type': self.project_type.id,
            'start_date': datetime.date.today().isoformat(),
            'coordinator': self.coordinator.id
        }
        
        serializer = InitiativeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        instance = serializer.save()
        self.assertEqual(instance.name, 'New Initiative')
        self.assertEqual(instance.type, self.project_type)
        self.assertEqual(instance.coordinator, self.coordinator)
    
    def test_validate_date_logic(self):
        """Test date validation in serializer."""
        data = {
            'name': 'Invalid Initiative',
            'type': self.project_type.id,
            'start_date': datetime.date.today().isoformat(),
            'end_date': (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
            'coordinator': self.coordinator.id
        }
        
        serializer = InitiativeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)
    
    def test_validate_inactive_type(self):
        """Test validation of inactive initiative type."""
        inactive_type = InitiativeType.objects.create(
            name='Inactive Type',
            code='inactive',
            is_active=False
        )
        
        data = {
            'name': 'Test Initiative',
            'type': inactive_type.id,
            'start_date': datetime.date.today().isoformat(),
            'coordinator': self.coordinator.id
        }
        
        serializer = InitiativeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('type', serializer.errors)
    
    def test_create_update_serializer_with_team_members(self):
        """Test InitiativeCreateUpdateSerializer with team member IDs."""
        data = {
            'name': 'Team Initiative',
            'description': 'Initiative with team',
            'type': self.project_type.id,
            'start_date': datetime.date.today().isoformat(),
            'coordinator': self.coordinator.id,
            'team_member_ids': [self.team_member.id]
        }
        
        serializer = InitiativeCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        instance = serializer.save()
        self.assertEqual(instance.team_members.count(), 1)
        self.assertIn(self.team_member, instance.team_members.all())
    
    def test_update_initiative_team_members(self):
        """Test updating initiative team members."""
        new_member = Person.objects.create(
            name='New Member',
            email='new@example.com'
        )
        
        data = {
            'team_member_ids': [new_member.id]
        }
        
        serializer = InitiativeCreateUpdateSerializer(
            self.initiative, 
            data=data, 
            partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        instance = serializer.save()
        self.assertEqual(instance.team_members.count(), 1)
        self.assertIn(new_member, instance.team_members.all())
        self.assertNotIn(self.team_member, instance.team_members.all())
    
    def test_parent_info_serialization(self):
        """Test parent information serialization."""
        # Create parent initiative
        parent = Initiative.objects.create(
            name='Parent Initiative',
            type=self.program_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator
        )
        
        # Create child initiative
        child = Initiative.objects.create(
            name='Child Initiative',
            type=self.project_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator,
            parent=parent
        )
        
        serializer = InitiativeSerializer(child)
        data = serializer.data
        
        self.assertIn('parent_info', data)
        self.assertEqual(data['parent_info']['name'], 'Parent Initiative')
        self.assertEqual(data['parent_info']['type_name'], 'Program')
        self.assertEqual(data['parent_info']['type_code'], 'program')
    
    def test_children_serialization_in_detail(self):
        """Test children serialization in detail serializer."""
        # Create child initiative
        child = Initiative.objects.create(
            name='Child Initiative',
            type=self.project_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator,
            parent=self.initiative
        )
        
        serializer = InitiativeDetailSerializer(self.initiative)
        data = serializer.data
        
        self.assertIn('children', data)
        self.assertEqual(len(data['children']), 1)
        self.assertEqual(data['children'][0]['name'], 'Child Initiative')