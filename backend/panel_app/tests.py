from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Server, Config, Announcement, Tutorial

User = get_user_model()

class AuthAndUserManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user_credentials = {'username': 'testadmin', 'password': 'StrongPassword123'}
        self.admin_user = User.objects.create_superuser(**self.admin_user_credentials, email='admin@example.com')

        self.normal_user_credentials = {'username': 'testuser', 'password': 'UserPassword123'}
        self.normal_user = User.objects.create_user(**self.normal_user_credentials, email='user@example.com', phone_number='1234567890')

        # Authenticate admin client
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

        # Get token for normal user for some tests
        self.normal_user_token = Token.objects.create(user=self.normal_user)
        self.authenticated_client = APIClient()
        self.authenticated_client.credentials(HTTP_AUTHORIZATION='Token ' + self.normal_user_token.key)


    def test_login_success(self):
        url = reverse('panel_app:api_token_auth')
        response = self.client.post(url, self.normal_user_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_fail_wrong_password(self):
        url = reverse('panel_app:api_token_auth')
        response = self.client.post(url, {'username': 'testuser', 'password': 'wrongpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_get_user_profile_authenticated(self):
        url = reverse('panel_app:user_profile')
        response = self.authenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.normal_user.username)
        self.assertEqual(response.data['phone_number'], self.normal_user.phone_number)

    def test_get_user_profile_unauthenticated(self):
        url = reverse('panel_app:user_profile')
        response = self.client.get(url) # Unauthenticated client
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Admin User Management Tests ---
    def test_admin_list_users_as_admin(self):
        url = reverse('panel_app:admin_user_list')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 2) # Admin and normal user

    def test_admin_list_users_as_normal_user(self):
        url = reverse('panel_app:admin_user_list')
        response = self.authenticated_client.get(url) # Normal user client
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_create_user_success(self):
        url = reverse('panel_app:admin_user_create')
        user_data = {
            'username': 'newcustomer',
            'password': 'NewPassword123',
            'email': 'customer@example.com',
            'phone_number': '9876543210',
            'is_support_staff': False
        }
        response = self.admin_client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        new_user = User.objects.get(username='newcustomer')
        self.assertEqual(new_user.email, 'customer@example.com')
        self.assertFalse(new_user.is_support_staff)

    def test_admin_create_user_generate_password(self):
        url = reverse('panel_app:admin_user_create')
        user_data = {
            'username': 'anothercustomer',
            'email': 'another@example.com',
            'phone_number': '0123456789'
            # Password omitted to test generation
        }
        response = self.admin_client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('generated_password', response.data)
        self.assertIsNotNone(response.data['generated_password'])
        self.assertTrue(len(response.data['generated_password']) >= 8) # Default length in serializer is 12
        new_user = User.objects.get(username='anothercustomer')
        self.assertTrue(new_user.check_password(response.data['generated_password']))


    def test_admin_create_user_username_exists(self):
        url = reverse('panel_app:admin_user_create')
        user_data = {'username': 'testuser', 'password': 'password'} # testuser already exists
        response = self.admin_client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_admin_create_support_user_success(self):
        url = reverse('panel_app:support_user_create')
        support_data = {
            'username': 'newsupport',
            'email': 'support_new@example.com',
            'phone_number': '5551234567'
        }
        response = self.admin_client.post(url, support_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('generated_password', response.data)
        self.assertTrue(len(response.data['generated_password']) >= 12) # As per serializer

        support_user = User.objects.get(username='newsupport')
        self.assertTrue(support_user.is_support_staff)
        self.assertFalse(support_user.is_staff) # Should not be general staff unless explicitly made so
        self.assertTrue(support_user.check_password(response.data['generated_password']))

    def test_admin_retrieve_user_detail(self):
        url = reverse('panel_app:admin_user_detail', kwargs={'pk': self.normal_user.pk})
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.normal_user.username)

    def test_admin_update_user(self):
        url = reverse('panel_app:admin_user_detail', kwargs={'pk': self.normal_user.pk})
        update_data = {'first_name': 'Test', 'last_name': 'UserUpdated', 'phone_number': '1112223333'}
        response = self.admin_client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, 'Test')
        self.assertEqual(self.normal_user.phone_number, '1112223333')

    def test_admin_delete_user(self):
        user_to_delete = User.objects.create_user(username='todelete', password='password')
        url = reverse('panel_app:admin_user_detail', kwargs={'pk': user_to_delete.pk})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=user_to_delete.pk).exists())


class BasicModelTests(TestCase): # Renamed from UserModelTests to avoid conflict, keeping other model tests

    def test_create_user_model_direct(self): # Renamed from test_create_user
        user = User.objects.create_user(username='directuser', password='password123', email='direct@example.com')
        self.assertEqual(user.username, 'directuser')
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_support_staff)

    def test_create_superuser_model_direct(self): # Renamed from test_create_superuser
        admin_user = User.objects.create_superuser(username='directadmin', password='password123', email='directadmin@example.com')
        self.assertEqual(admin_user.username, 'directadmin')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_create_support_staff_user_model_direct(self): # Renamed from test_create_support_staff_user
        support_user = User.objects.create_user(
            username='directsupport',
            password='password123',
            email='directsupport@example.com',
            is_support_staff=True
        )
        self.assertEqual(support_user.username, 'directsupport')
        self.assertTrue(support_user.is_support_staff)
        self.assertFalse(support_user.is_staff)

class ServerModelTests(TestCase):

    def setUp(self):
        self.server = Server.objects.create(
            name="Test Server",
            url="http://testserver.com",
            panel_type="alireza",
            username="testuser",
            password="testpassword"
        )

    def test_server_creation(self):
        self.assertEqual(self.server.name, "Test Server")
        self.assertEqual(self.server.panel_type, "alireza")
        self.assertFalse(self.server.is_active)

class ConfigModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='configuser', password='password123')
        self.server = Server.objects.create(
            name="Config Test Server",
            url="http://configserver.com",
            panel_type="3xui",
            username="config_server_user",
            password="config_server_password"
        )
        self.config = Config.objects.create(
            user=self.user,
            server=self.server,
            client_identifier="client_test_id_123",
            subscription_link="http://sublink.com/sub"
        )

    def test_config_creation(self):
        self.assertEqual(self.config.user.username, "configuser")
        self.assertEqual(self.config.server.name, "Config Test Server")
        self.assertEqual(self.config.client_identifier, "client_test_id_123")

class AnnouncementModelTests(TestCase):

    def test_announcement_creation(self):
        announcement = Announcement.objects.create(title="New Update", content="System will be down for maintenance.")
        self.assertEqual(announcement.title, "New Update")
        self.assertFalse(announcement.is_faq)

class TutorialModelTests(TestCase):

    def test_tutorial_creation(self):
        tutorial = Tutorial.objects.create(title="How to Connect", content="Follow these steps...", order=1)
        self.assertEqual(tutorial.title, "How to Connect")
        self.assertEqual(tutorial.order, 1)

    def test_tutorial_ordering(self):
        Tutorial.objects.create(title="Second Tutorial", content="...", order=2)
        Tutorial.objects.create(title="First Tutorial", content="...", order=1)
        Tutorial.objects.create(title="Third Tutorial", content="...", order=3)

        tutorials = Tutorial.objects.all() # Default ordering is by 'order', 'title'
        self.assertEqual(tutorials[0].title, "First Tutorial")
        self.assertEqual(tutorials[1].title, "Second Tutorial")
        self.assertEqual(tutorials[2].title, "Third Tutorial")
