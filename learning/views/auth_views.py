from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from learning.serializers import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Registro de nuevo usuario. No requiere autenticación.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Usuario registrado exitosamente.',
            'user': UserSerializer(user).data
        }, status=201)


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Login con email y password. Devuelve tokens JWT access + refresh.
    Incluye is_staff, is_superuser y role en el payload del JWT.
    """
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
