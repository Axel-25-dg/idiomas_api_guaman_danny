from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from learning.views import (
    RegisterView, LoginView, MeView,
    PasswordResetRequestView, PasswordResetConfirmView,
    LanguageViewSet, CourseViewSet, ModuleViewSet, LessonViewSet, ExerciseViewSet,
    UserProgressViewSet, UserStatsViewSet, AchievementViewSet, UserAchievementViewSet,
    RankingViewSet,
    SubscriptionViewSet, UserSubscriptionViewSet, PaymentViewSet, OrderViewSet,
    StaffUserViewSet, AdminStudentViewSet,
    ClassroomViewSet, CertificateViewSet, TeacherResourceViewSet,
    StudentDashboardView, TeacherDashboardView, AdminDashboardView,
)

router = DefaultRouter()

# ── Contenido educativo ──────────────────────────────────────────────────────
router.register(r'languages',   LanguageViewSet,  basename='language')
router.register(r'courses',     CourseViewSet,    basename='course')
router.register(r'modules',     ModuleViewSet,    basename='module')
router.register(r'lessons',     LessonViewSet,    basename='lesson')
router.register(r'exercises',   ExerciseViewSet,  basename='exercise')

# ── Progreso y gamificación ──────────────────────────────────────────────────
router.register(r'progress',        UserProgressViewSet,    basename='progress')
router.register(r'stats',           UserStatsViewSet,       basename='stats')
router.register(r'achievements',    AchievementViewSet,     basename='achievement')
router.register(r'my-achievements', UserAchievementViewSet, basename='my-achievement')
router.register(r'ranking',         RankingViewSet,         basename='ranking')

# ── Pagos / Suscripciones ────────────────────────────────────────────────────
router.register(r'subscriptions',    SubscriptionViewSet,     basename='subscription')
router.register(r'my-subscriptions', UserSubscriptionViewSet, basename='my-subscription')
router.register(r'payments',         PaymentViewSet,          basename='payment')
router.register(r'orders',           OrderViewSet,            basename='order')

# ── Gestión de usuarios ──────────────────────────────────────────────────────
router.register(r'users',           StaffUserViewSet,    basename='users')
router.register(r'admin-students',  AdminStudentViewSet, basename='admin-students')

# ── Nuevos módulos ───────────────────────────────────────────────────────────
router.register(r'classrooms',   ClassroomViewSet,       basename='classroom')
router.register(r'certificates', CertificateViewSet,     basename='certificate')
router.register(r'resources',    TeacherResourceViewSet, basename='resource')

urlpatterns = [
    # ── Autenticación ────────────────────────────────────────────────────────
    path('auth/register/',      RegisterView.as_view(),      name='register'),
    path('auth/login/',         LoginView.as_view(),         name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),  name='token_refresh'),
    path('auth/me/',            MeView.as_view(),            name='me'),

    # ── Password Reset ───────────────────────────────────────────────────────
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # ── Dashboards ───────────────────────────────────────────────────────────
    path('dashboard/student/',  StudentDashboardView.as_view(),  name='dashboard-student'),
    path('dashboard/teacher/',  TeacherDashboardView.as_view(),  name='dashboard-teacher'),
    path('dashboard/admin/',    AdminDashboardView.as_view(),    name='dashboard-admin'),

    # ── Router ───────────────────────────────────────────────────────────────
    path('', include(router.urls)),
]
