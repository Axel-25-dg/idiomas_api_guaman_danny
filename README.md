<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/UTE_logo.svg/512px-UTE_logo.svg.png" width="160" alt="Universidad UTE"/>

<br/>
<br/>

# LanguageAPI

**Backend REST para Plataforma de Aprendizaje de Idiomas**

Desarrollado con Django y Django REST Framework

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.14+-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Authentication-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

</div>

---

## Tabla de Contenido

- [Descripción](#descripción)
- [Características](#características)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Modelo de Base de Datos](#modelo-de-base-de-datos)
- [Endpoints de la API](#endpoints-de-la-api)
- [Tecnologías](#tecnologías)
- [Instalación](#instalación)
- [Pruebas de la API](#pruebas-de-la-api)
- [Seguridad](#seguridad)
- [Testing](#testing)
- [Autor](#autor)

---

## Descripción

LanguageAPI es un backend REST completo desarrollado para una plataforma de aprendizaje de idiomas inspirada en Duolingo y Babbel. Fue construido utilizando Django y Django REST Framework, con autenticación basada en tokens JWT y PostgreSQL como motor de base de datos.

El sistema está diseñado bajo una arquitectura modular que permite gestionar de manera independiente los módulos de usuarios, contenido educativo, progreso del estudiante y suscripciones. Cada módulo expone sus propios endpoints RESTful y aplica reglas de permisos específicas según el rol del usuario.

El proyecto sigue la misma estructura y convenciones del proyecto base `shopapi` del docente, adaptado completamente al dominio educativo.

---

## Características

- Registro e inicio de sesión con autenticación JWT
- Sistema de roles: administrador, estudiante y docente
- Gestión completa de idiomas, cursos, módulos, lecciones y ejercicios
- Seguimiento del progreso del estudiante por lección
- Sistema de gamificación con puntos de experiencia (XP), rachas y logros
- Planes de suscripción premium y registro de pagos
- Permisos diferenciados por rol (solo administradores pueden crear o modificar contenido)
- Paginación, filtros y ordenamiento en todos los endpoints
- Panel de administración Django con todos los modelos registrados
- Variables de entorno protegidas con python-decouple

---

## Arquitectura del Proyecto

```
languageapi/
│
├── config/
│   ├── settings.py             # Configuración principal: JWT, CORS, base de datos
│   ├── urls.py                 # URLs raíz del proyecto
│   ├── wsgi.py
│   └── asgi.py
│
├── learning/                   # Aplicación principal
│   │
│   ├── models/
│   │   ├── user.py             # Role, User, UserProfile
│   │   ├── language.py         # Language
│   │   ├── course.py           # Course, Module, Lesson, Exercise
│   │   ├── progress.py         # UserProgress, UserStats, Achievement, UserAchievement
│   │   └── subscription.py     # Subscription, UserSubscription, Payment
│   │
│   ├── serializers/
│   │   ├── user_serializer.py
│   │   ├── course_serializer.py
│   │   ├── progress_serializer.py
│   │   └── subscription_serializer.py
│   │
│   ├── views/
│   │   ├── auth_views.py       # Registro y login
│   │   ├── course_views.py     # Idiomas, cursos, módulos, lecciones, ejercicios
│   │   ├── progress_views.py   # Progreso, estadísticas, logros
│   │   └── subscription_views.py  # Planes y pagos
│   │
│   ├── tests/
│   │   └── test_api.py
│   │
│   ├── admin.py                # Registro de todos los modelos en el panel admin
│   ├── urls.py                 # Rutas con DefaultRouter
│   ├── pagination.py           # Paginación estándar (10 items por página)
│   ├── permissions.py          # Permiso IsAdminOrReadOnly
│   └── filters.py              # Filtros personalizados con django-filter
│
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Modelo de Base de Datos

El sistema está compuesto por **15 modelos** organizados en 4 módulos.

### Módulo de Usuarios y Autenticación

| Modelo | Descripción |
|---|---|
| `Role` | Define los roles del sistema: `admin`, `student`, `teacher` |
| `User` | Usuario principal. Extiende AbstractUser con autenticación por email |
| `UserProfile` | Perfil extendido: nombre, apellido, avatar, idioma nativo y zona horaria |

### Módulo de Contenido Educativo

| Modelo | Descripción |
|---|---|
| `Language` | Idiomas disponibles en la plataforma (Inglés, Francés, Alemán, etc.) |
| `Course` | Cursos organizados por idioma y nivel (A1, A2, B1, B2, C1, C2) |
| `Module` | Unidades dentro de un curso con orden definido |
| `Lesson` | Lecciones individuales con tipo de contenido y puntos XP de recompensa |
| `Exercise` | Ejercicios dentro de cada lección (opción múltiple, traducir, escuchar, completar) |

### Módulo de Progreso y Gamificación

| Modelo | Descripción |
|---|---|
| `UserProgress` | Registra el estado de cada lección por usuario (en curso / completado) |
| `UserStats` | Estadísticas del usuario: XP total, racha actual y racha más larga |
| `Achievement` | Logros disponibles en la plataforma con XP requerido para desbloquearlos |
| `UserAchievement` | Relación entre usuarios y los logros que han desbloqueado |

### Módulo de Pagos y Suscripciones

| Modelo | Descripción |
|---|---|
| `Subscription` | Planes de suscripción disponibles (mensual, anual, etc.) |
| `UserSubscription` | Suscripciones activas de cada usuario con fechas de inicio y vencimiento |
| `Payment` | Historial completo de transacciones con estado y método de pago |

---

## Endpoints de la API

### Autenticación — No requiere token

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/auth/register/` | Registro de nuevo usuario |
| `POST` | `/api/auth/login/` | Inicio de sesión — retorna access y refresh token |
| `POST` | `/api/auth/token/refresh/` | Renovar el access token usando el refresh token |

### Contenido Educativo — Requiere token

| Método | Endpoint | Descripción |
|---|---|---|
| `GET / POST` | `/api/languages/` | Listar o crear idiomas |
| `GET / POST` | `/api/courses/` | Listar o crear cursos |
| `GET / POST` | `/api/modules/` | Listar o crear módulos |
| `GET / POST` | `/api/lessons/` | Listar o crear lecciones |
| `GET / POST` | `/api/exercises/` | Listar o crear ejercicios |

### Progreso y Gamificación — Requiere token

| Método | Endpoint | Descripción |
|---|---|---|
| `GET / POST` | `/api/progress/` | Ver o registrar progreso por lección |
| `GET` | `/api/stats/` | Ver estadísticas personales (XP y rachas) |
| `GET` | `/api/achievements/` | Listar todos los logros disponibles |
| `GET` | `/api/my-achievements/` | Ver los logros desbloqueados por el usuario |

### Suscripciones y Pagos — Requiere token

| Método | Endpoint | Descripción |
|---|---|---|
| `GET / POST` | `/api/subscriptions/` | Listar planes de suscripción disponibles |
| `GET / POST` | `/api/my-subscriptions/` | Ver o crear suscripciones del usuario |
| `GET / POST` | `/api/payments/` | Ver o registrar pagos |

---

## Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.11+ | Lenguaje principal |
| Django | 4.2+ | Framework web backend |
| Django REST Framework | 3.14+ | Construcción de la API REST |
| djangorestframework-simplejwt | 5.3+ | Autenticación con tokens JWT |
| django-cors-headers | 4.0+ | Control de acceso CORS |
| django-filter | 23.0+ | Filtros avanzados en los endpoints |
| psycopg2-binary | 2.9+ | Conector para PostgreSQL |
| python-decouple | 3.8+ | Manejo seguro de variables de entorno |
| PostgreSQL | 14+ | Motor de base de datos relacional |

---

## Instalación

### Prerrequisitos

- Python 3.11 o superior
- PostgreSQL 14 o superior
- Git

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/languageapi.git
cd languageapi
```

### Paso 2 — Crear y activar el entorno virtual

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 3 — Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4 — Configurar variables de entorno

```bash
# Windows
copy .env.example .env

# Linux / Mac
cp .env.example .env
```

Editar el archivo `.env` con los datos del entorno local:

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

### Paso 5 — Crear la base de datos en PostgreSQL

```sql
CREATE DATABASE languageapi_db;
```

### Paso 6 — Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 7 — Crear superusuario

```bash
python manage.py createsuperuser
```

### Paso 8 — Iniciar el servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

El panel de administración estará disponible en: `http://127.0.0.1:8000/admin/`

---

## Pruebas de la API

### Registrar un usuario

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password2": "TestPass123!"
  }'
```

### Iniciar sesión

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### Acceder a un endpoint protegido

```bash
curl http://127.0.0.1:8000/api/courses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Seguridad

- Autenticación basada en tokens JWT con expiración configurable
- Todos los endpoints (excepto registro y login) requieren token válido
- Los endpoints de escritura (`POST`, `PUT`, `DELETE`) están restringidos a administradores
- Los usuarios autenticados tienen acceso de solo lectura al contenido educativo
- Cada usuario accede únicamente a su propio progreso, estadísticas y pagos
- Las credenciales y configuración sensible se gestionan con variables de entorno

---

## Testing

Ejecutar las pruebas unitarias del proyecto:

```bash
python manage.py test
```

Las pruebas cubren:

- Registro de usuario con datos válidos e inválidos
- Login y obtención de tokens JWT
- Acceso a endpoints con y sin autenticación
- Restricción de escritura para usuarios no administradores

---

## Autor

<div align="center">

**Danny Alexander Guamán Pillajo**

Estudiante de Ingeniería en Desarrollo de Software

Universidad Tecnológica Equinoccial — UTE

Seminario de Integración — Modulo 2

<br/>

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/UTE_logo.svg/512px-UTE_logo.svg.png" width="90" alt="UTE"/>

*Facultad de Ciencias de la Ingeniería e Industrias*

</div>
