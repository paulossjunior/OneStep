from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import serializers
from apps.people.models import Person
from apps.people.serializers import PersonSerializer, PersonDetailSerializer


class PersonSerializerTestCase(TestCase):
    """
    Test cases for Person serializers.
    """
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890'
        }
        
        self.person = Person.objects.create(**self.valid_data)
    
    def test_person_serializer_valid_data(self):
        """Test PersonSerializer with valid data."""
        serializer = PersonSerializer(data=self.valid_data)
        
        self.assertTrue(serializer.is_valid())
        person = serializer.save()
        
        self.assertEqual(person.name, 'John Doe')
        self.assertEqual(person.email, 'john.doe@example.com')
        self.assertEqual(person.phone, '+1234567890')
    
    def test_person_serializer_serialization(self):
        """Test PersonSerializer serialization of existing object."""
        serializer = PersonSerializer(self.person)
        data = serializer.data
        
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['email'], 'john.doe@example.com')
        self.assertEqual(data['phone'], '+1234567890')
        self.assertEqual(data['full_name'], 'John Doe')
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_person_serializer_computed_fields(self):
        """Test computed fields in PersonSerializer."""
        serializer = PersonSerializer(self.person)
        data = serializer.data
        
        self.assertEqual(data['coordinated_count'], 0)
        self.assertEqual(data['team_count'], 0)
        self.assertEqual(data['full_name'], 'John Doe')
    
    def test_name_validation_empty(self):
        """Test name validation for empty values."""
        invalid_data = self.valid_data.copy()
        invalid_data['name'] = ''
        
        serializer = PersonSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('Name cannot be empty', str(serializer.errors['name']))
    
    def test_name_validation_whitespace(self):
        """Test name validation for whitespace-only values."""
        invalid_data = self.valid_data.copy()
        invalid_data['name'] = '   '
        
        serializer = PersonSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_name_whitespace_cleanup(self):
        """Test that name whitespace is cleaned up."""
        data = self.valid_data.copy()
        data['name'] = '  John Doe  '
        
        serializer = PersonSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        person = serializer.save()
        self.assertEqual(person.name, 'John Doe')
    
    def test_email_validation_duplicate(self):
        """Test email validation for duplicate emails."""
        # Create a person with the email
        Person.objects.create(
            name='Existing Person',
            email='existing@example.com'
        )
        
        # Try to create another with same email
        invalid_data = {
            'name': 'New Person',
            'email': 'existing@example.com'
        }
        
        serializer = PersonSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('already exists', str(serializer.errors['email']))
    
    def test_email_validation_case_insensitive(self):
        """Test email validation is case-insensitive."""
        # Create a person with lowercase email
        Person.objects.create(
            name='Existing Person',
            email='existing@example.com'
        )
        
        # Try to create another with uppercase email
        invalid_data = {
            'name': 'New Person',
            'email': 'EXISTING@EXAMPLE.COM'
        }
        
        serializer = PersonSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_email_normalization(self):
        """Test that email is normalized to lowercase."""
        data = self.valid_data.copy()
        data['email'] = 'JOHN@EXAMPLE.COM'
        
        serializer = PersonSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        person = serializer.save()
        self.assertEqual(person.email, 'john@example.com')
    
    def test_phone_validation_optional(self):
        """Test that phone field is optional."""
        data = self.valid_data.copy()
        del data['phone']  # Remove phone
        
        serializer = PersonSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        person = serializer.save()
        self.assertEqual(person.phone, '')
    
    def test_phone_whitespace_cleanup(self):
        """Test that phone whitespace is cleaned up."""
        data = self.valid_data.copy()
        data['phone'] = '  +1234567890  '
        
        serializer = PersonSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        person = serializer.save()
        self.assertEqual(person.phone, '+1234567890')
    
    def test_update_serializer_excludes_current_instance(self):
        """Test that update validation excludes current instance."""
        # Update the person with same email should be valid
        serializer = PersonSerializer(
            instance=self.person,
            data={'email': self.person.email, 'name': 'Updated Name'},
            partial=True
        )
        
        self.assertTrue(serializer.is_valid())
    
    def test_read_only_fields(self):
        """Test that read-only fields are not updated."""
        update_data = {
            'name': 'Updated Name',
            'id': 999,  # Should be ignored
            'created_at': '2020-01-01T00:00:00Z',  # Should be ignored
            'full_name': 'Should Be Ignored'  # Should be ignored
        }
        
        serializer = PersonSerializer(
            instance=self.person,
            data=update_data,
            partial=True
        )
        
        self.assertTrue(serializer.is_valid())
        updated_person = serializer.save()
        
        self.assertEqual(updated_person.name, 'Updated Name')
        self.assertNotEqual(updated_person.id, 999)
        self.assertEqual(updated_person.full_name, 'Updated Name')


class PersonDetailSerializerTestCase(TestCase):
    """
    Test cases for PersonDetailSerializer.
    """
    
    def setUp(self):
        """Set up test data."""
        self.person = Person.objects.create(
            name='John Doe',
            email='john@example.com'
        )
    
    def test_detail_serializer_includes_additional_fields(self):
        """Test that detail serializer includes related initiative fields."""
        serializer = PersonDetailSerializer(self.person)
        data = serializer.data
        
        # Should include all PersonSerializer fields
        self.assertIn('name', data)
        self.assertIn('email', data)
        self.assertIn('coordinated_count', data)
        
        # Should include additional detail fields
        self.assertIn('coordinated_initiatives', data)
        self.assertIn('team_initiatives', data)
    
    def test_detail_serializer_empty_initiatives(self):
        """Test detail serializer with no related initiatives."""
        serializer = PersonDetailSerializer(self.person)
        data = serializer.data
        
        self.assertEqual(data['coordinated_initiatives'], [])
        self.assertEqual(data['team_initiatives'], [])