from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory
from apps.initiatives.admin import InitiativeAdmin, InitiativeTypeAdmin
from apps.initiatives.models import Initiative, InitiativeType
from apps.people.models import Person
import datetime


class MockRequest:
    """Mock request object for admin tests."""
    def __init__(self, user=None):
        self.user = user


class InitiativeTypeAdminTest(TestCase):
    """
    Test cases for InitiativeType admin interface.
    """
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = InitiativeTypeAdmin(InitiativeType, self.site)
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.request = MockRequest(user=self.user)
        
        self.initiative_type = InitiativeType.objects.create(
            name='Test Type',
            code='test',
            description='A test type',
            is_active=True
        )
    
    def test_list_display_fields(self):
        """Test that list display fields are correctly configured."""
        expected_fields = ['name', 'code', 'is_active', 'initiative_count', 'created_at']
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_initiative_count_display(self):
        """Test the initiative_count display method."""
        # Create an initiative using this type
        coordinator = Person.objects.create(
            name='Test Coordinator',
            email='test@example.com'
        )
        Initiative.objects.create(
            name='Test Initiative',
            type=self.initiative_type,
            start_date=datetime.date.today(),
            coordinator=coordinator
        )
        
        # Get queryset with annotations
        queryset = self.admin.get_queryset(self.request)
        obj = queryset.get(pk=self.initiative_type.pk)
        
        count_display = self.admin.initiative_count(obj)
        self.assertIn('1', count_display)
    
    def test_search_fields(self):
        """Test search functionality."""
        self.assertIn('name', self.admin.search_fields)
        self.assertIn('code', self.admin.search_fields)
        self.assertIn('description', self.admin.search_fields)


