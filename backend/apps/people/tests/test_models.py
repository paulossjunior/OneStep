from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.people.models import Person


class PersonModelTestCase(TestCase):
    """
    Test cases for Person model validation and methods.
    """
    
    def setUp(self):
        """Set up test data."""
        self.valid_person_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }
    
    def test_person_creation_with_valid_data(self):
        """Test creating a person with valid data."""
        person = Person.objects.create(**self.valid_person_data)
        
        self.assertEqual(person.name, 'John Doe')
        self.assertEqual(person.email, 'john.doe@example.com')
        self.assertIsNotNone(person.created_at)
        self.assertIsNotNone(person.updated_at)
    
    def test_person_str_representation(self):
        """Test string representation of Person."""
        person = Person(**self.valid_person_data)
        self.assertEqual(str(person), 'John Doe')
    
    def test_person_full_name_property(self):
        """Test full_name property returns correct value."""
        person = Person(**self.valid_person_data)
        self.assertEqual(person.full_name, 'John Doe')
    
    def test_email_uniqueness_constraint(self):
        """Test that email field enforces uniqueness."""
        Person.objects.create(**self.valid_person_data)
        
        # Try to create another person with same email
        with self.assertRaises(ValidationError):
            Person.objects.create(
                name='Jane Doe',
                email='john.doe@example.com'  # Same email
            )
    
    def test_name_validation_empty_string(self):
        """Test validation fails for empty name."""
        person = Person(
            name='',
            email='test@example.com'
        )
        
        with self.assertRaises(ValidationError) as context:
            person.full_clean()
        
        self.assertIn('name', context.exception.error_dict)
        self.assertIn('Name cannot be empty', str(context.exception))
    
    def test_name_validation_whitespace_only(self):
        """Test validation fails for whitespace-only name."""
        person = Person(
            name='   ',
            email='test@example.com'
        )
        
        with self.assertRaises(ValidationError) as context:
            person.full_clean()
        
        self.assertIn('name', context.exception.error_dict)
    
    def test_name_whitespace_cleanup(self):
        """Test that name whitespace is cleaned up."""
        person = Person(
            name='  John Doe  ',
            email='test@example.com'
        )
        person.full_clean()
        
        self.assertEqual(person.name, 'John Doe')
    
    def test_email_case_insensitive_uniqueness(self):
        """Test email uniqueness is case-insensitive."""
        Person.objects.create(
            name='John Doe',
            email='john@example.com'
        )
        
        person = Person(
            name='Jane Doe',
            email='JOHN@EXAMPLE.COM'  # Same email, different case
        )
        
        with self.assertRaises(ValidationError) as context:
            person.full_clean()
        
        self.assertIn('email', context.exception.error_dict)
    
    def test_email_normalization_to_lowercase(self):
        """Test that email is normalized to lowercase."""
        person = Person(
            name='John Doe',
            email='JOHN@EXAMPLE.COM'
        )
        person.full_clean()
        
        self.assertEqual(person.email, 'john@example.com')
    

    
    def test_model_ordering(self):
        """Test that Person model is ordered by name."""
        Person.objects.create(name='Zoe Smith', email='zoe@example.com')
        Person.objects.create(name='Alice Johnson', email='alice@example.com')
        Person.objects.create(name='Bob Wilson', email='bob@example.com')
        
        people = list(Person.objects.all())
        names = [person.name for person in people]
        
        self.assertEqual(names, ['Alice Johnson', 'Bob Wilson', 'Zoe Smith'])
    
    def test_get_coordinated_initiatives_count_no_initiatives(self):
        """Test coordinated initiatives count when no initiatives exist."""
        person = Person.objects.create(**self.valid_person_data)
        count = person.get_coordinated_initiatives_count()
        self.assertEqual(count, 0)
    
    def test_get_team_initiatives_count_no_initiatives(self):
        """Test team initiatives count when no initiatives exist."""
        person = Person.objects.create(**self.valid_person_data)
        count = person.get_team_initiatives_count()
        self.assertEqual(count, 0)