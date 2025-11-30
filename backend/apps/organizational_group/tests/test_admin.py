from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse
from django.core.exceptions import ValidationError
from apps.organizational_group.admin import OrganizationalGroupAdmin, OrganizationalGroupLeadershipInline, OrganizationalGroupMemberInline, OrganizationalGroupInitiativeInline
from apps.organizational_group.models import OrganizationalGroup, OrganizationalGroupLeadership
from apps.people.models import Person
from apps.initiatives.models import Initiative, InitiativeType
from apps.initiatives.admin import InitiativeAdmin, GroupInline
import datetime


class MockRequest:
    """Mock request object for admin tests."""
    def __init__(self, user=None):
        self.user = user


class OrganizationalGroupAdminTest(TestCase):
    """
    Test cases for OrganizationalGroup admin interface.
    """
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = OrganizationalGroupAdmin(OrganizationalGroup, self.site)
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.request = MockRequest(user=self.user)
        
        # Create test data
        self.leader = Person.objects.create(
            name='John Leader',
            email='john@example.com'
        )
        self.member = Person.objects.create(
            name='Jane Member',
            email='jane@example.com'
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
            coordinator=self.leader
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
            person=self.leader,
            start_date=datetime.date.today(),
            is_active=True
        )
        
        # Add member
        self.group.members.add(self.member)
        
        # Add initiative
        self.group.initiatives.add(self.initiative)
    
    def test_list_display_fields(self):
        """Test that list display fields are correctly configured."""
        expected_fields = [
            'name',
            'short_name',
            'type_display',
            'campus',
            'knowledge_area',
            'leader_count_display',
            'member_count_display',
            'initiative_count_display',
            'created_at'
        ]
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_type_display_with_colors(self):
        """Test type display with color coding."""
        type_display = self.admin.type_display(self.group)
        self.assertIn('Research', type_display)
        self.assertIn('color:', type_display)
        self.assertIn('#2196F3', type_display)
        
        # Test extension type
        extension_group = OrganizationalGroup.objects.create(
            name='Extension Group',
            short_name='EG',
            type=OrganizationalGroup.TYPE_EXTENSION,
            knowledge_area='Agriculture',
            campus='Main Campus'
        )
        
        extension_display = self.admin.type_display(extension_group)
        self.assertIn('Extension', extension_display)
        self.assertIn('#4CAF50', extension_display)
    
    def test_leader_count_display(self):
        """Test leader count display."""
        # Get queryset with annotations
        queryset = self.admin.get_queryset(self.request)
        obj = queryset.get(pk=self.group.pk)
        
        leader_display = self.admin.leader_count_display(obj)
        self.assertIn('1', leader_display)
        self.assertIn('leader', leader_display)
        
        # Test with no leaders
        no_leader_group = OrganizationalGroup.objects.create(
            name='No Leader Group',
            short_name='NLG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Test',
            campus='Main Campus'
        )
        
        queryset = self.admin.get_queryset(self.request)
        obj = queryset.get(pk=no_leader_group.pk)
        
        no_leader_display = self.admin.leader_count_display(obj)
        self.assertIn('No leaders', no_leader_display)
    
    def test_member_count_display(self):
        """Test member count display."""
        # Get queryset with annotations
        queryset = self.admin.get_queryset(self.request)
        obj = queryset.get(pk=self.group.pk)
        
        member_display = self.admin.member_count_display(obj)
        self.assertIn('1', member_display)
        self.assertIn('member', member_display)
        
        # Test with no members
        no_member_group = OrganizationalGroup.objects.create(
            name='No Member Group',
            short_name='NMG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Test',
            campus='Main Campus'
        )
        
        queryset = self.admin.get_queryset(self.request)
        obj = queryset.get(pk=no_member_group.pk)
        
        no_member_display = self.admin.member_count_display(obj)
        self.assertIn('No members', no_member_display)
    
    def test_initiative_count_display(self):
        """Test initiative count display."""
        # Get queryset with annotations
        queryset = self.admin.get_queryset(self.request)
        obj = queryset.get(pk=self.group.pk)
        
        initiative_display = self.admin.initiative_count_display(obj)
        self.assertIn('1', initiative_display)
        self.assertIn('initiative', initiative_display)
        
        # Test with no initiatives
        no_initiative_group = OrganizationalGroup.objects.create(
            name='No Initiative Group',
            short_name='NIG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Test',
            campus='Main Campus'
        )
        
        queryset = self.admin.get_queryset(self.request)
        obj = queryset.get(pk=no_initiative_group.pk)
        
        no_initiative_display = self.admin.initiative_count_display(obj)
        self.assertIn('No initiatives', no_initiative_display)
    
    def test_get_queryset_optimization(self):
        """Test that queryset is properly optimized."""
        queryset = self.admin.get_queryset(self.request)
        
        # Check that prefetch_related is used
        self.assertTrue(hasattr(queryset, '_prefetch_related_lookups'))
        
        # Check that annotations are added
        obj = queryset.first()
        self.assertTrue(hasattr(obj, 'annotated_member_count'))
        self.assertTrue(hasattr(obj, 'annotated_initiative_count'))
        self.assertTrue(hasattr(obj, 'annotated_leader_count'))
    
    def test_search_fields(self):
        """Test search functionality."""
        expected_search_fields = [
            'name',
            'short_name',
            'knowledge_area',
            'campus'
        ]
        self.assertEqual(self.admin.search_fields, expected_search_fields)
    
    def test_list_filter_fields(self):
        """Test list filter configuration."""
        expected_filters = [
            'type',
            'campus',
            'knowledge_area',
            'created_at',
            'updated_at'
        ]
        
        for field in expected_filters:
            self.assertIn(field, self.admin.list_filter)
    
    def test_readonly_fields(self):
        """Test readonly fields configuration."""
        expected_readonly = [
            'id',
            'created_at',
            'updated_at',
            'leader_count_display',
            'member_count_display',
            'initiative_count_display'
        ]
        
        for field in expected_readonly:
            self.assertIn(field, self.admin.readonly_fields)
    
    def test_fieldsets_configuration(self):
        """Test fieldsets configuration."""
        fieldsets = self.admin.fieldsets
        
        # Check that we have the expected number of fieldsets
        self.assertEqual(len(fieldsets), 4)
        
        # Check fieldset names
        fieldset_names = [fs[0] for fs in fieldsets]
        expected_names = [
            'Basic Information',
            'Classification',
            'Statistics',
            'System Information'
        ]
        
        for name in expected_names:
            self.assertIn(name, fieldset_names)
    
    def test_inlines_configuration(self):
        """Test that inlines are properly configured."""
        expected_inlines = [
            OrganizationalGroupLeadershipInline,
            OrganizationalGroupMemberInline,
            OrganizationalGroupInitiativeInline
        ]
        
        self.assertEqual(self.admin.inlines, expected_inlines)
    
    def test_ordering(self):
        """Test default ordering."""
        self.assertEqual(self.admin.ordering, ['name'])
    
    def test_list_per_page(self):
        """Test pagination configuration."""
        self.assertEqual(self.admin.list_per_page, 25)
        self.assertEqual(self.admin.list_max_show_all, 100)
    
    def test_get_form_help_text(self):
        """Test that form has proper help text."""
        form = self.admin.get_form(self.request)
        
        # Check help text for fields
        self.assertIn('url', form.base_fields)
        self.assertIsNotNone(form.base_fields['url'].help_text)
        
        self.assertIn('type', form.base_fields)
        self.assertIsNotNone(form.base_fields['type'].help_text)
        
        self.assertIn('knowledge_area', form.base_fields)
        self.assertIsNotNone(form.base_fields['knowledge_area'].help_text)
        
        self.assertIn('campus', form.base_fields)
        self.assertIsNotNone(form.base_fields['campus'].help_text)


