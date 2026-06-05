<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/UTE_logo.svg/512px-UTE_logo.svg.png" width="160" alt="Universidad UTE"/>

<br/>
<br/>

# JumpUp UTE — LanguageAPI

**Backend REST para Plataforma de Aprendizaje de Idiomas**

Desarrollado con Django y Django REST Framework

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.14+-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Authentication-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

</div>

---

## Tabla de Contenido

- [Descripción](#descripción)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Sistema de Roles y Permisos](#sistema-de-roles-y-permisos)
- [Modelo de Base de Datos](#modelo-de-base-de-datos)
- [Endpoints de la API](#endpoints-de-la-api)
- [Panel de Administración Django](#panel-de-administración-django)
- [Tecnologías](#tecnologías)
- [Instalación](#instalación)
- [Deploy con GitHub Actions](#deploy-con-github-actions)
- [Testing](#testing)
- [Autor](#autor)

---

## Descripción

**JumpUp UTE** es un backend REST completo para una plataforma de aprendizaje de idiomas inspirada en Duolingo y Babbel. Construido con Django y Django REST Framework, implementa autenticación JWT, un sistema de roles profesional y PostgreSQL como motor de base de datos.

El sistema gestiona tres paneles independientes para Android:

| Panel | Rol | Acceso |
|---|---|---|
| **Admin Dashboard** | `admin` | Gestión total: usuarios, suscripciones, estadísticas, configuración |
| **Teacher Dashboard** | `teacher` | Contenido educativo: cursos, lecciones, ejercicios |
| **Student Dashboard** | `student` | Aprendizaje: progreso, logros, suscripciones propias |

---

## Arquitectura del Proyecto

```
aplicacionidion_idiomas_guaman_danny/
│
├── config/
│   ├── settings.py             # JWT, CORS, base de datos, DRF config
│   ├── urls.py                 # URLs raíz: /admin/, /api/
│   ├── wsgi.py
│   └── asgi.py
│
├── learning/                   # Aplicación principal
│   │
│   ├── models/
│   │   ├── user.py             # Role, User (con sync_flags_from_role), UserProfile
│   │   ├── language.py         # Language
│   │   ├── course.py           # Course, Module, Lesson, Exercise
│   │   ├── progress.py         # UserProgress, UserStats, Achievement, UserAchievement
│   │   └── subscription.py     # Subscription, UserSubscription, Payment, Order
│   │
│   ├── serializers/
│   │   ├── user_serializer.py  # Register, Login (con user en body), Me, StaffUser
│   │   ├── course_serializer.py
│   │   ├── progress_serializer.py
│   │   ├── subscription_serializer.py
│   │   └── order_serializer.py
│   │
│   ├── views/
│   │   ├── auth_views.py       # RegisterView, LoginView, MeView
│   │   ├── course_views.py     # Languages, Courses, Modules, Lessons, Exercises
│   │   ├── progress_views.py   # Progress, Stats, Achievements
│   │   ├── subscription_views.py  # Subscriptions, Payments, Orders
│   │   └── user_views.py       # StaffUserViewSet (solo admin)
│   │
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_order.py
│   │   └── 0003_seed_roles_and_fix_users.py  # Seed roles + fix flags producción
│   │
│   ├── tests/
│   │   ├── test_api.py                       # Tests originales (6 tests)
│   │   └── test_roles_and_permissions.py     # Tests de roles/permisos (23 tests)
│   │
│   ├── admin.py                # Todos los modelos registrados en /admin/
│   ├── urls.py                 # DefaultRouter + auth/me/
│   ├── pagination.py           # 10 items/página, máx 100
│   ├── permissions.py          # IsAdmin, IsTeacher, IsStudent, IsTeacherOrAdmin, etc.
│   └── filters.py              # Filtros con django-filter
│
├── .github/workflows/
│   └── deploy.yml              # CI/CD: push → SSH → migrate → restart gunicorn
│
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Sistema de Roles y Permisos

### Arquitectura híbrida (role + is_staff + is_superuser)

```
ADMIN
├── role.name    = "admin"
├── is_staff     = True
└── is_superuser = True

TEACHER
├── role.name    = "teacher"
├── is_staff     = True
└── is_superuser = False

STUDENT
├── role.name    = "student"
├── is_staff     = False
└── is_superuser = False
```

### Sincronización automática

Cuando se asigna o cambia el `role` de un usuario, `User.save()` sincroniza automáticamente `is_staff` e `is_superuser`. No es necesario asignarlos manualmente.

```python
user.role = Role.objects.get(name='teacher')
user.save()
# → is_staff=True, is_superuser=False  (automático)
```

### Permisos disponibles

| Permiso | Descripción |
|---|---|
| `IsAdmin` | Solo `role='admin'` (superusuario) |
| `IsTeacher` | Solo `role='teacher'` |
| `IsStudent` | Solo `role='student'` |
| `IsTeacherOrAdmin` | Teacher o Admin |
| `IsAdminOrReadOnly` | Escritura solo admin; lectura cualquier autenticado |
| `IsTeacherOrAdminOrReadOnly` | Escritura teacher/admin; lectura cualquier autenticado |

### Tabla de acceso por endpoint

| Endpoint | Student | Teacher | Admin |
|---|---|---|---|
| `GET /api/courses/` | ✅ | ✅ | ✅ |
| `POST /api/courses/` | ❌ | ✅ | ✅ |
| `POST /api/languages/` | ❌ | ❌ | ✅ |
| `GET /api/users/` | ❌ | ❌ | ✅ |
| `GET /api/orders/stats/` | ❌ | ❌ | ✅ |
| `GET /api/progress/` | ✅ (propio) | ✅ (propio) | ✅ |
| `GET /api/stats/` | ✅ (propio) | ✅ (propio) | ✅ |

---

## Modelo de Base de Datos

El sistema está compuesto por **16 modelos** organizados en 4 módulos.

### Módulo de Usuarios y Autenticación

| Modelo | Descripción |
|---|---|
| `Role` | Roles del sistema: `admin`, `teacher`, `student` |
| `User` | Extiende AbstractUser. Login por email. Sincroniza flags desde role |
| `UserProfile` | Perfil extendido: nombre, apellido, avatar, idioma nativo, zona horaria |

### Módulo de Contenido Educativo

| Modelo | Descripción |
|---|---|
| `Language` | Idiomas disponibles (Inglés, Francés, Alemán…) |
| `Course` | Cursos por idioma y nivel MCER (A1 → C2) |
| `Module` | Unidades dentro de un curso, con orden |
| `Lesson` | Lecciones con tipo de contenido (video, text, audio, interactive) y XP |
| `Exercise` | Ejercicios: opción múltiple, traducir, escuchar, completar, emparejar |

### Módulo de Progreso y Gamificación

| Modelo | Descripción |
|---|---|
| `UserProgress` | Estado por lección: `in_progress` / `completed`, score |
| `UserStats` | XP total, racha actual, racha más larga |
| `Achievement` | Logros con XP requerido para desbloquear |
| `UserAchievement` | Logros desbloqueados por usuario |

### Módulo de Pagos y Suscripciones

| Modelo | Descripción |
|---|---|
| `Subscription` | Planes disponibles (nombre, precio, duración, beneficios) |
| `UserSubscription` | Suscripción activa de un usuario con fechas |
| `Payment` | Transacciones: monto, método, estado |
| `Order` | Órdenes de compra vinculadas a un plan |

---

## Endpoints de la API

Base URL: `https://tu-servidor.com/api/`

### Autenticación — Público

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/auth/register/` | Registro. Asigna `role=student` automáticamente |
| `POST` | `/api/auth/login/` | Login. Devuelve `access`, `refresh` y `user{}` |
| `POST` | `/api/auth/token/refresh/` | Renovar access token |
| `GET` | `/api/auth/me/` | 🆕 Datos del usuario autenticado (para validación Android) |

**Response de login:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 1,
    "username": "danny",
    "email": "danny@email.com",
    "role": "teacher",
    "is_staff": true,
    "is_superuser": false
  }
}
```

### Gestión de usuarios — Solo Admin

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/users/` | Lista usuarios de personal (teachers y admins) |
| `POST` | `/api/users/` | Crea teacher o admin. Flags se sincronizan por role |
| `GET` | `/api/users/{id}/` | Detalle del usuario |
| `PATCH` | `/api/users/{id}/` | Actualizar usuario (cambiar role sincroniza flags) |
| `DELETE` | `/api/users/{id}/` | Eliminar usuario |

### Contenido Educativo

| Método | Endpoint | Acceso escritura | Descripción |
|---|---|---|---|
| `GET/POST` | `/api/languages/` | Admin | Idiomas |
| `GET/POST` | `/api/courses/` | Teacher, Admin | Cursos |
| `GET/POST` | `/api/modules/` | Teacher, Admin | Módulos |
| `GET/POST` | `/api/lessons/` | Teacher, Admin | Lecciones |
| `GET/POST` | `/api/exercises/` | Teacher, Admin | Ejercicios |

**Filtros disponibles:**
- Cursos: `?language=1`, `?difficulty_level=A1`, `?search=básico`
- Lecciones: `?module=1`, `?content_type=video`
- Ejercicios: `?lesson=1`, `?exercise_type=multiple_choice`

### Progreso y Gamificación — Autenticado (datos propios)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET/POST` | `/api/progress/` | Progreso por lección. Filtro: `?status=completed` |
| `GET` | `/api/stats/` | XP total, racha actual, racha más larga |
| `GET` | `/api/achievements/` | Catálogo de logros disponibles |
| `GET` | `/api/my-achievements/` | Logros desbloqueados por el usuario |

### Suscripciones y Pagos

| Método | Endpoint | Acceso | Descripción |
|---|---|---|---|
| `GET/POST` | `/api/subscriptions/` | Lectura: todos / Escritura: Admin | Planes disponibles |
| `GET/POST` | `/api/my-subscriptions/` | Autenticado (propio) | Suscripciones del usuario |
| `GET/POST` | `/api/payments/` | Autenticado (propio) | Historial de pagos |
| `GET/POST` | `/api/orders/` | Propio / Admin ve todas | Órdenes de compra |
| `GET` | `/api/orders/stats/` | Solo Admin | Ingresos totales y cantidad de órdenes |

### Paginación global

```json
{
  "count": 50,
  "next": "http://servidor/api/courses/?page=2",
  "previous": null,
  "results": [...]
}
```

Parámetros: `?page=2` · `?page_size=20` (máx 100)

### Header de autenticación

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## Panel de Administración Django

Disponible en: `http://tu-servidor/admin/`

Acceso con usuario `role=admin` (`is_staff=True`, `is_superuser=True`).

### Modelos gestionables desde el panel

| Sección | Modelos |
|---|---|
| **Usuarios** | Role, User, UserProfile |
| **Contenido** | Language, Course, Module, Lesson, Exercise |
| **Progreso** | UserProgress, UserStats, Achievement, UserAchievement |
| **Pagos** | Subscription, UserSubscription, Payment, Order |

Desde `/admin/` puedes crear, editar y eliminar cualquier registro sin tocar la API directamente.

---

## Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.11+ | Lenguaje principal |
| Django | 4.2+ | Framework backend |
| Django REST Framework | 3.14+ | API REST |
| djangorestframework-simplejwt | 5.3+ | Autenticación JWT |
| django-cors-headers | 4.0+ | CORS para Android |
| django-filter | 23.0+ | Filtros avanzados |
| psycopg2-binary | 2.9+ | Conector PostgreSQL |
| python-decouple | 3.8+ | Variables de entorno |
| PostgreSQL | 14+ | Base de datos |
| GitHub Actions | — | CI/CD automático |
| Gunicorn | — | Servidor WSGI producción |

---

## Instalación

### Prerrequisitos

- Python 3.11+
- PostgreSQL 14+
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/Axel-25-dg/idiomas_api_guaman_danny.git
cd aplicacionidion_idiomas_guaman_danny
```

### 2. Crear y activar entorno virtual

```powershell
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1
```

```bash
# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env   # Linux/Mac
copy .env.example .env # Windows
```

```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=languageapi_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOW_ALL_ORIGINS=True
```

### 5. Crear base de datos

```sql
CREATE DATABASE languageapi_db;
```

### 6. Aplicar migraciones

```bash
python manage.py migrate
```

> La migración `0003` crea automáticamente los roles `admin`, `teacher`, `student`
> y asigna roles a usuarios existentes según sus flags.

### 7. Crear superusuario (admin)

```bash
python manage.py createsuperuser
```

> Después del login en `/admin/`, asigna el rol `admin` al superusuario
> desde **Learning > Users** para que funcione con la app Android.

### 8. Iniciar servidor

```bash
python manage.py runserver
```

- API: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`

---

## Deploy con GitHub Actions

El pipeline en `.github/workflows/deploy.yml` se activa automáticamente con cada push a `main`:

```
push a main
  └── GitHub Actions (ubuntu-latest)
        ├── Checkout código
        └── SSH al VPS
              ├── git pull origin main
              ├── source .venv/bin/activate
              ├── pip install -r requirements.txt
              ├── python manage.py migrate        ← aplica 0003 en producción
              └── systemctl restart gunicorn-shopapi.service
```

**Secrets requeridos en GitHub:**

| Secret | Descripción |
|---|---|
| `SERVER_IP` | IP del VPS |
| `SERVER_USER` | Usuario SSH (root) |
| `SSH_PRIVATE_KEY` | Llave privada SSH |

---

## Testing

```bash
# Todos los tests
python manage.py test learning --verbosity=2

# Solo tests de roles y permisos
python manage.py test learning.tests.test_roles_and_permissions --verbosity=2
```

**Cobertura actual: 29 tests**

| Suite | Tests | Cubre |
|---|---|---|
| `test_api.py` | 6 | Auth básico, idiomas, permisos básicos |
| `test_roles_and_permissions.py` | 23 | Sincronización de flags, registro, login con `user{}`, `/api/auth/me/`, permisos por rol, migración de datos |

---

## Autor

<div align="center">

**Danny Alexander Guamán Pillajo**

Estudiante de Ingeniería en Desarrollo de Software

Universidad Tecnológica Equinoccial — UTE

Seminario de Integración — Módulo 2

<br/>

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/UTE_logo.svg/512px-UTE_logo.svg.png" width="90" alt="UTE"/>

*Facultad de Ciencias de la Ingeniería e Industrias*

</div>
