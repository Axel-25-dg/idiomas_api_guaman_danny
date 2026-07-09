from .user_serializer import (
    RoleSerializer,
    UserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    MyTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    StaffUserSerializer,
    Verify2FASerializer,
    RegisterBiometricSerializer,
    LoginBiometricSerializer,
)
from .course_serializer import (
    LanguageSerializer, CourseSerializer, ModuleSerializer,
    LessonSerializer, ExerciseSerializer,
)
from .progress_serializer import (
    UserProgressSerializer, UserStatsSerializer,
    AchievementSerializer, UserAchievementSerializer,
)
from .subscription_serializer import (
    SubscriptionSerializer, UserSubscriptionSerializer, PaymentSerializer,
)
from .order_serializer import OrderSerializer
from .classroom_serializer import (
    ClassroomSerializer, ClassroomDetailSerializer,
    ClassroomEnrollmentSerializer, JoinClassroomSerializer,
)
from .certificate_serializer import (
    CertificateSerializer, CertificateCreateSerializer, CertificateIssueSerializer,
)
from .resource_serializer import TeacherResourceSerializer

from .interaction_serializers import (
    UserFavoriteSerializer,
    UserFeedbackSerializer,
    MediaAssetSerializer,
    ReportSerializer,
    UserActivityLogSerializer,
)
from .notification_serializers import (
    AnnouncementSerializer,
    NotificationSerializer,
    UserNotificationPreferenceSerializer,
)
from .system_serializers import (
    MaintenanceLogSerializer,
    BackupHistorySerializer,
)

# ── Nuevos módulos ────────────────────────────────────────────────────────────
from .messaging_serializer import (
    MessageThreadSerializer, MessageSerializer, MessageAttachmentSerializer,
)
from .forum_serializer import (
    ForumCategorySerializer, ForumThreadSerializer, ForumPostSerializer,
    ForumReactionSerializer, ForumReportSerializer,
)
from .social_serializer import (
    SocialPostSerializer, SocialCommentSerializer, SocialReactionSerializer,
)
from .live_session_serializer import (
    LiveSessionSerializer, LiveSessionDetailSerializer, LiveParticipantSerializer,
)
from .media_serializer import MediaFileSerializer, MediaProgressSerializer