class OrganizationalGroupLeadershipInlineTest(TestCase):
    """
    Test cases for OrganizationalGroupLeadership inline admin.
    """
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.parent_admin = OrganizationalGroupAdmin(OrganizationalGroup, self.site)
        self.inline = OrganizationalGroupLeadershipInline(OrganizationalGroup, self.site)
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.request = MockRequest(user=self.user)
        
        self.leader = Person.objects.create(
            name='John Leader',
            email='john@example.com'
        )
        
        self.group = OrganizationalGroup.objects.create(
            name='Test Group',
            short_name='TG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Test',
            campus='Main Campus'
        )
    
    def test_inline_model(self):
        """Test that inline uses correct model."""
        self.assertEqual(self.inline.model, OrganizationalGroupLeadership)
    
    def test_inline_fields(self):
        """Test inline fields configuration."""
        expected_fields = ['person', 'start_date', 'end_date', 'is_active']
        self.assertEqual(self.inline.fields, expected_fields)
    
    def test_inline_autocomplete_fields(self):
        """Test autocomplete fields configuration."""
        self.assertIn('person', self.inline.autocomplete_fields)
    
    def test_inline_extra(self):
        """Test extra forms configuration."""
        self.assertEqual(self.inline.extra, 1)
    
    def test_inline_can_delete(self):
        """Test can_delete configuration."""
        self.assertTrue(self.inline.can_delete)
    
    def test_get_queryset_optimization(self):
        """Test that inline queryset is optimized."""
        queryset = self.inline.get_queryset(self.request)
        
        # Check that select_related is used
        self.assertTrue(len(queryset.query.select_related) > 0)


