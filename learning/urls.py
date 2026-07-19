from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from learning.views import (
    RegisterView, LoginView, MeView,
    PasswordResetRequestView, PasswordResetConfirmView, UpdateUserLanguagesView,
    RegisterBiometricView, LoginBiometricView,
    LanguageViewSet, CourseViewSet, ModuleViewSet, LessonViewSet, ExerciseViewSet,
    UserProgressViewSet, UserStatsViewSet, AchievementViewSet, UserAchievementViewSet,
    RankingViewSet, GameSubmitResultView,
    # (Suscripciones eliminadas)
    StaffUserViewSet, AdminStudentViewSet,
    ClassroomViewSet, CertificateViewSet, TeacherResourceViewSet,
    StudentDashboardView, TeacherDashboardView, AdminDashboardView,

    # Interacción y sistema
    ReportViewSet, UserFeedbackViewSet, MediaAssetViewSet, UserFavoriteViewSet, UserActivityLogViewSet,
    AnnouncementViewSet, NotificationViewSet, UserNotificationPreferenceViewSet,
    MaintenanceLogViewSet, BackupHistoryViewSet,

    # Nuevos módulos
    MessageThreadViewSet, MessageViewSet,
    ForumCategoryViewSet, ForumThreadViewSet, ForumPostViewSet,
    ForumReactionViewSet, ForumReportViewSet,
    SocialPostViewSet, SocialCommentViewSet, SocialReactionViewSet,
    LiveSessionViewSet,
    MediaFileViewSet, MediaProgressViewSet,
    GlobalSearchView,
    CatalogoViewSet, CarritoViewSet, OrdenCompraViewSet,
)
from learning.views import system_views, interaction_views, notification_views
# Stripe/Suscripciones eliminados — se usa venta directa

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

# ── Pagos / Suscripciones (Deprecado - Transición a Ventas Directas) ─────────

# ── E-Commerce y Ventas Directas ─────────────────────────────────────────────
router.register(r'catalogo',        CatalogoViewSet,         basename='catalogo')
router.register(r'carrito',         CarritoViewSet,          basename='carrito')
router.register(r'ordenes-compra',  OrdenCompraViewSet,      basename='orden-compra')

# ── Gestión de usuarios ──────────────────────────────────────────────────────
router.register(r'users',           StaffUserViewSet,    basename='users')
router.register(r'admin-students',  AdminStudentViewSet, basename='admin-students')

# ── Nuevos módulos ───────────────────────────────────────────────────────────
router.register(r'classrooms',   ClassroomViewSet,       basename='classroom')
router.register(r'certificates', CertificateViewSet,     basename='certificate')
router.register(r'resources',    TeacherResourceViewSet, basename='resource')

# ── Sistema, Notificaciones e Interacciones ──────────────────────────────────
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'preferences',   UserNotificationPreferenceViewSet, basename='preference')

router.register(r'maintenance',   MaintenanceLogViewSet, basename='maintenance')
router.register(r'backups',       BackupHistoryViewSet, basename='backup')

router.register(r'favorites', UserFavoriteViewSet, basename='favorite')
router.register(r'reports',   ReportViewSet,       basename='report')
router.register(r'feedbacks', UserFeedbackViewSet, basename='feedback')
router.register(r'media',     MediaAssetViewSet,   basename='media')
router.register(r'activity-logs', UserActivityLogViewSet, basename='activity-log')

# ── Mensajería ───────────────────────────────────────────────────────────────
router.register(r'threads',  MessageThreadViewSet, basename='thread')
router.register(r'messages', MessageViewSet,       basename='message')

# ── Foro ─────────────────────────────────────────────────────────────────────
router.register(r'forum-categories', ForumCategoryViewSet, basename='forum-category')
router.register(r'forum-threads',    ForumThreadViewSet,   basename='forum-thread')
router.register(r'forum-posts',      ForumPostViewSet,     basename='forum-post')
router.register(r'forum-reactions',  ForumReactionViewSet, basename='forum-reaction')
router.register(r'forum-reports',    ForumReportViewSet,   basename='forum-report')

# ── Feed Social ──────────────────────────────────────────────────────────────
router.register(r'social-posts',     SocialPostViewSet,     basename='social-post')
router.register(r'social-comments',  SocialCommentViewSet,  basename='social-comment')
router.register(r'social-reactions', SocialReactionViewSet, basename='social-reaction')

# ── Videotutoría ─────────────────────────────────────────────────────────────
router.register(r'live-sessions', LiveSessionViewSet, basename='live-session')

# ── Multimedia ───────────────────────────────────────────────────────────────
router.register(r'media-files',    MediaFileViewSet,    basename='media-file')
router.register(r'media-progress', MediaProgressViewSet, basename='media-progress')


urlpatterns = [
    # ── Autenticación ────────────────────────────────────────────────────────
    path('auth/register/',      RegisterView.as_view(),      name='register'),
    path('auth/login/',         LoginView.as_view(),         name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),  name='token_refresh'),
    path('auth/me/',            MeView.as_view(),            name='me'),
    path('auth/profile/update-languages/', UpdateUserLanguagesView.as_view(), name='update_languages'),
    path('auth/biometric/register/', RegisterBiometricView.as_view(), name='register_biometric'),
    path('auth/biometric/login/', LoginBiometricView.as_view(), name='login_biometric'),

    # ── Password Reset ───────────────────────────────────────────────────────
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # ── Gamificación para juegos Flutter ────────────────────────────────────
    path('games/submit-result/', GameSubmitResultView.as_view(), name='game-submit-result'),

    # ── Dashboards ───────────────────────────────────────────────────────────
    path('dashboard/student/',  StudentDashboardView.as_view(),  name='dashboard-student'),
    path('dashboard/teacher/',  TeacherDashboardView.as_view(),  name='dashboard-teacher'),
    path('dashboard/admin/',    AdminDashboardView.as_view(),    name='dashboard-admin'),

    # ── Router ───────────────────────────────────────────────────────────────
    path('', include(router.urls)),

    # ── Búsqueda global ──────────────────────────────────────────────────────
    path('search/', GlobalSearchView.as_view(), name='search'),

    # ── Stripe (Eliminado - se usa venta directa) ───────────────────────────
]