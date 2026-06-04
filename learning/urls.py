from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from learning.views import (
    RegisterView, LoginView,
    LanguageViewSet, CourseViewSet, ModuleViewSet, LessonViewSet, ExerciseViewSet,
    UserProgressViewSet, UserStatsViewSet, AchievementViewSet, UserAchievementViewSet,
    SubscriptionViewSet, UserSubscriptionViewSet, PaymentViewSet, OrderViewSet, StaffUserViewSet,
)

router = DefaultRouter()

# ── Contenido educativo ──────────────────────────────────────────────────────
router.register(r'languages',    LanguageViewSet,  basename='language')
router.register(r'courses',      CourseViewSet,    basename='course')
router.register(r'modules',      ModuleViewSet,    basename='module')
router.register(r'lessons',      LessonViewSet,    basename='lesson')
router.register(r'exercises',    ExerciseViewSet,  basename='exercise')

# ── Progreso y gamificación ──────────────────────────────────────────────────
router.register(r'progress',         UserProgressViewSet,   basename='progress')
router.register(r'stats',            UserStatsViewSet,      basename='stats')
router.register(r'achievements',     AchievementViewSet,    basename='achievement')
router.register(r'my-achievements',  UserAchievementViewSet, basename='my-achievement')

# ── Pagos / Suscripciones ────────────────────────────────────────────────────
router.register(r'subscriptions',    SubscriptionViewSet,     basename='subscription')
router.register(r'my-subscriptions', UserSubscriptionViewSet, basename='my-subscription')
router.register(r'payments',         PaymentViewSet,          basename='payment')
router.register(r'users',            StaffUserViewSet,        basename='users')
router.register(r'orders',           OrderViewSet,            basename='order')

urlpatterns = [
    # Autenticación
    path('auth/register/',      RegisterView.as_view(),  name='register'),
    path('auth/login/',         LoginView.as_view(),     name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Todas las rutas del router
    path('', include(router.urls)),
]
