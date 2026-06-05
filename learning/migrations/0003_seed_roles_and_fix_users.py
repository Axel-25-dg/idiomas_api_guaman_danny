"""
Migración 0003 — Seed de roles y corrección de usuarios existentes
===================================================================

SEGURA para producción:
  - No elimina ninguna tabla ni columna.
  - No elimina ningún usuario.
  - Solo opera con datos (RunPython).
  - Totalmente reversible (reverse_migration).
  - Depende de 0002_order (la migración de modelo Order ya en producción).

Acciones:
  1. Crea los roles canónicos: admin, teacher, student (si no existen).
  2. Normaliza nombres alternativos en BD:
       profesor/Profesor  → teacher
       estudiante/Alumno  → student
       administrador      → admin
  3. Asigna roles a usuarios existentes según sus flags:
       is_superuser=True              → admin
       is_staff=True, superuser=False → teacher
       role=NULL                      → student
  4. Sincroniza is_staff e is_superuser para que coincidan con el rol.

REVERSIÓN:
  - Elimina los tres roles creados solo si no tienen usuarios asignados.
"""

from django.db import migrations


# Mapa de nombres alternativos → nombre canónico
ALIAS_MAP = {
    'profesor':      'teacher',
    'Profesor':      'teacher',
    'teacher':       'teacher',
    'Teacher':       'teacher',
    'admin':         'admin',
    'Admin':         'admin',
    'administrador': 'admin',
    'Administrador': 'admin',
    'student':       'student',
    'Student':       'student',
    'estudiante':    'student',
    'Estudiante':    'student',
    'alumno':        'student',
    'Alumno':        'student',
}

CANONICAL_ROLES = ['admin', 'teacher', 'student']


def forward_migration(apps, schema_editor):
    Role = apps.get_model('learning', 'Role')
    User = apps.get_model('learning', 'User')

    # ── 1. Crear roles canónicos ───────────────────────────────────────────
    role_objects = {}
    for role_name in CANONICAL_ROLES:
        role_obj, _ = Role.objects.get_or_create(name=role_name)
        role_objects[role_name] = role_obj

    # ── 2. Normalizar roles con nombres alternativos ──────────────────────
    for role in list(Role.objects.all()):
        canonical = ALIAS_MAP.get(role.name)
        if canonical and role.name != canonical:
            canonical_role = role_objects[canonical]
            # Reasignar usuarios al rol canónico antes de borrar el alias
            User.objects.filter(role=role).update(role=canonical_role)
            role.delete()

    # Refrescar referencias tras posibles eliminaciones
    for role_name in CANONICAL_ROLES:
        role_objects[role_name] = Role.objects.get(name=role_name)

    admin_role   = role_objects['admin']
    teacher_role = role_objects['teacher']
    student_role = role_objects['student']

    # ── 3. Asignar roles a usuarios sin rol ───────────────────────────────
    for user in User.objects.filter(role__isnull=True):
        if user.is_superuser:
            user.role = admin_role
        elif user.is_staff:
            user.role = teacher_role
        else:
            user.role = student_role
        user.save(update_fields=['role'])

    # ── 4. Sincronizar is_staff / is_superuser según el rol asignado ──────
    #   admin   → is_staff=True,  is_superuser=True
    #   teacher → is_staff=True,  is_superuser=False
    #   student → is_staff=False, is_superuser=False
    User.objects.filter(role=admin_role).update(
        is_staff=True, is_superuser=True
    )
    User.objects.filter(role=teacher_role).update(
        is_staff=True, is_superuser=False
    )
    User.objects.filter(role=student_role).update(
        is_staff=False, is_superuser=False
    )


def reverse_migration(apps, schema_editor):
    """
    Reversión conservadora:
    - No elimina usuarios.
    - Solo elimina los roles canónicos si no tienen usuarios asignados.
    """
    Role = apps.get_model('learning', 'Role')

    for role_name in CANONICAL_ROLES:
        try:
            role = Role.objects.get(name=role_name)
            if not role.users.exists():
                role.delete()
        except Role.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0002_order'),
    ]

    operations = [
        migrations.RunPython(
            forward_migration,
            reverse_code=reverse_migration,
        ),
    ]
