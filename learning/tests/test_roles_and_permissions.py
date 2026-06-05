"""
Tests de roles, permisos, registro y login
===========================================
Cobertura:
  - Sincronización automática de flags al asignar role
  - RegisterSerializer → crea student sin rol NULL
  - Login → devuelve user{} en el body
  - GET /api/auth/me/ → devuelve usuario autenticado
  - Permisos IsAdmin, IsTeacher, IsStudent, IsTeacherOrAdmin
  - Migración de datos (roles creados, usuarios asignados)
  - Endpoints con permisos correctos por rol
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from learning.models import Role, User, UserProfile, ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT


# ─── Helpers ─────────────────────────────────────────────────────────────────

def create_roles():
    """Crea los tres roles canónicos. Idempotente."""
    admin_role,   _ = Role.objects.get_or_create(name=ROLE_ADMIN)
    teacher_role, _ = Role.objects.get_or_create(name=ROLE_TEACHER)
    student_role, _ = Role.objects.get_or_create(name=ROLE_STUDENT)
    return admin_role, teacher_role, student_role


def make_user(email, username, password, role_obj):
    user = User.objects.create_user(
        email=email, username=username, password=password
    )
    user.role = role_obj
    user.save()
    UserProfile.objects.get_or_create(user=user)
    return user


# ─── 1. Sincronización de flags ───────────────────────────────────────────────

class RoleFlagSyncTests(TestCase):

    def setUp(self):
        self.admin_role, self.teacher_role, self.student_role = create_roles()

    def test_admin_role_sets_staff_and_superuser(self):
        user = make_user('admin@test.com', 'adm', 'Pass1234!', self.admin_role)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_teacher_role_sets_staff_only(self):
        user = make_user('teacher@test.com', 'tch', 'Pass1234!', self.teacher_role)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_student_role_unsets_both_flags(self):
        user = make_user('student@test.com', 'std', 'Pass1234!', self.student_role)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_changing_role_teacher_to_student_updates_flags(self):
        user = make_user('change@test.com', 'chg', 'Pass1234!', self.teacher_role)
        self.assertTrue(user.is_staff)

        user.role = self.student_role
        user.save()

        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_changing_role_student_to_admin_updates_flags(self):
        user = make_user('promote@test.com', 'prm', 'Pass1234!', self.student_role)
        self.assertFalse(user.is_staff)

        user.role = self.admin_role
        user.save()

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


# ─── 2. Registro ─────────────────────────────────────────────────────────────

class RegisterTests(APITestCase):

    def setUp(self):
        create_roles()
        self.url = reverse('register')

    def test_register_creates_student_role(self):
        data = {
            'username': 'nuevo',
            'email': 'nuevo@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email='nuevo@test.com')
        self.assertIsNotNone(user.role)
        self.assertEqual(user.role.name, ROLE_STUDENT)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_register_creates_user_profile(self):
        data = {
            'username': 'conperfil',
            'email': 'perfil@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        self.client.post(self.url, data)
        user = User.objects.get(email='perfil@test.com')
        self.assertTrue(hasattr(user, 'profile'))

    def test_register_password_mismatch_returns_400(self):
        data = {
            'username': 'bad',
            'email': 'bad@test.com',
            'password': 'TestPass123!',
            'password2': 'OtroPass456!',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_role_never_null(self):
        data = {
            'username': 'notnull',
            'email': 'notnull@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        self.client.post(self.url, data)
        user = User.objects.get(email='notnull@test.com')
        self.assertIsNotNone(user.role)


# ─── 3. Login ────────────────────────────────────────────────────────────────

class LoginTests(APITestCase):

    def setUp(self):
        create_roles()
        _, teacher_role, _ = create_roles()
        self.user = make_user('login@test.com', 'loginuser', 'TestPass123!', teacher_role)
        self.url = reverse('login')

    def test_login_returns_access_and_refresh(self):
        response = self.client.post(self.url, {
            'email': 'login@test.com',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_returns_user_object_in_body(self):
        response = self.client.post(self.url, {
            'email': 'login@test.com',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        user_data = response.data['user']
        self.assertEqual(user_data['email'], 'login@test.com')
        self.assertEqual(user_data['role'], ROLE_TEACHER)
        self.assertTrue(user_data['is_staff'])
        self.assertFalse(user_data['is_superuser'])

    def test_login_wrong_password_returns_401(self):
        response = self.client.post(self.url, {
            'email': 'login@test.com',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ─── 4. Endpoint /api/auth/me/ ───────────────────────────────────────────────

class MeEndpointTests(APITestCase):

    def setUp(self):
        create_roles()
        _, _, student_role = create_roles()
        self.user = make_user('me@test.com', 'meuser', 'TestPass123!', student_role)
        self.url = reverse('me')

    def _auth(self):
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'email': 'me@test.com',
            'password': 'TestPass123!',
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_me_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_user_data(self):
        self._auth()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'me@test.com')
        self.assertEqual(response.data['role']['name'], ROLE_STUDENT)
        self.assertFalse(response.data['is_staff'])
        self.assertFalse(response.data['is_superuser'])


# ─── 5. Permisos por rol en endpoints ────────────────────────────────────────

class PermissionTests(APITestCase):

    def setUp(self):
        admin_role, teacher_role, student_role = create_roles()

        self.admin   = make_user('admin@p.com',   'adm_p',  'Pass1234!', admin_role)
        self.teacher = make_user('teacher@p.com', 'tch_p',  'Pass1234!', teacher_role)
        self.student = make_user('student@p.com', 'std_p',  'Pass1234!', student_role)

        self.courses_url = '/api/courses/'
        self.users_url   = '/api/users/'
        self.stats_url   = '/api/orders/stats/'

    def _get_token(self, email, password):
        response = self.client.post(reverse('login'), {
            'email': email, 'password': password
        })
        return response.data.get('access')

    def _auth_as(self, user_email, password='Pass1234!'):
        token = self._get_token(user_email, password)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Cursos — teacher puede crear
    def test_teacher_can_create_course(self):
        from learning.models import Language
        lang = Language.objects.create(name='Inglés', code='EN')
        self._auth_as('teacher@p.com')
        response = self.client.post(self.courses_url, {
            'language': lang.id,
            'title': 'Test Course',
            'description': 'Desc',
            'difficulty_level': 'A1',
        })
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
        ])

    # Cursos — student NO puede crear
    def test_student_cannot_create_course(self):
        from learning.models import Language
        lang = Language.objects.create(name='Francés', code='FR')
        self._auth_as('student@p.com')
        response = self.client.post(self.courses_url, {
            'language': lang.id,
            'title': 'Intento ilegal',
            'description': 'Desc',
            'difficulty_level': 'A1',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # /api/users/ — solo admin puede acceder
    def test_admin_can_list_users(self):
        self._auth_as('admin@p.com')
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_access_users_endpoint(self):
        self._auth_as('teacher@p.com')
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_access_users_endpoint(self):
        self._auth_as('student@p.com')
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # /api/orders/stats/ — solo admin
    def test_teacher_cannot_access_order_stats(self):
        self._auth_as('teacher@p.com')
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_access_order_stats(self):
        self._auth_as('student@p.com')
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ─── 6. Migración de datos ────────────────────────────────────────────────────

class MigrationDataTests(TestCase):
    """
    Verifica que los roles canónicos existen tras las migraciones.
    En el entorno de test Django ejecuta todas las migraciones antes de correr.
    """

    def test_canonical_roles_exist(self):
        for role_name in [ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT]:
            self.assertTrue(
                Role.objects.filter(name=role_name).exists(),
                f'El rol "{role_name}" no existe en la base de datos.'
            )

    def test_no_users_with_null_role_after_migration(self):
        """
        Tras la migración, ningún usuario debe tener role=NULL.
        (Este test aplica si ya existen usuarios; si no hay usuarios pasa trivialmente.)
        """
        null_role_count = User.objects.filter(role__isnull=True).count()
        self.assertEqual(
            null_role_count, 0,
            f'Hay {null_role_count} usuarios con role=NULL tras la migración.'
        )
