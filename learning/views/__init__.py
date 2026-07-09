from .auth_views import (
    RegisterView, LoginView, MeView,
    PasswordResetRequestView, PasswordResetConfirmView, UpdateUserLanguagesView,
    Verify2FAView, RegisterBiometricView, LoginBiometricView
)
from .course_views import LanguageViewSet, CourseViewSet, ModuleViewSet, LessonViewSet, ExerciseViewSet
from .progress_views import (
    UserProgressViewSet, UserStatsViewSet, AchievementViewSet,
    UserAchievementViewSet, RankingViewSet,
)
from .subscription_views import (
    SubscriptionViewSet, UserSubscriptionViewSet, PaymentViewSet, OrderViewSet
)
from .user_views import StaffUserViewSet, AdminStudentViewSet
from .classroom_views import ClassroomViewSet
from .certificate_views import CertificateViewSet
from .resource_views import TeacherResourceViewSet
from .dashboard_views import StudentDashboardView, TeacherDashboardView, AdminDashboardView

from .interaction_views import ReportViewSet,UserFeedbackViewSet, MediaAssetViewSet, UserFavoriteViewSet, UserActivityLogViewSet
from .notification_views import NotificationViewSet, UserNotificationPreferenceViewSet, AnnouncementViewSet
from .system_views import MaintenanceLogViewSet, BackupHistoryViewSet

# ── Nuevos módulos ────────────────────────────────────────────────────────────
from .messaging_views import MessageThreadViewSet, MessageViewSet
from .forum_views import (
    ForumCategoryViewSet, ForumThreadViewSet, ForumPostViewSet,
    ForumReactionViewSet, ForumReportViewSet,
)
from .social_views import SocialPostViewSet, SocialCommentViewSet, SocialReactionViewSet
from .live_session_views import LiveSessionViewSet
from .media_views import MediaFileViewSet, MediaProgressViewSet
from .search_views import GlobalSearchView