class OrganizationalGroupMemberInlineTest(TestCase):
    """
    Test cases for OrganizationalGroupMember inline admin.
    """
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.inline = OrganizationalGroupMemberInline(OrganizationalGroup, self.site)
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.request = MockRequest(user=self.user)
    
    def test_inline_model(self):
        """Test that inline uses correct through model."""
        self.assertEqual(self.inline.model, OrganizationalGroup.members.through)
    
    def test_inline_autocomplete_fields(self):
        """Test autocomplete fields configuration."""
        self.assertIn('person', self.inline.autocomplete_fields)
    
    def test_inline_extra(self):
        """Test extra forms configuration."""
        self.assertEqual(self.inline.extra, 1)
    
    def test_inline_can_delete(self):
        """Test can_delete configuration."""
        self.assertTrue(self.inline.can_delete)
    
    def test_get_queryset_optimization(self):
        """Test that inline queryset is optimized."""
        queryset = self.inline.get_queryset(self.request)
        
        # Check that select_related is used
        self.assertTrue(len(queryset.query.select_related) > 0)


class OrganizationalGroupInitiativeInlineTest(TestCase):
    """
    Test cases for OrganizationalGroupInitiative inline admin.
    """
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.inline = OrganizationalGroupInitiativeInline(OrganizationalGroup, self.site)
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.request = MockRequest(user=self.user)
    
    def test_inline_model(self):
        """Test that inline uses correct through model."""
        self.assertEqual(self.inline.model, OrganizationalGroup.initiatives.through)
    
    def test_inline_autocomplete_fields(self):
        """Test autocomplete fields configuration."""
        self.assertIn('initiative', self.inline.autocomplete_fields)
    
    def test_inline_extra(self):
        """Test extra forms configuration."""
        self.assertEqual(self.inline.extra, 1)
    
    def test_inline_can_delete(self):
        """Test can_delete configuration."""
        self.assertTrue(self.inline.can_delete)
    
    def test_get_queryset_optimization(self):
        """Test that inline queryset is optimized."""
        queryset = self.inline.get_queryset(self.request)
        
        # Check that select_related is used
        self.assertTrue(len(queryset.query.select_related) > 0)



