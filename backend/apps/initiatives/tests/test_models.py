from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.initiatives.models import Initiative, InitiativeType
from apps.people.models import Person
import datetime


class InitiativeTypeModelTest(TestCase):
    """
    Test cases for InitiativeType model validation and functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        self.type_data = {
            'name': 'Test Type',
            'code': 'test',
            'description': 'A test initiative type',
            'is_active': True
        }
    
    def test_create_initiative_type(self):
        """Test creating a valid InitiativeType."""
        itype = InitiativeType.objects.create(**self.type_data)
        self.assertEqual(itype.name, 'Test Type')
        self.assertEqual(itype.code, 'test')
        self.assertTrue(itype.is_active)
    
    def test_initiative_type_str_representation(self):
        """Test string representation of InitiativeType."""
        itype = InitiativeType.objects.create(**self.type_data)
        self.assertEqual(str(itype), 'Test Type')
    
    def test_initiative_type_unique_constraints(self):
        """Test unique constraints on name and code."""
        # Use unique test data to avoid conflicts
        unique_type_data = {
            'name': 'Unique Test Type',
            'code': 'unique_test',
            'description': 'A unique test initiative type',
            'is_active': True
        }
        
        InitiativeType.objects.create(**unique_type_data)
        
        # Test duplicate name - should raise ValidationError from model validation
        with self.assertRaises((IntegrityError, ValidationError)):
            InitiativeType.objects.create(
                name='Unique Test Type',
                code='different_code',
                description='Different description'
            )
        
        # Test duplicate code - should raise ValidationError from model validation  
        with self.assertRaises((IntegrityError, ValidationError)):
            InitiativeType.objects.create(
                name='Different Name',
                code='unique_test',
                description='Different description'
            )
    
    def test_initiative_type_validation(self):
        """Test InitiativeType model validation."""
        # Test empty name
        itype = InitiativeType(name='', code='test')
        with self.assertRaises(ValidationError):
            itype.full_clean()
        
        # Test empty code
        itype = InitiativeType(name='Test', code='')
        with self.assertRaises(ValidationError):
            itype.full_clean()
    
    def test_get_default_types(self):
        """Test the get_default_types class method."""
        program, project, event = InitiativeType.get_default_types()
        
        self.assertEqual(program.code, 'program')
        self.assertEqual(program.name, 'Program')
        
        self.assertEqual(project.code, 'project')
        self.assertEqual(project.name, 'Project')
        
        self.assertEqual(event.code, 'event')
        self.assertEqual(event.name, 'Event')


class InitiativeModelTest(TestCase):
    """
    Test cases for Initiative model validation and functionality.
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
        
        # Base initiative data
        self.initiative_data = {
            'name': 'Test Initiative',
            'description': 'A test initiative',
            'type': self.program_type,
            'start_date': datetime.date.today(),
            'coordinator': self.coordinator
        }
    
    def test_create_initiative(self):
        """Test creating a valid Initiative."""
        initiative = Initiative.objects.create(**self.initiative_data)
        self.assertEqual(initiative.name, 'Test Initiative')
        self.assertEqual(initiative.type, self.program_type)
        self.assertEqual(initiative.coordinator, self.coordinator)
    
    def test_initiative_str_representation(self):
        """Test string representation of Initiative."""
        initiative = Initiative.objects.create(**self.initiative_data)
        self.assertEqual(str(initiative), 'Test Initiative')
    
    def test_initiative_validation(self):
        """Test Initiative model validation."""
        # Test empty name
        initiative = Initiative(name='', **{k: v for k, v in self.initiative_data.items() if k != 'name'})
        with self.assertRaises(ValidationError):
            initiative.full_clean()
        
        # Test end date before start date
        initiative = Initiative(
            **self.initiative_data,
            end_date=datetime.date.today() - datetime.timedelta(days=1)
        )
        with self.assertRaises(ValidationError):
            initiative.full_clean()
    
    def test_initiative_hierarchical_relationships(self):
        """Test hierarchical parent-child relationships."""
        parent = Initiative.objects.create(**self.initiative_data)
        
        child_data = self.initiative_data.copy()
        child_data['name'] = 'Child Initiative'
        child_data['parent'] = parent
        child = Initiative.objects.create(**child_data)
        
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())
    
    def test_prevent_circular_parent_relationships(self):
        """Test prevention of circular parent relationships."""
        initiative = Initiative.objects.create(**self.initiative_data)
        
        # Test self-reference
        initiative.parent = initiative
        with self.assertRaises(ValidationError):
            initiative.full_clean()
    
    def test_team_members_relationship(self):
        """Test many-to-many team members relationship."""
        initiative = Initiative.objects.create(**self.initiative_data)
        initiative.team_members.add(self.team_member)
        
        self.assertIn(self.team_member, initiative.team_members.all())
        self.assertIn(initiative, self.team_member.team_initiatives.all())
    
    def test_computed_properties(self):
        """Test computed properties of Initiative."""
        initiative = Initiative.objects.create(**self.initiative_data)
        initiative.team_members.add(self.team_member)
        
        # Create child initiative
        child_data = self.initiative_data.copy()
        child_data['name'] = 'Child Initiative'
        child_data['parent'] = initiative
        Initiative.objects.create(**child_data)
        
        self.assertEqual(initiative.team_count, 1)
        self.assertEqual(initiative.children_count, 1)
        self.assertEqual(initiative.coordinator_name, 'John Coordinator')
        self.assertEqual(initiative.get_hierarchy_level(), 0)
    
    def test_hierarchy_level_calculation(self):
        """Test hierarchy level calculation."""
        # Root level
        root = Initiative.objects.create(**self.initiative_data)
        self.assertEqual(root.get_hierarchy_level(), 0)
        
        # Level 1
        level1_data = self.initiative_data.copy()
        level1_data['name'] = 'Level 1'
        level1_data['parent'] = root
        level1 = Initiative.objects.create(**level1_data)
        self.assertEqual(level1.get_hierarchy_level(), 1)
        
        # Level 2
        level2_data = self.initiative_data.copy()
        level2_data['name'] = 'Level 2'
        level2_data['parent'] = level1
        level2 = Initiative.objects.create(**level2_data)
        self.assertEqual(level2.get_hierarchy_level(), 2)
    
    def test_get_all_children_recursive(self):
        """Test recursive retrieval of all children."""
        root = Initiative.objects.create(**self.initiative_data)
        
        # Create child
        child_data = self.initiative_data.copy()
        child_data['name'] = 'Child'
        child_data['parent'] = root
        child = Initiative.objects.create(**child_data)
        
        # Create grandchild
        grandchild_data = self.initiative_data.copy()
        grandchild_data['name'] = 'Grandchild'
        grandchild_data['parent'] = child
        grandchild = Initiative.objects.create(**grandchild_data)
        
        all_children = root.get_all_children()
        self.assertIn(child, all_children)
        self.assertIn(grandchild, all_children)
        self.assertEqual(len(all_children), 2)