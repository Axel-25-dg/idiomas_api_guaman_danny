from .user_serializer import (
    RoleSerializer,
    UserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    MyTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    StaffUserSerializer,

    RegisterBiometricSerializer,
    LoginBiometricSerializer,
)
from .course_serializer import (
    LanguageSerializer, CourseSerializer, ModuleSerializer,
    LessonSerializer, ExerciseSerializer, ExerciseSafeSerializer,
    ExerciseValidationSerializer,
)
from .progress_serializer import (
    UserProgressSerializer, UserStatsSerializer,
    AchievementSerializer, UserAchievementSerializer,
    GameSubmissionSerializer,
)
# (Serializadores de suscripciones eliminados — venta directa)
from .classroom_serializer import (
    ClassroomSerializer, ClassroomDetailSerializer,
    ClassroomEnrollmentSerializer, JoinClassroomSerializer,
    ClassroomJoinRequestSerializer,
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
from .sales_serializer import (
    CatalogoSerializer, CarritoItemSerializer, CarritoSerializer,
    OrdenDetalleSerializer, OrdenCompraSerializer,
)