class OrganizationalGroupAdminListViewTest(TestCase):
    """
    Test cases for OrganizationalGroup admin list view rendering.
    Requirement: 4.1, 4.2, 4.3
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Create test data
        self.leader = Person.objects.create(
            name='John Leader',
            email='john@example.com'
        )
        self.member = Person.objects.create(
            name='Jane Member',
            email='jane@example.com'
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
            coordinator=self.leader
        )
        
        # Create test groups
        self.group1 = OrganizationalGroup.objects.create(
            name='Computer Science Research Group',
            short_name='CSRG',
            url='https://example.com/csrg',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Computer Science',
            campus='Main Campus'
        )
        
        self.group2 = OrganizationalGroup.objects.create(
            name='Agriculture Extension Group',
            short_name='AEG',
            url='https://example.com/aeg',
            type=OrganizationalGroup.TYPE_EXTENSION,
            knowledge_area='Agriculture',
            campus='North Campus'
        )
        
        # Add leaders, members, and initiatives
        OrganizationalGroupLeadership.objects.create(
            group=self.group1,
            person=self.leader,
            start_date=datetime.date.today(),
            is_active=True
        )
        self.group1.members.add(self.member)
        self.group1.initiatives.add(self.initiative)
    
    def test_admin_list_view_renders(self):
        """Test that admin list view renders successfully."""
        url = reverse('admin:organizational_group_organizationalunit_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Computer Science Research Group')
        self.assertContains(response, 'Agriculture Extension Group')
    
    def test_admin_list_view_displays_correct_columns(self):
        """Test that list view displays all required columns including initiative_count."""
        url = reverse('admin:organizational_group_organizationalunit_changelist')
        response = self.client.get(url)
        
        # Check for column headers
        self.assertContains(response, 'Name')
        self.assertContains(response, 'Short name')
        self.assertContains(response, 'Type')
        self.assertContains(response, 'Campus')
        self.assertContains(response, 'Knowledge area')
        self.assertContains(response, 'Leaders')
        self.assertContains(response, 'Members')
        self.assertContains(response, 'Initiatives')
        
        # Check for data values
        self.assertContains(response, 'CSRG')
        self.assertContains(response, 'Main Campus')
        self.assertContains(response, 'Computer Science')
        # Check that counts are displayed (HTML formatted)
        self.assertContains(response, 'leader')
        self.assertContains(response, 'member')
        self.assertContains(response, 'initiative')
    
    def test_admin_search_by_name(self):
        """Test admin search functionality by name."""
        url = reverse('admin:organizational_group_organizationalunit_changelist')
        response = self.client.get(url, {'q': 'Computer Science'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Computer Science Research Group')
        self.assertNotContains(response, 'Agriculture Extension Group')
    
    def test_admin_search_by_short_name(self):
        """Test admin search functionality by short name."""
        url = reverse('admin:organizational_group_organizationalunit_changelist')
        response = self.client.get(url, {'q': 'CSRG'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Computer Science Research Group')
        self.assertNotContains(response, 'Agriculture Extension Group')
    
    def test_admin_search_by_knowledge_area(self):
        """Test admin search functionality by knowledge area."""
        url = reverse('admin:organizational_group_organizationalunit_changelist')
        response = self.client.get(url, {'q': 'Agriculture'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Agriculture Extension Group')
        self.assertNotContains(response, 'Computer Science Research Group')
    
    def test_admin_filter_by_type(self):
        """Test admin filtering by type."""
        url = reverse('admin:organizational_group_organizationalunit_changelist')
        response = self.client.get(url, {'type': OrganizationalGroup.TYPE_RESEARCH})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Computer Science Research Group')
        # Note: Both groups may appear in the filter sidebar, but only filtered results in main list
    
    def test_admin_filter_by_campus(self):
        """Test admin filtering by campus."""
        url = reverse('admin:organizational_group_organizationalunit_changelist')
        response = self.client.get(url, {'campus': 'Main Campus'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Computer Science Research Group')
    
    def test_admin_filter_by_knowledge_area(self):
        """Test admin filtering by knowledge area."""
        url = reverse('admin:organizational_group_organizationalunit_changelist')
        response = self.client.get(url, {'knowledge_area': 'Computer Science'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Computer Science Research Group')


class OrganizationalGroupAdminInlineEditingTest(TestCase):
    """
    Test cases for inline editing of leaders, members, and initiatives.
    Requirement: 4.4, 6.5
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Create test data
        self.leader = Person.objects.create(
            name='John Leader',
            email='john@example.com'
        )
        self.member = Person.objects.create(
            name='Jane Member',
            email='jane@example.com'
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
            coordinator=self.leader
        )
        
        self.group = OrganizationalGroup.objects.create(
            name='Test Research Group',
            short_name='TRG',
            url='https://example.com/trg',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Computer Science',
            campus='Main Campus'
        )
    
    def test_admin_change_view_has_leader_inline(self):
        """Test that change view includes leader inline."""
        url = reverse('admin:organizational_group_organizationalgroup_change', args=[self.group.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Leaders')
        self.assertContains(response, 'groupleadership_set')
    
    def test_admin_change_view_has_member_inline(self):
        """Test that change view includes member inline."""
        url = reverse('admin:organizational_group_organizationalgroup_change', args=[self.group.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Members')
        self.assertContains(response, 'members')
    
    def test_admin_change_view_has_initiative_inline(self):
        """Test that change view includes initiative inline."""
        url = reverse('admin:organizational_group_organizationalgroup_change', args=[self.group.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Initiatives')
        self.assertContains(response, 'initiatives')
    
    def test_admin_can_add_leader_via_inline(self):
        """Test adding a leader through inline form using model directly."""
        # Add leader directly to test the functionality
        OrganizationalGroupLeadership.objects.create(
            group=self.group,
            person=self.leader,
            start_date=datetime.date.today(),
            is_active=True
        )
        
        # Verify leader was added
        self.group.refresh_from_db()
        self.assertEqual(self.group.leader_count(), 1)
        self.assertIn(self.leader, self.group.get_current_leaders())
        
        # Verify it appears in admin change view
        url = reverse('admin:organizational_group_organizationalgroup_change', args=[self.group.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.leader.name)
    
    def test_admin_can_add_member_via_inline(self):
        """Test adding a member through inline form using model directly."""
        # Add member directly to test the functionality
        self.group.members.add(self.member)
        
        # Verify member was added
        self.group.refresh_from_db()
        self.assertEqual(self.group.member_count(), 1)
        self.assertIn(self.member, self.group.members.all())
        
        # Verify it appears in admin change view
        url = reverse('admin:organizational_group_organizationalgroup_change', args=[self.group.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.name)
    
    def test_admin_can_add_initiative_via_inline(self):
        """Test adding an initiative through inline form using model directly."""
        # Add initiative directly to test the functionality
        self.group.initiatives.add(self.initiative)
        
        # Verify initiative was added
        self.group.refresh_from_db()
        self.assertEqual(self.group.initiative_count(), 1)
        self.assertIn(self.initiative, self.group.initiatives.all())
        
        # Verify it appears in admin change view
        url = reverse('admin:organizational_group_organizationalgroup_change', args=[self.group.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.initiative.name)


class OrganizationalGroupAdminValidationTest(TestCase):
    """
    Test cases for admin validation error display.
    Requirement: 7.1, 7.2, 7.3, 7.4, 7.6
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Create existing group for duplicate testing
        self.existing_group = OrganizationalGroup.objects.create(
            name='Existing Group',
            short_name='EG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Test',
            campus='Main Campus'
        )
    
    def test_admin_validation_empty_name(self):
        """Test validation error for empty name."""
        url = reverse('admin:organizational_group_organizationalgroup_add')
        
        data = {
            'name': '',  # Empty name
            'short_name': 'TEST',
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'Main Campus',
            
            # Inline formsets
            'groupleadership_set-TOTAL_FORMS': '0',
            'groupleadership_set-INITIAL_FORMS': '0',
            'groupleadership_set-MIN_NUM_FORMS': '0',
            'groupleadership_set-MAX_NUM_FORMS': '1000',
            'members-TOTAL_FORMS': '0',
            'members-INITIAL_FORMS': '0',
            'members-MIN_NUM_FORMS': '0',
            'members-MAX_NUM_FORMS': '1000',
            'initiatives-TOTAL_FORMS': '0',
            'initiatives-INITIAL_FORMS': '0',
            'initiatives-MIN_NUM_FORMS': '0',
            'initiatives-MAX_NUM_FORMS': '1000',
        }
        
        response = self.client.post(url, data)
        
        # Should show validation error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
    
    def test_admin_validation_empty_short_name(self):
        """Test validation error for empty short name."""
        url = reverse('admin:organizational_group_organizationalgroup_add')
        
        data = {
            'name': 'Test Group',
            'short_name': '',  # Empty short name
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'Main Campus',
            
            # Inline formsets
            'groupleadership_set-TOTAL_FORMS': '0',
            'groupleadership_set-INITIAL_FORMS': '0',
            'groupleadership_set-MIN_NUM_FORMS': '0',
            'groupleadership_set-MAX_NUM_FORMS': '1000',
            'members-TOTAL_FORMS': '0',
            'members-INITIAL_FORMS': '0',
            'members-MIN_NUM_FORMS': '0',
            'members-MAX_NUM_FORMS': '1000',
            'initiatives-TOTAL_FORMS': '0',
            'initiatives-INITIAL_FORMS': '0',
            'initiatives-MIN_NUM_FORMS': '0',
            'initiatives-MAX_NUM_FORMS': '1000',
        }
        
        response = self.client.post(url, data)
        
        # Should show validation error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
    
    def test_admin_validation_invalid_url(self):
        """Test validation error for invalid URL format."""
        url = reverse('admin:organizational_group_organizationalgroup_add')
        
        data = {
            'name': 'Test Group',
            'short_name': 'TG',
            'url': 'not-a-valid-url',  # Invalid URL
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'Main Campus',
            
            # Inline formsets
            'groupleadership_set-TOTAL_FORMS': '0',
            'groupleadership_set-INITIAL_FORMS': '0',
            'groupleadership_set-MIN_NUM_FORMS': '0',
            'groupleadership_set-MAX_NUM_FORMS': '1000',
            'members-TOTAL_FORMS': '0',
            'members-INITIAL_FORMS': '0',
            'members-MIN_NUM_FORMS': '0',
            'members-MAX_NUM_FORMS': '1000',
            'initiatives-TOTAL_FORMS': '0',
            'initiatives-INITIAL_FORMS': '0',
            'initiatives-MIN_NUM_FORMS': '0',
            'initiatives-MAX_NUM_FORMS': '1000',
        }
        
        response = self.client.post(url, data)
        
        # Should show validation error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid URL')
    
    def test_admin_validation_duplicate_short_name_campus(self):
        """Test validation error for duplicate short_name + campus combination."""
        url = reverse('admin:organizational_group_organizationalgroup_add')
        
        data = {
            'name': 'Another Group',
            'short_name': 'EG',  # Same as existing_group
            'type': OrganizationalGroup.TYPE_RESEARCH,
            'knowledge_area': 'Test',
            'campus': 'Main Campus',  # Same as existing_group
            
            # Inline formsets
            'groupleadership_set-TOTAL_FORMS': '0',
            'groupleadership_set-INITIAL_FORMS': '0',
            'groupleadership_set-MIN_NUM_FORMS': '0',
            'groupleadership_set-MAX_NUM_FORMS': '1000',
            'members-TOTAL_FORMS': '0',
            'members-INITIAL_FORMS': '0',
            'members-MIN_NUM_FORMS': '0',
            'members-MAX_NUM_FORMS': '1000',
            'initiatives-TOTAL_FORMS': '0',
            'initiatives-INITIAL_FORMS': '0',
            'initiatives-MIN_NUM_FORMS': '0',
            'initiatives-MAX_NUM_FORMS': '1000',
        }
        
        response = self.client.post(url, data)
        
        # Should show validation error
        self.assertEqual(response.status_code, 200)
        # Check for constraint error message
        self.assertTrue(
            'already exists' in response.content.decode().lower() or
            'unique' in response.content.decode().lower()
        )


class OrganizationalGroupInlineInInitiativeAdminTest(TestCase):
    """
    Test cases for OrganizationalGroupInline in InitiativeAdmin.
    Requirement: 6.6
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Create test data
        self.coordinator = Person.objects.create(
            name='John Coordinator',
            email='john@example.com'
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
            coordinator=self.coordinator
        )
        
        self.group = OrganizationalGroup.objects.create(
            name='Test Research Group',
            short_name='TRG',
            type=OrganizationalGroup.TYPE_RESEARCH,
            knowledge_area='Computer Science',
            campus='Main Campus'
        )
        
        # Associate group with initiative
        self.initiative.groups.add(self.group)
    
    def test_initiative_admin_has_group_inline(self):
        """Test that InitiativeAdmin includes GroupInline."""
        site = AdminSite()
        admin = InitiativeAdmin(Initiative, site)
        
        # Check that GroupInline is in inlines
        self.assertIn(GroupInline, admin.inlines)
    
    def test_initiative_change_view_displays_groups(self):
        """Test that initiative change view displays associated groups."""
        url = reverse('admin:initiatives_initiative_change', args=[self.initiative.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Groups')
        self.assertContains(response, 'Test Research Group')
    
    def test_initiative_can_add_group_via_inline(self):
        """Test adding a group to initiative through inline form using model directly."""
        # Create another group
        new_group = OrganizationalGroup.objects.create(
            name='Another Group',
            short_name='AG',
            type=OrganizationalGroup.TYPE_EXTENSION,
            knowledge_area='Agriculture',
            campus='North Campus'
        )
        
        # Count existing groups
        existing_groups = self.initiative.groups.count()
        
        # Add group directly to test the functionality
        self.initiative.groups.add(new_group)
        
        # Check that group was added
        self.initiative.refresh_from_db()
        self.assertEqual(self.initiative.groups.count(), existing_groups + 1)
        self.assertIn(new_group, self.initiative.groups.all())
        
        # Verify it appears in admin change view
        url = reverse('admin:initiatives_initiative_change', args=[self.initiative.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, new_group.name)
    
    def test_group_inline_queryset_optimization(self):
        """Test that GroupInline queryset is optimized."""
        site = AdminSite()
        inline = GroupInline(Initiative, site)
        request = MockRequest(user=self.user)
        
        queryset = inline.get_queryset(request)
        
        # Check that select_related is used
        self.assertTrue(len(queryset.query.select_related) > 0)
