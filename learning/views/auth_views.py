import uuid
from datetime import timedelta
import random
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from learning.serializers import (
    RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    RegisterBiometricSerializer, LoginBiometricSerializer,
    UserProfileSerializer,
)
from learning.services.email_service import send_welcome_email, send_password_reset_pin_email
from seguridad_acceso.models import PasswordReset, BiometricDevice

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            send_welcome_email(user)
        except Exception:
            pass

        return Response({
            'message': 'Usuario registrado exitosamente.',
            'user': UserSerializer(user).data,
        }, status=201)


class LoginView(TokenObtainPairView):
    serializer_class   = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            
        data = serializer.validated_data
        user = serializer.user
        
        # "Remember me" option
        if getattr(serializer, 'remember_me', False):
            refresh = RefreshToken.for_user(user)
            refresh.set_exp(lifetime=timedelta(days=30))
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)

        return Response(data, status=status.HTTP_200_OK)


class RegisterBiometricView(generics.GenericAPIView):
    serializer_class = RegisterBiometricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device_id = serializer.validated_data['device_id']
        
        biometric_token = uuid.uuid4().hex
        
        BiometricDevice.objects.update_or_create(
            user=request.user,
            device_id=device_id,
            defaults={'biometric_token': biometric_token, 'is_active': True}
        )
        
        return Response({'biometric_token': biometric_token, 'message': 'Dispositivo registrado para inicio de sesión biométrico.'})


class LoginBiometricView(generics.GenericAPIView):
    serializer_class = LoginBiometricSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device_id = serializer.validated_data['device_id']
        biometric_token = serializer.validated_data['biometric_token']
        
        try:
            device = BiometricDevice.objects.get(device_id=device_id, biometric_token=biometric_token, is_active=True)
            device.last_used = timezone.now()
            device.save()
            
            user = device.user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.name if user.role else None,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                }
            })
        except BiometricDevice.DoesNotExist:
            return Response({'error': 'Token biométrico inválido o dispositivo no registrado.'}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            code = f"{random.randint(100000, 999999)}"
            
            PasswordReset.objects.create(
                user=user,
                token=code,
                expires_at=timezone.now() + timedelta(minutes=15)
            )
            
            try:
                send_password_reset_pin_email(user, code)
            except Exception:
                pass
        except User.DoesNotExist:
            pass
            
        return Response({
            'message': 'Si el correo existe, recibirás un PIN de 6 dígitos para restablecer tu contraseña.'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
            reset_obj = PasswordReset.objects.filter(
                user=user, token=code, is_used=False, expires_at__gt=timezone.now()
            ).latest('created_at')
            
            user.set_password(password)
            user.save()
            
            reset_obj.is_used = True
            reset_obj.save()
            
            return Response({'message': 'Contraseña restablecida exitosamente.'}, status=status.HTTP_200_OK)
        except (User.DoesNotExist, PasswordReset.DoesNotExist):
            return Response({'error': 'PIN inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserLanguagesView(generics.GenericAPIView):
    """
    PATCH /api/auth/profile/update-languages/

    Para estudiantes: actualiza languages_learning (respeta límite del plan).
    Para profesores:  actualiza languages_teaching.

    Body para estudiante:
        { "languages_learning": [1, 2, 3] }

    Body para profesor:
        { "languages_teaching": [1] }
    """
    serializer_class   = UserProfileSerializer          # requerido por drf-spectacular
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        from learning.models import UserSubscription

        profile = request.user.profile
        role    = request.user.role.name if request.user.role else None

        if role in ['student', 'premium_student']:
            if 'languages_learning' not in request.data:
                return Response(
                    {"error": "Se requiere el campo 'languages_learning'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_ids = request.data.get('languages_learning', [])

            # Verificar límite del plan de suscripción
            today = timezone.now().date()
            sub = UserSubscription.objects.filter(
                user=request.user, is_active=True, end_date__gte=today
            ).select_related('subscription').order_by('-end_date').first()

            max_lang = sub.subscription.max_languages if sub else 1  # plan gratuito → 1

            if max_lang != 0 and len(new_ids) > max_lang:
                plan_name = sub.subscription.name if sub else 'gratuito'
                return Response(
                    {
                        "error": (
                            f"Tu plan '{plan_name}' permite aprender máximo {max_lang} idioma(s). "
                            f"Actualiza tu suscripción para agregar más."
                        ),
                        "max_languages": max_lang,
                        "is_premium": sub is not None,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "message":       "Idiomas de aprendizaje actualizados.",
                "data":          serializer.data,
                "max_languages": max_lang,
            })

        elif role in ['teacher', 'assistant_teacher']:
            if 'languages_teaching' not in request.data:
                return Response(
                    {"error": "Se requiere el campo 'languages_teaching'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Idiomas de enseñanza actualizados.", "data": serializer.data})

        return Response(
            {"error": "Rol no autorizado para esta acción."},
            status=status.HTTP_400_BAD_REQUEST,
        )
