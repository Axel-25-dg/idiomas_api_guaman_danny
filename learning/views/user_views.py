from rest_framework import viewsets, permissions
from learning.models import User
from learning.serializers import StaffUserSerializer
from learning.pagination import StandardPagination


class StaffUserViewSet(viewsets.ModelViewSet):
    """
    GET    /api/users/         — Lista solo usuarios de personal
    POST   /api/users/         — Crea un nuevo miembro de personal
    GET    /api/users/{id}/    — Detalle de usuario
    PATCH  /api/users/{id}/    — Actualiza parcialmente un usuario de personal
    """
    serializer_class = StaffUserSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = StandardPagination

    def get_queryset(self):
        return User.objects.filter(is_staff=True).select_related('role')

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
