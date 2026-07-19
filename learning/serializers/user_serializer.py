from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

from learning.models import User, UserProfile, Role, ROLE_STUDENT, ROLE_TEACHER, Language


# ─── Serializers de solo lectura ──────────────────────────────────────────────

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class ProfileLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'code', 'flag_icon_url']



class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    languages_learning_details = ProfileLanguageSerializer(source='languages_learning', many=True, read_only=True)
    languages_teaching_details = ProfileLanguageSerializer(source='languages_teaching', many=True, read_only=True)
    
    languages_learning = serializers.PrimaryKeyRelatedField(many=True, queryset=Language.objects.all(), required=False)
    languages_teaching = serializers.PrimaryKeyRelatedField(many=True, queryset=Language.objects.all(), required=False)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'first_name', 'last_name', 'avatar', 'avatar_url',
            'native_language', 'timezone',
            'languages_learning', 'languages_learning_details',
            'languages_teaching', 'languages_teaching_details'
        ]
        extra_kwargs = {'avatar': {'write_only': True}}

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return obj.avatar_url  # Fallback a la URL manual si existe

    def validate_avatar(self, value):
        if not value:
            return value
        max_size = 2 * 1024 * 1024  # 2 MB
        valid_types = ['image/jpeg', 'image/png', 'image/webp']
        if value.size > max_size:
            raise serializers.ValidationError('La imagen no debe exceder los 2 MB.')
        if value.content_type not in valid_types:
            raise serializers.ValidationError('Solo se permiten imágenes JPEG, PNG y WebP.')
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el usuario autenticado. Soporta actualización de perfil."""
    profile = UserProfileSerializer()
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'profile',
            'is_staff', 'is_superuser', 'is_active',
            'created_at',
        ]
        read_only_fields = ['created_at', 'is_staff', 'is_superuser', 'username', 'email']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Actualizar campos del User (si se enviaron)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        # Actualizar campos del Profile
        if profile_data:
            profile = instance.profile
            languages_learning = profile_data.pop('languages_learning', None)
            languages_teaching = profile_data.pop('languages_teaching', None)

            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

            if languages_learning is not None:
                profile.languages_learning.set(languages_learning)
            if languages_teaching is not None:
                profile.languages_teaching.set(languages_teaching)

        return instance


# ─── JWT ──────────────────────────────────────────────────────────────────────

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extiende el JWT para incluir role, is_staff e is_superuser en el payload.
    Además, devuelve los datos del usuario en el body del response de login.
    """

    remember_me = serializers.BooleanField(default=False, write_only=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claims personalizados dentro del JWT
        token['is_staff']      = user.is_staff
        token['is_superuser']  = user.is_superuser
        token['role']          = user.role.name if user.role else None
        return token

    def validate(self, attrs):
        remember_me = attrs.pop('remember_me', False)
        data = super().validate(attrs)
        
        # Guardar para la vista
        self.remember_me = remember_me
        
        # Añadimos el objeto user al body del response — Android ya no necesita
        # decodificar el JWT para obtener el rol.
        data['user'] = {
            'id':           self.user.id,
            'username':     self.user.username,
            'email':        self.user.email,
            'first_name':   self.user.first_name,
            'last_name':    self.user.last_name,
            'full_name':    f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
            'role':         self.user.role.name if self.user.role else None,
            'is_staff':     self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
        return data


# ─── Registro ─────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    Registro público.
    - Permite configurar username, email, password, first_name, last_name, y role ('student' o 'teacher').
    - Crea UserProfile automáticamente y guarda los nombres.
    """
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(required=False, default='student')

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        role_name = validated_data.pop('role', 'student')

        if role_name not in ['student', 'teacher']:
            role_name = 'student'

        # Obtener el rol correspondiente
        try:
            assigned_role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            raise serializers.ValidationError(
                f'El rol "{role_name}" no existe en la base de datos. '
                'Ejecuta las migraciones pendientes.'
            )

        # Creamos el usuario base
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
        )

        # Asignamos role — User.save() sincroniza is_staff e is_superuser
        user.role = assigned_role
        user.save()

        # Perfil con first_name/last_name
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
            }
        )

        return user


# ─── Password Reset ──────────────────────────────────────────────────────────

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Las contraseñas no coinciden.'})
        return attrs


# ─── Gestión de usuarios Staff (admin only) ───────────────────────────────────

class StaffUserSerializer(serializers.ModelSerializer):
    """
    Gestión de usuarios de personal (teachers, admins).
    Solo accesible por admins desde /api/users/.
    Al asignar role_id, User.save() sincroniza automáticamente is_staff e is_superuser.
    """
    role    = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True,
        required=True,
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
    )

    class Meta:
        model  = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'role_id',
            'is_staff',        # read-only: lo controla User.save()
            'is_superuser',    # read-only: lo controla User.save()
            'is_active',
            'password',
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser']

    def validate(self, attrs):
        # Password requerido solo en creación
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError(
                {'password': 'Se requiere contraseña para crear un usuario.'}
            )
        return attrs

    def create(self, validated_data):
        role     = validated_data.pop('role', None)
        password = validated_data.pop('password', None)

        user = User.objects.create_user(
            username   = validated_data.get('username'),
            email      = validated_data.get('email'),
            password   = password,
            first_name = validated_data.get('first_name', ''),
            last_name  = validated_data.get('last_name', ''),
        )

        # Asignar role y dejar que User.save() sincronice los flags
        user.role      = role
        user.is_active = validated_data.get('is_active', True)
        user.save()

        # Crear perfil si no existe
        UserProfile.objects.get_or_create(user=user)

        return user

    def update(self, instance, validated_data):
        role     = validated_data.pop('role', None)
        password = validated_data.pop('password', None)

        # Actualizar campos simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Actualizar role — User.save() sincronizará is_staff e is_superuser
        if role is not None:
            instance.role = role

        if password:
            instance.set_password(password)

        instance.save()  # <-- sincronización ocurre aquí
        return instance


# ─── Biométrico ────────────────────────────────────────────────────────────────

class RegisterBiometricSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=255)

class LoginBiometricSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=255)
    biometric_token = serializers.CharField(max_length=255)
