from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from learning.models import User, Language, Course, Module, Lesson, Exercise, UserStats, Catalogo, Carrito, OrdenCompra
from datetime import date, timedelta

class InteractiveFeaturesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='student', email='student@example.com', password='StudentPass123!'
        )
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='AdminPass123!'
        )
        self.lang = Language.objects.create(name='Español', code='ES')
        self.course = Course.objects.create(title='Curso Test', language=self.lang)
        self.module = Module.objects.create(title='Modulo 1', course=self.course, order=1)
        self.lesson = Lesson.objects.create(title='Lección 1', module=self.module, order=1)
        
        # Ejercicio Fill in the blank
        self.exercise = Exercise.objects.create(
            lesson=self.lesson,
            question_text="Last night we ____ (walk) to the cinema.",
            exercise_type="fill_blank",
            correct_answer="walked"
        )
        
    def test_exercise_hides_correct_answer_for_student(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('exercise-detail', kwargs={'pk': self.exercise.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # student shouldn't see the correct answer
        self.assertNotIn('correct_answer', response.data)
        
    def test_exercise_shows_correct_answer_for_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('exercise-detail', kwargs={'pk': self.exercise.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('correct_answer', response.data)
        
    def test_exercise_validation_success_and_streak(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('exercise-validar', kwargs={'pk': self.exercise.id})
        
        # Test incorrect answer
        response = self.client.post(url, {'respuesta_usuario': 'walk'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['es_correcto'])
        
        # Test correct answer
        response = self.client.post(url, {'respuesta_usuario': 'walked'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['es_correcto'])
        
        # Check that score and streak were updated
        stats = UserStats.objects.get(user=self.student)
        self.assertEqual(stats.total_xp, 10)
        self.assertEqual(stats.current_streak, 1)
        self.assertEqual(stats.last_activity_date, date.today())
        
    def test_sales_flow(self):
        # Create product in catalog
        product = Catalogo.objects.create(
            titulo='Curso Pro',
            tipo='curso',
            precio=99.99,
            curso=self.course
        )
        
        self.client.force_authenticate(user=self.student)
        
        # Get cart
        url_cart = reverse('carrito-list')
        response = self.client.get(url_cart)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Add to cart
        url_add = reverse('carrito-agregar')
        response = self.client.post(url_add, {'producto_id': product.id, 'cantidad': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Purchase
        url_checkout = reverse('carrito-comprar')
        response = self.client.post(url_checkout)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total'], '99.99')
        self.assertEqual(response.data['estado'], 'pagada')
        
        # Verify order was saved
        self.assertTrue(OrdenCompra.objects.filter(estudiante=self.student, estado='pagada').exists())
