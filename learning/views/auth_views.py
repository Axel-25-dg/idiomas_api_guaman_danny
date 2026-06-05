from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from learning.serializers import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer


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


class MeView(generics.RetrieveAPIView):
    """
    GET /api/auth/me/
    Devuelve los datos completos del usuario autenticado.
    Android debe llamar este endpoint al iniciar sesión para
    validar el usuario y obtener el rol sin decodificar el JWT.

    Response:
    {
        "id":           1,
        "username":     "danny",
        "email":        "danny@email.com",
        "role":         { "id": 3, "name": "student" },
        "profile":      { "first_name": "", ... },
        "is_staff":     false,
        "is_superuser": false,
        "is_active":    true,
        "created_at":   "2025-06-04T10:00:00Z"
    }
    """
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
