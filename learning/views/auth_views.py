from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model

from learning.serializers import (
    RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from learning.services.email_service import send_welcome_email, send_password_reset_email

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Registro público. Crea usuario con role='student' automáticamente.
    No requiere autenticación.
    """
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Enviar correo de bienvenida
        try:
            send_welcome_email(user)
        except Exception:
            # No bloqueamos el registro si el correo falla
            pass

        return Response({
            'message': 'Usuario registrado exitosamente.',
            'user': UserSerializer(user).data,
        }, status=201)


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Login con email y password.

    Response:
    {
        "access":  "<jwt>",
        "refresh": "<jwt>",
        "user": {
            "id":           1,
            "username":     "danny",
            "email":        "danny@email.com",
            "role":         "student",
            "is_staff":     false,
            "is_superuser": false
        }
    }

    El JWT sigue incluyendo los mismos claims personalizados:
    is_staff, is_superuser, role — retrocompatible con Android actual.
    """
    serializer_class   = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/auth/me/  — Datos del usuario autenticado
    PATCH /api/auth/me/  — Actualizar datos (incluyendo avatar)

    Para subir el avatar, enviar un Form-Data con:
    - first_name: string
    - last_name: string
    - profile.avatar: File
    """
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(generics.GenericAPIView):
    """
    POST /api/auth/password-reset/
    Solicita un restablecimiento de contraseña. Envía un correo con el link.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # El link apunta al frontend (configurado en settings.py)
            # Ejemplo: http://localhost:3000/reset-password?uid=...&token=...
            reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            
            send_password_reset_email(user, reset_link)
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            pass
            
        return Response({
            'message': 'Si el correo existe en nuestra base de datos, recibirás un enlace para restablecer tu contraseña.'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    POST /api/auth/password-reset-confirm/
    Confirma el cambio de contraseña usando el token y uid.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response({'message': 'Contraseña restablecida exitosamente.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'El token es inválido o ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Datos de restablecimiento inválidos.'}, status=status.HTTP_400_BAD_REQUEST)
