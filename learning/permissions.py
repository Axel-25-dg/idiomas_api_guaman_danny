"""
Permisos personalizados — arquitectura híbrida role + is_staff + is_superuser

Jerarquía:
  admin   → role='admin',   is_staff=True,  is_superuser=True
  teacher → role='teacher', is_staff=True,  is_superuser=False
  student → role='student', is_staff=False, is_superuser=False

Regla de diseño:
  - Los permisos SIEMPRE validan autenticación primero.
  - Se comprueba role.name para la lógica de negocio.
  - Se mantiene is_staff / is_superuser para compatibilidad con Django admin.
  - SAFE_METHODS (GET, HEAD, OPTIONS) = solo requieren IsAuthenticated salvo
    que la vista requiera más restricción explícita.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from learning.models import ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT


def _get_role(user) -> str | None:
    """Devuelve el nombre del rol del usuario o None de forma segura.
    Si no tiene role FK pero tiene is_superuser, se trata como admin.
    Si no tiene role FK pero tiene is_staff, se trata como teacher."""
    try:
        if user.role_id:
            return user.role.name
    except Exception:
        pass
    # Fallback por flags de Django — retrocompatibilidad
    if user.is_superuser:
        return ROLE_ADMIN
    if user.is_staff:
        return ROLE_TEACHER
    return ROLE_STUDENT


# ─── Permisos atómicos ────────────────────────────────────────────────────────

class IsAdmin(BasePermission):
    """Solo usuarios con role='admin' (is_superuser=True, is_staff=True)."""
    message = 'Se requiere rol de administrador.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and _get_role(request.user) == ROLE_ADMIN
        )


class IsTeacher(BasePermission):
    """Solo usuarios con role='teacher' (is_staff=True, is_superuser=False)."""
    message = 'Se requiere rol de profesor.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and _get_role(request.user) == ROLE_TEACHER
        )


class IsStudent(BasePermission):
    """Solo usuarios con role='student'."""
    message = 'Se requiere rol de estudiante.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and _get_role(request.user) == ROLE_STUDENT
        )


# ─── Permisos combinados ──────────────────────────────────────────────────────

class IsTeacherOrAdmin(BasePermission):
    """Permite acceso a teachers y admins (ambos tienen is_staff=True)."""
    message = 'Se requiere rol de profesor o administrador.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        role = _get_role(request.user)
        return role in (ROLE_TEACHER, ROLE_ADMIN)


class IsAdminOrReadOnly(BasePermission):
    """
    Lectura: cualquier usuario autenticado.
    Escritura (POST/PUT/PATCH/DELETE): solo admin.

    Mantiene compatibilidad con las views actuales que la usan.
    Internamente usa role='admin' en lugar de solo is_staff,
    pero sigue siendo retrocompatible porque admin tiene is_staff=True.
    """
    message = 'Se requiere rol de administrador para esta operación.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return _get_role(request.user) == ROLE_ADMIN


class IsTeacherOrAdminOrReadOnly(BasePermission):
    """
    Lectura: cualquier usuario autenticado.
    Escritura: teacher o admin.

    Usar en Courses, Modules, Lessons, Exercises —
    el profesor puede gestionar contenido educativo.
    """
    message = 'Se requiere rol de profesor o administrador para esta operación.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        role = _get_role(request.user)
        return role in (ROLE_TEACHER, ROLE_ADMIN)