class InitiativeAdminTest(TestCase):
    """
    Test cases for Initiative admin interface.
    """
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = InitiativeAdmin(Initiative, self.site)
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.request = MockRequest(user=self.user)
        
        # Create test data (use get_or_create to avoid conflicts with migration data)
        self.initiative_type, _ = InitiativeType.objects.get_or_create(
            code='program',
            defaults={'name': 'Program', 'description': 'Program type'}
        )
        self.coordinator = Person.objects.create(
            name='John Coordinator',
            email='john@example.com'
        )
        self.team_member = Person.objects.create(
            name='Jane Member',
            email='jane@example.com'
        )
        
        self.initiative = Initiative.objects.create(
            name='Test Initiative',
            description='A test initiative',
            type=self.initiative_type,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=30),
            coordinator=self.coordinator
        )
        self.initiative.team_members.add(self.team_member)
    
    def test_list_display_fields(self):
        """Test that list display fields are correctly configured."""
        expected_fields = [
            'name_display',
            'type_display',
            'coordinator_display',
            'start_date_display',
            'end_date_display',
            'team_count_display',
            'children_count_display',
            'hierarchy_level_display',
            'status_display'
        ]
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_name_display_with_hierarchy(self):
        """Test name display with hierarchy indication."""
        # Test root level
        root_display = self.admin.name_display(self.initiative)
        self.assertIn('Test Initiative', root_display)
        
        # Create child initiative
        child = Initiative.objects.create(
            name='Child Initiative',
            type=self.initiative_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator,
            parent=self.initiative
        )
        
        child_display = self.admin.name_display(child)
        self.assertIn('Child Initiative', child_display)
        self.assertIn('└─', child_display)
    
    def test_type_display_with_colors(self):
        """Test type display with color coding."""
        type_display = self.admin.type_display(self.initiative)
        self.assertIn('Program', type_display)
        self.assertIn('color:', type_display)
    
    def test_coordinator_display_with_link(self):
        """Test coordinator display with admin link."""
        coord_display = self.admin.coordinator_display(self.initiative)
        self.assertIn('John Coordinator', coord_display)
        self.assertIn('href=', coord_display)
    
    def test_team_count_display(self):
        """Test team count display."""
        # Get queryset with annotations
        queryset = self.admin.get_queryset(self.request)
        obj = queryset.get(pk=self.initiative.pk)
        
        team_display = self.admin.team_count_display(obj)
        self.assertIn('1', team_display)
        self.assertIn('member', team_display)
    
    def test_children_count_display(self):
        """Test children count display."""
        # Create child initiative
        Initiative.objects.create(
            name='Child Initiative',
            type=self.initiative_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator,
            parent=self.initiative
        )
        
        # Get queryset with annotations
        queryset = self.admin.get_queryset(self.request)
        obj = queryset.get(pk=self.initiative.pk)
        
        children_display = self.admin.children_count_display(obj)
        self.assertIn('1', children_display)
        self.assertIn('child', children_display)
    
    def test_hierarchy_level_display(self):
        """Test hierarchy level display."""
        # Test root level
        level_display = self.admin.hierarchy_level_display(self.initiative)
        self.assertIn('Root', level_display)
        
        # Create child initiative
        child = Initiative.objects.create(
            name='Child Initiative',
            type=self.initiative_type,
            start_date=datetime.date.today(),
            coordinator=self.coordinator,
            parent=self.initiative
        )
        
        child_level_display = self.admin.hierarchy_level_display(child)
        self.assertIn('Level', child_level_display)
        self.assertIn('1', child_level_display)
    
    def test_status_display(self):
        """Test status display based on dates."""
        # Test active initiative (current)
        status_display = self.admin.status_display(self.initiative)
        self.assertIn('Active', status_display)
        
        # Test upcoming initiative
        future_initiative = Initiative.objects.create(
            name='Future Initiative',
            type=self.initiative_type,
            start_date=datetime.date.today() + datetime.timedelta(days=10),
            coordinator=self.coordinator
        )
        
        future_status = self.admin.status_display(future_initiative)
        self.assertIn('Upcoming', future_status)
        
        # Test completed initiative
        past_initiative = Initiative.objects.create(
            name='Past Initiative',
            type=self.initiative_type,
            start_date=datetime.date.today() - datetime.timedelta(days=30),
            end_date=datetime.date.today() - datetime.timedelta(days=1),
            coordinator=self.coordinator
        )
        
        past_status = self.admin.status_display(past_initiative)
        self.assertIn('Completed', past_status)
    
    def test_get_queryset_optimization(self):
        """Test that queryset is properly optimized."""
        queryset = self.admin.get_queryset(self.request)
        
        # Check that select_related and prefetch_related are used
        self.assertTrue(hasattr(queryset, '_prefetch_related_lookups'))
        self.assertTrue(len(queryset.query.select_related) > 0)
    
    def test_search_fields(self):
        """Test search functionality."""
        expected_search_fields = [
            'name',
            'description',
            'coordinator__name',
            'parent__name'
        ]
        self.assertEqual(self.admin.search_fields, expected_search_fields)
    
    def test_list_filter_fields(self):
        """Test list filter configuration."""
        expected_filters = [
            'type',
            'start_date',
            'end_date',
            'coordinator',
            'created_at',
            'updated_at',
            ('parent', self.admin.list_filter[6].__class__)  # RelatedOnlyFieldListFilter
        ]
        
        # Check that all expected filters are present (excluding the class check)
        filter_fields = [f if isinstance(f, str) else f[0] for f in expected_filters[:-1]]
        admin_filter_fields = [f if isinstance(f, str) else f[0] for f in self.admin.list_filter[:-1]]
        
        for field in filter_fields:
            self.assertIn(field, admin_filter_fields)
    
    def test_readonly_fields(self):
        """Test readonly fields configuration."""
        expected_readonly = [
            'id',
            'created_at',
            'updated_at',
            'team_count_display',
            'children_count_display',
            'hierarchy_level_display',
            'coordinator_name',
            'status_display'
        ]
        
        for field in expected_readonly:
            self.assertIn(field, self.admin.readonly_fields)
    
    def test_fieldsets_configuration(self):
        """Test fieldsets configuration."""
        fieldsets = self.admin.fieldsets
        
        # Check that we have the expected number of fieldsets
        self.assertEqual(len(fieldsets), 5)
        
        # Check fieldset names
        fieldset_names = [fs[0] for fs in fieldsets]
        expected_names = [
            'Basic Information',
            'Timeline',
            'Relationships',
            'Statistics',
            'System Information'
        ]
        
        for name in expected_names:
            self.assertIn(name, fieldset_names)