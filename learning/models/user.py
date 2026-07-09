import uuid
from pathlib import Path
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


def avatar_upload_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f'avatars/user_{instance.user_id}/{uuid.uuid4()}{ext}'


# Nombres canónicos de roles — fuente de verdad
ROLE_ADMIN   = 'admin'
ROLE_TEACHER = 'teacher'
ROLE_STUDENT = 'student'

VALID_ROLES = {ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT}


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # 'admin' | 'teacher' | 'student'

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    deleted_at  = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    # ─────────────────────────────────────────────────────────────────
    # Sincronización automática de flags según role
    # Centralizada aquí — NO se duplica en serializers ni views.
    #
    #   admin   → is_staff=True,  is_superuser=True
    #   teacher → is_staff=True,  is_superuser=False
    #   student → is_staff=False, is_superuser=False
    #   None    → is_staff=False, is_superuser=False  (fallback seguro)
    # ─────────────────────────────────────────────────────────────────
    def sync_flags_from_role(self):
        """Sincroniza is_staff / is_superuser a partir del role actual.
        Llama explícitamente antes de save() cuando el role cambia."""
        role_name = self.role.name if self.role else None

        if role_name == ROLE_ADMIN:
            self.is_staff      = True
            self.is_superuser  = True
        elif role_name == ROLE_TEACHER:
            self.is_staff      = True
            self.is_superuser  = False
        else:
            # student o sin rol
            self.is_staff      = False
            self.is_superuser  = False

    def save(self, *args, **kwargs):
        # Sincroniza flags SOLO cuando hay un role FK asignado.
        # Si role_id es None, NO toca is_staff / is_superuser
        # → Permite que create_superuser() y migraciones funcionen sin problemas.
        if self.role_id is not None:
            try:
                self.sync_flags_from_role()
            except Exception:
                # Protección ante migraciones donde la tabla Role aún no exista
                pass
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])


class UserProfile(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name      = models.CharField(max_length=100, blank=True)
    last_name       = models.CharField(max_length=100, blank=True)
    avatar          = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    avatar_url      = models.URLField(blank=True, null=True)
    avatar_file     = models.ForeignKey(
        'learning.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profile_avatars',
    )
    native_language = models.CharField(max_length=50, blank=True)
    timezone        = models.CharField(max_length=50, default='America/Guayaquil')
    is_2fa_enabled  = models.BooleanField(default=False)
    updated_at      = models.DateTimeField(auto_now=True)

    languages_learning = models.ManyToManyField(
        'learning.Language', 
        blank=True, 
        related_name='student_profiles'
    )
    languages_teaching = models.ManyToManyField(
        'learning.Language', 
        blank=True, 
        related_name='teacher_profiles'
    )

    class Meta:
        ordering = ['user']

    def __str__(self):
        return f'Perfil de {self.user.email}'

    @property
    def avatar_file_url(self):
        if self.avatar_file and self.avatar_file.file:
            return self.avatar_file.file.url
        return self.avatar_url
