from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from learning.models import User, Language, Course, Module, Lesson


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')

    def test_register_user(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)

    def test_register_passwords_dont_match(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'OtroPassword!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        User.objects.create_user(username='testuser', email='login@example.com', password='TestPass123!')
        data = {'email': 'login@example.com', 'password': 'TestPass123!'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class LanguageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='student', email='student@example.com', password='TestPass123!'
        )
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='AdminPass123!'
        )

    def test_list_languages_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('language-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_language_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Inglés', 'code': 'EN'}
        response = self.client.post(reverse('language-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_language_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Francés', 'code': 'FR'}
        response = self.client.post(reverse('language-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
