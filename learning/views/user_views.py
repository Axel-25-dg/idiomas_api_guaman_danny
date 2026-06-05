from rest_framework import viewsets
from learning.models import User
from learning.serializers import StaffUserSerializer
from learning.pagination import StandardPagination
from learning.permissions import IsAdmin


class StaffUserViewSet(viewsets.ModelViewSet):
    """
    Gestión de usuarios de personal (teachers y admins).
    Solo accesible por administradores (role='admin').

    GET    /api/users/         — Lista teachers y admins
    POST   /api/users/         — Crea un nuevo miembro de personal
    GET    /api/users/{id}/    — Detalle
    PATCH  /api/users/{id}/    — Actualiza parcialmente
    DELETE /api/users/{id}/    — Elimina

    Cuando se asigna role_id, User.save() sincroniza
    automáticamente is_staff e is_superuser.
    """
    serializer_class   = StaffUserSerializer
    permission_classes = [IsAdmin]
    pagination_class   = StandardPagination

    def get_queryset(self):
        # Lista solo staff (teachers y admins), no students
        return User.objects.filter(is_staff=True).select_related('role')
