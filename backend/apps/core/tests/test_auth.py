from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from oauth2_provider.models import Application
from datetime import timedelta
from django.utils import timezone

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        self.application = Application.objects.create(
            name="Test App",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_PASSWORD,
            user=self.user
        )

    def test_token_obtain_and_me_view(self):
        # 1. Obtain Token
        token_url = '/o/token/'
        data = {
            'grant_type': 'password',
            'username': 'testuser',
            'password': 'testpassword',
            'client_id': self.application.client_id,
        }
        response = self.client.post(token_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('access_token', response_data)
        access_token = response_data['access_token']

        # 2. Access Me View
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        me_url = '/api/v1/auth/me/'
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
