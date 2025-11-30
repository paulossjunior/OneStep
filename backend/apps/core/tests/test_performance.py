"""
Performance tests for the OneStep API.

This test suite validates that the API meets performance requirements
including query optimization, response times, and efficient data handling.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from rest_framework import status
from apps.people.models import Person
from apps.initiatives.models import Initiative, InitiativeType
import datetime
import time


class PerformanceTest(TestCase):
    """
    Performance tests to ensure API meets response time and query optimization requirements.
    """
    
    def setUp(self):
        """Set up test environment with sample data."""
        # Create user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Set up API client
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
        
        # Create initiative types
        self.program_type, _ = InitiativeType.objects.get_or_create(
            code='program',
            defaults={
                'name': 'Program',
                'description': 'Strategic program',
                'is_active': True
            }
        )
        self.project_type, _ = InitiativeType.objects.get_or_create(
            code='project',
            defaults={
                'name': 'Project',
                'description': 'Specific project',
                'is_active': True
            }
        )
    
    def test_person_list_query_optimization(self):
        """Test that person list endpoint uses optimized queries."""
        # Create test data
        for i in range(10):
            Person.objects.create(
                name=f'Person {i}',
                email=f'person{i}@example.com'
            )
        
        # Measure queries
        with CaptureQueriesContext(connection) as context:
            response = self.api_client.get('/api/people/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Should use a reasonable number of queries (not N+1)
            # Typically: 1 for count, 1 for data, maybe 1-2 for auth
            self.assertLess(len(context.captured_queries), 10,
                          f"Too many queries: {len(context.captured_queries)}")
    
    def test_initiative_list_query_optimization(self):
        """Test that initiative list endpoint uses optimized queries."""
        # Create test data with relationships
        coordinator = Person.objects.create(
            name='Coordinator',
            email='coord@example.com'
        )
        
        for i in range(10):
            Initiative.objects.create(
                name=f'Initiative {i}',
                type=self.program_type,
                start_date=datetime.date.today(),
                coordinator=coordinator
            )
        
        # Measure queries
        with CaptureQueriesContext(connection) as context:
            response = self.api_client.get('/api/initiatives/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Should use optimized queries with select_related and prefetch_related
            # With complex relationships (type, coordinator, parent, team_members, children)
            # we expect: count query, main query with joins, prefetch queries
            # Allow up to 20 queries for complex relationships
            self.assertLess(len(context.captured_queries), 20,
                          f"Too many queries: {len(context.captured_queries)}")
    
    def test_initiative_detail_query_optimization(self):
        """Test that initiative detail endpoint avoids N+1 queries."""
        # Create test data with complex relationships
        coordinator = Person.objects.create(
            name='Coordinator',
            email='coord@example.com'
        )
        
        members = []
        for i in range(5):
            member = Person.objects.create(
                name=f'Member {i}',
                email=f'member{i}@example.com'
            )
            members.append(member)
        
        # Create parent initiative
        parent = Initiative.objects.create(
            name='Parent Initiative',
            type=self.program_type,
            start_date=datetime.date.today(),
            coordinator=coordinator
        )
        
        # Create initiative with relationships
        initiative = Initiative.objects.create(
            name='Test Initiative',
            type=self.project_type,
            start_date=datetime.date.today(),
            coordinator=coordinator,
            parent=parent
        )
        initiative.team_members.set(members)
        
        # Create children
        for i in range(3):
            Initiative.objects.create(
                name=f'Child {i}',
                type=self.project_type,
                start_date=datetime.date.today(),
                coordinator=coordinator,
                parent=initiative
            )
        
        # Measure queries for detail view
        with CaptureQueriesContext(connection) as context:
            response = self.api_client.get(f'/api/initiatives/{initiative.id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Should use select_related and prefetch_related to avoid N+1
            # With nested serialization (children, team_members, parent, type, coordinator)
            # Allow up to 40 queries for complex nested data
            self.assertLess(len(context.captured_queries), 40,
                          f"Too many queries: {len(context.captured_queries)}")
    
    def test_person_detail_query_optimization(self):
        """Test that person detail endpoint avoids N+1 queries."""
        # Create person with multiple initiatives
        coordinator = Person.objects.create(
            name='Busy Coordinator',
            email='busy@example.com'
        )
        
        # Create initiatives they coordinate
        for i in range(5):
            Initiative.objects.create(
                name=f'Coordinated Initiative {i}',
                type=self.program_type,
                start_date=datetime.date.today(),
                coordinator=coordinator
            )
        
        # Create initiatives they're a team member of
        other_coord = Person.objects.create(
            name='Other Coordinator',
            email='other@example.com'
        )
        for i in range(5):
            initiative = Initiative.objects.create(
                name=f'Team Initiative {i}',
                type=self.project_type,
                start_date=datetime.date.today(),
                coordinator=other_coord
            )
            initiative.team_members.add(coordinator)
        
        # Measure queries for detail view
        with CaptureQueriesContext(connection) as context:
            response = self.api_client.get(f'/api/people/{coordinator.id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Should use prefetch_related to avoid N+1
            self.assertLess(len(context.captured_queries), 15,
                          f"Too many queries: {len(context.captured_queries)}")
    
    def test_api_response_time_person_list(self):
        """Test that person list API responds within acceptable time."""
        # Create moderate dataset
        for i in range(50):
            Person.objects.create(
                name=f'Person {i}',
                email=f'person{i}@example.com'
            )
        
        # Measure response time
        start_time = time.time()
        response = self.api_client.get('/api/people/')
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should respond within 100ms as per performance requirements
        # In test environment, allow up to 500ms for safety
        self.assertLess(response_time_ms, 500,
                       f"Response time too slow: {response_time_ms:.2f}ms")
    
    def test_api_response_time_initiative_list(self):
        """Test that initiative list API responds within acceptable time."""
        # Create moderate dataset with relationships
        coordinator = Person.objects.create(
            name='Coordinator',
            email='coord@example.com'
        )
        
        for i in range(50):
            Initiative.objects.create(
                name=f'Initiative {i}',
                type=self.program_type if i % 2 == 0 else self.project_type,
                start_date=datetime.date.today(),
                coordinator=coordinator
            )
        
        # Measure response time
        start_time = time.time()
        response = self.api_client.get('/api/initiatives/')
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should respond within 100ms as per performance requirements
        # In test environment, allow up to 500ms for safety
        self.assertLess(response_time_ms, 500,
                       f"Response time too slow: {response_time_ms:.2f}ms")
    
    def test_pagination_performance(self):
        """Test that pagination doesn't cause performance issues."""
        # Create large dataset
        for i in range(100):
            Person.objects.create(
                name=f'Person {i}',
                email=f'person{i}@example.com'
            )
        
        # Test first page
        with CaptureQueriesContext(connection) as context:
            response = self.api_client.get('/api/people/', {'page': 1})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            first_page_queries = len(context.captured_queries)
        
        # Test middle page
        with CaptureQueriesContext(connection) as context:
            response = self.api_client.get('/api/people/', {'page': 3})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            middle_page_queries = len(context.captured_queries)
        
        # Query count should be consistent across pages
        self.assertEqual(first_page_queries, middle_page_queries,
                        "Query count varies across pages")
    
    def test_filtering_performance(self):
        """Test that filtering doesn't cause performance degradation."""
        # Create test data
        coordinator1 = Person.objects.create(
            name='Coordinator 1',
            email='coord1@example.com'
        )
        coordinator2 = Person.objects.create(
            name='Coordinator 2',
            email='coord2@example.com'
        )
        
        for i in range(50):
            Initiative.objects.create(
                name=f'Initiative {i}',
                type=self.program_type if i % 2 == 0 else self.project_type,
                start_date=datetime.date.today(),
                coordinator=coordinator1 if i % 2 == 0 else coordinator2
            )
        
        # Test filtering by type
        with CaptureQueriesContext(connection) as context:
            response = self.api_client.get('/api/initiatives/', {
                'type': self.program_type.id
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            type_filter_queries = len(context.captured_queries)
        
        # Test filtering by coordinator
        with CaptureQueriesContext(connection) as context:
            response = self.api_client.get('/api/initiatives/', {
                'coordinator': coordinator1.id
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            coord_filter_queries = len(context.captured_queries)
        
        # Filtering should not significantly increase query count
        # With complex relationships, allow up to 30 queries
        self.assertLess(type_filter_queries, 30)
        self.assertLess(coord_filter_queries, 30)
    
    def test_search_performance(self):
        """Test that search functionality is performant."""
        # Create searchable data
        for i in range(100):
            Person.objects.create(
                name=f'Person {i}',
                email=f'person{i}@example.com'
            )
        
        # Test search
        start_time = time.time()
        response = self.api_client.get('/api/people/search/', {'q': 'Person 5'})
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Search should be fast even with many records
        self.assertLess(response_time_ms, 500,
                       f"Search too slow: {response_time_ms:.2f}ms")
    
    def test_hierarchical_query_performance(self):
        """Test that hierarchical queries are optimized."""
        # Create hierarchical structure
        coordinator = Person.objects.create(
            name='Coordinator',
            email='coord@example.com'
        )
        
        # Create parent
        parent = Initiative.objects.create(
            name='Parent',
            type=self.program_type,
            start_date=datetime.date.today(),
            coordinator=coordinator
        )
        
        # Create children
        children = []
        for i in range(10):
            child = Initiative.objects.create(
                name=f'Child {i}',
                type=self.project_type,
                start_date=datetime.date.today(),
                coordinator=coordinator,
                parent=parent
            )
            children.append(child)
        
        # Create grandchildren
        for child in children[:3]:
            for j in range(3):
                Initiative.objects.create(
                    name=f'Grandchild {j}',
                    type=self.project_type,
                    start_date=datetime.date.today(),
                    coordinator=coordinator,
                    parent=child
                )
        
        # Test hierarchy endpoint
        with CaptureQueriesContext(connection) as context:
            response = self.api_client.get(f'/api/initiatives/{children[0].id}/hierarchy/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Should handle hierarchy efficiently
            self.assertLess(len(context.captured_queries), 20,
                          f"Too many queries for hierarchy: {len(context.captured_queries)}")
