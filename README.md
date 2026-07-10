<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/UTE_logo.svg/512px-UTE_logo.svg.png" width="160" alt="Universidad UTE"/>

<br/>
<br/>

# JumpUp UTE — API de Aprendizaje de Idiomas

**Backend REST para Plataforma Educativa de Idiomas**

Desarrollado con Django 6.0.5 + Django REST Framework + PostgreSQL + Django Channels

<br/>

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Channels](https://img.shields.io/badge/Channels-WebSocket-44B39D?style=for-the-badge&logo=django&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT4o-412991?style=for-the-badge&logo=openai&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-Docs-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

</div>

---

## Información General

| Campo | Detalle |
|---|---|
| **Proyecto** | JumpUp UTE — Plataforma de Aprendizaje de Idiomas |
| **Integrantes** | Danny Guamán, Alex Macias, Ariel Paucar |
| **Carrera** | Ingeniería en Desarrollo de Software |
| **Universidad** | Universidad Tecnológica Equinoccial (UTE) |
| **Materia** | Seminario de Integración |
| **Repositorio** | https://github.com/Axel-25-dg/idiomas_api_guaman_danny |
| **URL Pública** | https://guaman-idiomas-ute.online |
| **Documentación API** | https://guaman-idiomas-ute.online/api/docs/ |
| **Redoc** | https://guaman-idiomas-ute.online/api/redoc/ |

---

## Descripción del Sistema

JumpUp UTE es una API REST + WebSocket completa para una plataforma de aprendizaje de idiomas. Ofrece:

- **Cursos** por niveles MCER (A1-C2) con módulos, lecciones y ejercicios
- **Gamificación** con XP, rachas (streaks), logros y ranking global
- **Tutor IA** integrado con OpenAI GPT-4o vía WebSocket
- **Aulas virtuales** con código de acceso
- **Certificados** verificables públicamente (A1-C2)
- **Suscripciones y pagos**
- **Foro** comunitario con categorías, hilos, posts y reacciones
- **Feed social** con publicaciones, comentarios y reacciones
- **Mensajería** directa en tiempo real vía WebSocket
- **Videotutoría** en vivo con WebRTC
- **Notificaciones push** en tiempo real
- **Autenticación** JWT con 3 roles (admin, teacher, student) + login biométrico
- **Seguridad** con bloqueo de IPs, monitoreo de sesiones y alertas

---

## Stack Tecnológico

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.13 | Lenguaje |
| Django | 6.0.5 | Framework principal |
| Django REST Framework | 3.15+ | API REST |
| Django Channels | 4.0+ | WebSockets |
| Daphne | 4.0+ | ASGI Server |
| Channels Redis | 4.1+ | Channel Layer |
| djangorestframework-simplejwt | 5.3+ | JWT Auth |
| drf-spectacular | 0.27+ | Swagger/Redoc |
| django-cors-headers | 4.0+ | CORS |
| django-filter | 23.0+ | Filtros |
| django-celery-beat | - | Tareas programadas |
| psycopg2-binary | 2.9+ | PostgreSQL |
| python-decouple | 3.8+ | Variables de entorno |
| Pillow | 10.0+ | Procesamiento de imágenes |
| OpenAI | 1.0+ | Tutor IA (GPT-4o) |
| PostgreSQL | 16 | Base de datos |
| Gunicorn | - | WSGI Server |
| Nginx | - | Proxy inverso |
| GitHub Actions | - | CI/CD |
| Hetzner Cloud | - | VPS (Ubuntu 22.04) |

---

## Base de Datos — 58 Tablas

### App `learning` (48 tablas)

| # | Modelo | Tabla | Descripción |
|---|---|---|---|
| 1 | `Role` | `learning_role` | Roles del sistema: admin, teacher, student |
| 2 | `User` | `learning_user` | Usuario personalizado (email = USERNAME_FIELD, soft-delete) |
| 3 | `UserProfile` | `learning_userprofile` | Perfil: avatar, idiomas, zona horaria |
| 4 | `Language` | `learning_language` | Idiomas disponibles (EN, ES, FR...) |
| 5 | `Course` | `learning_course` | Cursos por idioma y nivel A1-C2 |
| 6 | `Module` | `learning_module` | Módulos dentro de un curso |
| 7 | `Lesson` | `learning_lesson` | Lecciones (video/text/interactive/audio) + XP reward |
| 8 | `Exercise` | `learning_exercise` | Ejercicios (multiple_choice, translate, listen, fill_blank, match) |
| 9 | `UserProgress` | `learning_userprogress` | Progreso usuario-lección (status, score) |
| 10 | `UserStats` | `learning_userstats` | XP total, racha actual, racha máxima |
| 11 | `Achievement` | `learning_achievement` | Logros definidos (nombre, XP requerido) |
| 12 | `UserAchievement` | `learning_userachievement` | Logros desbloqueados por usuario |
| 13 | `Subscription` | `learning_subscription` | Planes de suscripción |
| 14 | `UserSubscription` | `learning_usersubscription` | Suscripciones por usuario |
| 15 | `Payment` | `learning_payment` | Pagos |
| 16 | `Order` | `learning_order` | Órdenes de compra |
| 17 | `Classroom` | `learning_classroom` | Aulas virtuales con código de acceso |
| 18 | `ClassroomEnrollment` | `learning_classroomenrollment` | Inscripción estudiante-aula |
| 19 | `Certificate` | `learning_certificate` | Certificados MCER (código único verificable) |
| 20 | `TeacherResource` | `learning_teacherresource` | Recursos subidos por profesores |
| 21 | `MediaFile` | `learning_mediafile` | Archivos multimedia centralizados (+thumbnail WebP) |
| 22 | `EmailLog` | `learning_emaillog` | Registro de correos enviados |
| 23 | `BroadcastEmail` | `learning_broadcastemail` | Correos masivos |
| 24 | `Notification` | `learning_notification` | Notificaciones push |
| 25 | `Announcement` | `learning_announcement` | Anuncios globales |
| 26 | `UserNotificationPreference` | `learning_usernotificationpreference` | Preferencias de notificación |
| 27 | `MessageThread` | `learning_messagethread` | Hilos de chat |
| 28 | `Message` | `learning_message` | Mensajes (incluye Tutor IA) |
| 29 | `MessageAttachment` | `learning_messageattachment` | Archivos adjuntos en mensajes |
| 30 | `ForumCategory` | `learning_forumcategory` | Categorías del foro |
| 31 | `ForumThread` | `learning_forumthread` | Hilos del foro |
| 32 | `ForumPost` | `learning_forumpost` | Publicaciones (soft-delete) |
| 33 | `ForumReaction` | `learning_forumreaction` | Reacciones a posts |
| 34 | `ForumReport` | `learning_forumreport` | Reportes de contenido |
| 35 | `SocialPost` | `learning_socialpost` | Publicaciones del feed social |
| 36 | `SocialComment` | `learning_socialcomment` | Comentarios |
| 37 | `SocialReaction` | `learning_socialreaction` | Reacciones al feed |
| 38 | `LiveSession` | `learning_livesession` | Sesiones de tutoría en vivo |
| 39 | `LiveParticipant` | `learning_liveparticipant` | Participantes en sesiones |
| 40 | `MediaProgress` | `learning_mediaprogress` | Progreso de reproducción multimedia |
| 41 | `UserActivityLog` | `learning_useractivitylog` | Registro de actividad |
| 42 | `UserFavorite` | `learning_userfavorite` | Favoritos (cursos/lecciones) |
| 43 | `Report` | `learning_report` | Reportes del sistema |
| 44 | `MediaAsset` | `learning_mediaasset` | Assets multimedia |
| 45 | `UserFeedback` | `learning_userfeedback` | Feedback de usuarios |
| 46 | `MaintenanceLog` | `learning_maintenancelog` | Registro de mantenimiento |
| 47 | `BackupHistory` | `learning_backuphistory` | Historial de backups |
| 48 | `NotificationType` | `learning_notificationtype` | Tipos de notificación (TextChoices) |

### App `seguridad_acceso` (6 tablas)

| # | Modelo | Tabla | Descripción |
|---|---|---|---|
| 49 | `PasswordReset` | `password_resets` | Tokens/reset de contraseña |
| 50 | `LoginAttempt` | `login_attempts` | Intentos de login |
| 51 | `ActiveSession` | `active_sessions` | Sesiones activas |
| 52 | `BlockedIp` | `blocked_ips` | IPs bloqueadas |
| 53 | `ApiToken` | `api_tokens` | Tokens de API |
| 54 | `BiometricDevice` | `biometric_devices` | Dispositivos biométricos |

### App `dispositivos_alertas` (3 tablas)

| # | Modelo | Tabla | Descripción |
|---|---|---|---|
| 55 | `UserDevice` | `user_devices` | Dispositivos del usuario |
| 56 | `UserLocation` | `user_locations` | Ubicaciones geográficas |
| 57 | `SecurityAlert` | `security_alerts` | Alertas de seguridad |

### Modelos Base (abstractos)

| Modelo | Campos | Usado por |
|---|---|---|
| `TimestampedModel` | created_at, updated_at | MediaFile, EmailLog, BroadcastEmail, Notification, etc. |
| `SoftDeleteModel` | is_active, deleted_at | MediaFile, User, Course, Classroom, etc. |

---

## Arquitectura del Sistema

```
App Móvil (Flutter)           Servidor Django 6.0               OpenAI / SMTP
       │                            │                                │
       │── HTTPS (REST API) ───────>│                                │
       │── WebSocket (ws/wss) ─────>│                                │
       │                            │── OpenAI GPT-4o ────────────>│
       │                            │── SMTP (correos HTML) ──────>│
       │<── JSON Responses ─────────│                                │
       │<── WebSocket Events ───────│                                │
```

```
┌─────────────────────────────────────────────────────────┐
│                    HTTP / WebSocket                      │
│              Gunicorn + Daphne (ASGI)                    │
├─────────────────────────────────────────────────────────┤
│               Django Channels (Redis)                    │
│         Chat / Notificaciones / Live Sessions            │
├─────────────────────────────────────────────────────────┤
│             Django REST Framework (API)                  │
│       43 ViewSets + 9 APIViews + 50+ Serializers         │
├─────────────────────────────────────────────────────────┤
│               Business Logic Layer                       │
│  Services (AI, Email) + Signals (gamificación) + Utils   │
├─────────────────────────────────────────────────────────┤
│                   Models Layer                           │
│           57 modelos en 3 apps (learning ppal)           │
├─────────────────────────────────────────────────────────┤
│                Database (PostgreSQL 16)                  │
└─────────────────────────────────────────────────────────┘
```

---

## Roles y Permisos

| Rol | is_staff | is_superuser | Acceso Admin | Permisos API |
|-----|:--------:|:------------:|:------------:|--------------|
| **admin** | ✅ | ✅ | Completo | Todos los endpoints |
| **teacher** | ✅ | ❌ | Limitado | Crear contenido, aulas, certificados |
| **student** | ❌ | ❌ | No | Consumir contenido, progreso, foro, chat |

| Clase de Permiso | Acceso |
|---|---|
| `IsAdmin` | Solo admin |
| `IsTeacher` | Solo teacher |
| `IsStudent` | Solo student |
| `IsTeacherOrAdmin` | Teacher o admin |
| `IsAdminOrReadOnly` | Lectura cualquiera, escritura admin |
| `IsTeacherOrAdminOrReadOnly` | Lectura cualquiera, escritura teacher/admin |

La sincronización es automática: `User.save()` llama a `sync_flags_from_role()` que setea `is_staff`/`is_superuser` según el rol FK.

---

## Autenticación (JWT SimpleJWT)

| Config | Valor |
|---|---|
| Access token | 1 hora |
| Refresh token | 7 días (30 días con `remember_me`) |
| Rotación | Sí (cada refresh invalida el anterior) |
| Algoritmo | HS256 |

**Payload del JWT:**
```json
{
  "token_type": "access",
  "exp": 1234567890,
  "user_id": 1,
  "is_staff": true,
  "is_superuser": false,
  "role": "teacher"
}
```

### Login Biométrico

Registro: `POST /api/auth/biometric/register/` → devuelve `biometric_token`.
Login: `POST /api/auth/biometric/login/` con `device_id` + `biometric_token`.

---

## Tutor IA (OpenAI GPT-4o)

Integrado en el sistema de mensajería WebSocket. Se activa automáticamente cuando un hilo tiene 1 solo participante o el asunto contiene "IA".

**Prompt del sistema:**
> *"Eres el Tutor IA de JumpUp. Tu objetivo es ayudar al estudiante a practicar y aprender idiomas de manera amigable, interactiva y gamificada. Corrige los errores con amabilidad y sugiere mejoras. Sé conciso y directo."*

**Flujo:**
1. Usuario crea hilo (`POST /api/threads/`)
2. Conecta WebSocket: `ws://host/ws/chat/{id}/?token=JWT`
3. Envía: `{"type":"chat_message","body":"How do I say hello?"}`
4. Backend detecta hilo IA → llama a OpenAI GPT-4o
5. Respuesta se guarda como mensaje del usuario `tutor_ia`
6. Se envía de vuelta por WebSocket

---

## WebSockets (Django Channels)

| Conexión | Propósito |
|---|---|
| `ws://host/ws/chat/{thread_id}/?token=JWT` | Chat en tiempo real + Tutor IA |
| `ws://host/ws/notifications/?token=JWT` | Notificaciones push en tiempo real |
| `ws://host/ws/live-session/{session_id}/?token=JWT` | Señalización WebRTC |

**Autenticación:** Token JWT vía query string `?token=<jwt>` o header `Authorization: Bearer <jwt>`.

**Eventos WebSocket (Chat):**
```
Cliente → Servidor:
{ "type": "chat_message", "body": "Hello!" }
{ "type": "typing", "is_typing": true }

Servidor → Cliente:
{ "type": "chat_message", "message": {...} }
{ "type": "typing", "user_id": 1, "is_typing": true }
{ "type": "read_receipt", "message_id": 42, "reader_id": 2 }
```

---

## Gamificación (Signals)

| Evento | Acción automática |
|---|---|
| Usuario se registra | Se crea `UserProfile` automáticamente |
| Lección completada | Suma XP a `UserStats`, actualiza racha (días consecutivos), verifica logros |
| XP cambia | Revisa y desbloquea logros que cumplan el `required_xp` |
| Nueva lección creada | Notifica por correo a estudiantes del curso |

**Cálculo de rachas:**
- Día consecutivo (diff=1) → incrementa racha
- Mismo día (diff=0) → no cambia
- Se rompió (diff>1) → reinicia a 1

---

## Sistema de Archivos Multimedia (MediaFile)

**Procesamiento automático de imágenes:**
1. Calcula SHA-256 checksum (único, evita duplicados)
2. Convierte a **WebP** calidad 85%, máx 2048x2048 px
3. Genera **thumbnail** 300x300 WebP calidad 70%
4. Almacena dimensiones (width/height)

**Validaciones:**
| Tipo | Tamaño máx | Formatos |
|---|---|---|
| General | 20 MB | jpg, jpeg, png, webp, pdf |
| Avatar | 2 MB | jpeg, png, webp |

**Almacenamiento:** local, S3, Cloudinary (configurable).

---

## Sistema de Correos (HTML Templates)

Todos los correos se envían con **templates HTML profesionales** y quedan registrados en `EmailLog`:

| Correo | Template | Disparador |
|---|---|---|
| Bienvenida | `welcome_email.html` | Registro de usuario |
| Código PIN reset | `password_reset_pin_email.html` | Solicitud de reset |
| Reset link | `password_reset_email.html` | Solicitud de reset (link) |
| Certificado | `certificate_email.html` | Emisión de certificado |
| Confirmación pago | `payment_confirmation_email.html` | Pago aprobado |
| Notificación curso | `course_notification_email.html` | Nueva lección |
| Suscripción por vencer | `subscription_expiration_email.html` | CRON programado |
| Verificación email | `verification_email.html` | Registro |
| Correo personalizado | `custom_email.html` | Admin/comunicaciones |

**Configuración SMTP en `.env`:**
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=contraseña_app
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=tu_correo@gmail.com
```

El base template `email_base.html` cuenta con:
- Header degradado azul con logo
- Footer oscuro con enlaces sociales
- Botones con gradiente y sombra
- Códigos PIN en display oscuro monospace
- Tablas de recibo profesionales
- Info boxes (success, warning, info)
- Totalmente responsive

---

## Endpoints de la API

### Autenticación (10 endpoints)

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| POST | `/api/auth/register/` | ❌ | Registro (username, email, password, password2) |
| POST | `/api/auth/login/` | ❌ | Login + JWT. Soporta `remember_me` |
| POST | `/api/auth/token/refresh/` | ❌ | Refrescar JWT |
| POST | `/api/auth/biometric/register/` | ✅ | Registrar dispositivo biométrico |
| POST | `/api/auth/biometric/login/` | ❌ | Login biométrico |
| POST | `/api/auth/password-reset/` | ❌ | Solicitar PIN reset (6 dígitos al email) |
| POST | `/api/auth/password-reset-confirm/` | ❌ | Confirmar reset con PIN |
| GET | `/api/auth/me/` | ✅ | Perfil propio |
| PATCH | `/api/auth/me/` | ✅ | Actualizar perfil (incluye avatar multipart) |
| PATCH | `/api/auth/profile/update-languages/` | ✅ | Actualizar idiomas según rol |

### Dashboards (3 endpoints)

| Método | Endpoint | Acceso | Contenido |
|---|---|---|---|
| GET | `/api/dashboard/student/` | Todos | XP, nivel, rachas, progreso %, logros, certificados, aulas |
| GET | `/api/dashboard/teacher/` | Teacher/Admin | Aulas, estudiantes, recursos, lecciones emitidas |
| GET | `/api/dashboard/admin/` | Admin | Usuarios totales, teachers, estudiantes, cursos, suscripciones, pagos |

### Contenido Educativo (CRUD por rol)

| Endpoint | Basename | Filtros Disponibles |
|---|---|---|
| `/api/languages/` | language | `?search=name&ordering=name` |
| `/api/courses/` | course | `?language=1&difficulty_level=A1&search=title` |
| `/api/modules/` | module | `?course=1&search=title` |
| `/api/lessons/` | lesson | `?module=1&content_type=video` + `GET /{id}/stats/` |
| `/api/exercises/` | exercise | `?lesson=1&exercise_type=match` |

- **Lectura:** Todos autenticados
- **Escritura:** Teacher/Admin (languages solo Admin)

### Progreso y Gamificación (6 endpoints)

| Método | Endpoint | Descripción |
|---|---|---|
| CRUD | `/api/progress/` | Progreso por lección |
| GET | `/api/progress/summary/` | Resumen completo (total, completado, XP, nivel, rachas) |
| GET | `/api/stats/` | XP total, racha actual, racha máxima |
| GET | `/api/achievements/` | Catálogo de logros |
| GET | `/api/my-achievements/` | Logros desbloqueados |
| GET | `/api/ranking/` | Top 100 por XP (posición, nivel, rachas) |

### Suscripciones y Pagos (4 endpoints)

| Endpoint | Descripción |
|---|---|
| `/api/subscriptions/` | CRUD planes (admin escribe) |
| `/api/my-subscriptions/` | Mis suscripciones |
| `/api/payments/` | Mis pagos (envía correo al crear) |
| `/api/orders/` | Órdenes + `GET /stats/` (admin: revenue total) |

### Gestión de Usuarios (2 endpoints, solo admin)

| Endpoint | Descripción |
|---|---|
| `/api/users/` | CRUD teachers/admins |
| `/api/admin-students/` | CRUD estudiantes |

### Aulas Virtuales (1 endpoint)

| Método | Endpoint | Descripción |
|---|---|---|
| CRUD | `/api/classrooms/` | Aulas virtuales |
| POST | `/api/classrooms/join/` | Unirse con `access_code` |
| GET | `/api/classrooms/mine/` | Mis aulas (estudiante) |
| POST | `/api/classrooms/{id}/remove-student/` | Expulsar estudiante |

### Certificados (1 endpoint)

| Método | Endpoint | Descripción |
|---|---|---|
| CRUD | `/api/certificates/` | CRUD |
| PATCH | `/api/certificates/{id}/issue/` | Emitir certificado (+ email) |
| PATCH | `/api/certificates/{id}/revoke/` | Revocar |
| GET | `/api/certificates/verify/{code}/` | Verificación pública (AllowAny) |

### Recursos (1 endpoint)

| Método | Endpoint | Descripción |
|---|---|---|
| CRUD | `/api/resources/` | Materiales docentes (PDF, audio, video) |

### Mensajería (2 endpoints)

| Método | Endpoint | Descripción |
|---|---|---|
| CRUD | `/api/threads/` | Hilos de chat |
| GET/POST | `/api/threads/{id}/messages/` | Mensajes del hilo |
| POST | `/api/messages/{id}/read/` | Marcar como leído |

> **Nota:** Al enviar mensaje REST, se notifica vía push a los otros participantes.

### Foro (5 endpoints)

| Endpoint | Descripción |
|---|---|
| `/api/forum-categories/` | Categorías (admin escribe) |
| `/api/forum-threads/` | Hilos + `pin/`, `close/` (admin) |
| `/api/forum-posts/` | Publicaciones (soft-delete) |
| `/api/forum-reactions/` | Reacciones (upsert: 1 reacción/usuario/post) |
| `/api/forum-reports/` | Reportes |

### Feed Social (3 endpoints)

| Endpoint | Descripción |
|---|---|
| `/api/social-posts/` | Feed público + `mine/` |
| `/api/social-comments/` | Comentarios (`?post=id`) |
| `/api/social-reactions/` | Reacciones (upsert) |

### Videotutoría (1 endpoint)

| Método | Endpoint | Acceso |
|---|---|---|
| CRUD | `/api/live-sessions/` | Teacher crea, todos ven |
| POST | `/api/live-sessions/{id}/join/` | Unirse (control de capacidad) |
| POST | `/api/live-sessions/{id}/leave/` | Salir |
| GET | `/api/live-sessions/{id}/participants/` | Participantes |
| POST | `/api/live-sessions/{id}/start/` | Iniciar (scheduled → live) |
| POST | `/api/live-sessions/{id}/end/` | Finalizar (live → ended) |

### Multimedia (2 endpoints)

| Endpoint | Descripción |
|---|---|
| `/api/media-files/` | Subir/administrar archivos (teacher/admin) |
| `/api/media-progress/` | Progreso reproducción + `resume/{lesson_id}/` (upsert) |

### Notificaciones (3 endpoints)

| Endpoint | Descripción |
|---|---|
| `/api/announcements/` | Anuncios globales (solo lectura) |
| `/api/notifications/` | Notificaciones + `read/`, `read-all/`, `unread-count/` |
| `/api/preferences/` | Preferencias de notificación |

### Interacciones (5 endpoints)

| Endpoint | Modelo | Descripción |
|---|---|---|
| `/api/favorites/` | UserFavorite | Favoritos (cursos/lecciones) |
| `/api/reports/` | Report | Reportes del sistema |
| `/api/feedbacks/` | UserFeedback | Feedback de usuarios |
| `/api/media/` | MediaAsset | Assets multimedia |
| `/api/activity-logs/` | UserActivityLog | Registro de actividad |

### Sistema (2 endpoints, solo admin)

| Endpoint | Descripción |
|---|---|
| `/api/maintenance/` | Registro de mantenimiento |
| `/api/backups/` | Historial de backups |

### Búsqueda Global

| Parámetro | Descripción |
|---|---|
| `GET /api/search/?q=texto` | Búsqueda en cursos, lecciones, recursos, foro, sesiones |
| `?type=cursos` | Filtrar por tipo (cursos, lecciones, usuarios, recursos, foro, sesiones) |
| `?limit=10` | Limitar resultados (default 5, max 20) |

### Documentación

| URL | Formato |
|---|---|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | Redoc UI |
| `/api/schema/` | OpenAPI Schema (JSON) |

---

## Instalación y Desarrollo Local

### Prerrequisitos
- Python 3.11+
- PostgreSQL 14+ (o SQLite para pruebas)
- Git

### Pasos

```bash
# 1. Clonar
git clone https://github.com/Axel-25-dg/idiomas_api_guaman_danny.git
cd idiomas_api_guaman_danny

# 2. Entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# Editar .env con tus datos

# 5. Base de datos
createdb languageapi_db
# o con SQL: CREATE DATABASE languageapi_db;

# 6. Migraciones
python manage.py migrate

# 7. Superusuario
python manage.py createsuperuser

# 8. Ejecutar
python manage.py runserver
```

**Accesos:**
- API: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/
- Swagger: http://127.0.0.1:8000/api/docs/
- Redoc: http://127.0.0.1:8000/api/redoc/

---

## Despliegue en Producción (VPS)

### Servidor
- **Proveedor:** Hetzner Cloud
- **SO:** Ubuntu 22.04 LTS
- **Dominio:** guaman-idiomas-ute.online

### Configuración PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb languageapi_db
sudo -u postgres createuser --superuser api_user
```

### Gunicorn (systemd)

Archivo: `/etc/systemd/system/gunicorn-shopapi.service`
```ini
[Unit]
Description=Gunicorn JumpUp API
After=network.target

[Service]
User=root
WorkingDirectory=/root/idiomas_api_guaman_danny
ExecStart=/root/idiomas_api_guaman_danny/.venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable gunicorn-shopapi
sudo systemctl start gunicorn-shopapi
```

### Nginx

```nginx
server {
    listen 80;
    server_name guaman-idiomas-ute.online;

    location /static/ {
        alias /root/idiomas_api_guaman_danny/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### CI/CD (GitHub Actions)

Cada push a `main` ejecuta automáticamente:
```
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn-shopapi.service
```

---

## Testing

```bash
# Todos los tests
python manage.py test learning --verbosity=2

# Tests específicos
python manage.py test learning.tests.test_roles_and_permissions
python manage.py test learning.tests.test_api
python manage.py test learning.tests.test_websockets
```

29 tests cubren: registro, login, roles, sincronización de flags, permisos por rol, migración de datos, WebSockets.

---

## Variables de Entorno (.env)

```env
SECRET_KEY=tu_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,guaman-idiomas-ute.online

# Base de datos
DB_NAME=languageapi_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# Archivos multimedia
FILE_UPLOAD_MAX_MEMORY_SIZE=26214400
DATA_UPLOAD_MAX_MEMORY_SIZE=52428800

# Email SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=contraseña_app
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=tu_correo@gmail.com
FRONTEND_URL=http://localhost:3000
PASSWORD_RESET_TIMEOUT=86400

# Seguridad
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# CORS
CORS_ALLOW_ALL_ORIGINS=True

# OpenAI (Tutor IA)
OPENAI_API_KEY=sk-...
```

---

## Migraciones

| Migración | Fecha | Descripción |
|---|---|---|
| `0001_initial` | 28 May | Modelos base: Role, User, Course, Module, Lesson, Exercise, etc. |
| `0002_order` | 04 Jun | Modelo Order |
| `0003_seed_roles` | 04 Jun | Seed de roles admin/teacher/student |
| `0004_classroom` | 05 Jun | Classroom, Certificate, TeacherResource |
| `0005_mediafile` | 09 Jun | MediaFile + soft-deletes + MediaFile FKs |
| `0006_emaillog` | 09 Jun | EmailLog |
| `0007_broadcast` | 10 Jun | BroadcastEmail |
| `0008_notifications` | 27 Jun | BackupHistory, Announcement, Notification, etc. |
| `0009_languages_m2m` | 07 Jul | M2M languages_learning/teaching en UserProfile |
| `0010_forum_messaging` | 08 Jul | Forum, Messaging, Social, LiveSession, MediaProgress |
| `0011_notification_type` | 08 Jul | Tipo + uuid en Notification |
| `0012_2fa` | 09 Jul | ~~is_2fa_enabled~~ (eliminada) |
| `0013_remove_2fa` | 09 Jul | Elimina campo is_2fa_enabled de UserProfile |

**seguridad_acceso:**
| Migración | Descripción |
|---|---|
| `0001_initial` | PasswordReset, LoginAttempt, TwoFactorAuth, BiometricDevice, etc. |
| `0002_delete_2fa` | Elimina modelo TwoFactorAuth |

---

## Historial de Cambios

### v1.4 — 09 Jul 2026
- **Eliminada verificación en dos pasos (2FA)**
  - Removido campo `is_2fa_enabled` de `UserProfile`
  - Eliminado modelo `TwoFactorAuth` de `seguridad_acceso`
  - Eliminados `Verify2FAView`, `Verify2FASerializer`, ruta `auth/2fa/verify/`
  - Eliminado `send_2fa_code_email` y template asociado
- **Rediseño completo de templates de correo**
  - Base con gradientes, sombras y tipografía moderna
  - Todos los templates profesionales: welcome, PIN reset, certificate, payment, etc.
  - Responsive design para móvil

### v1.3 — 07 Jul 2026
- Módulo Mensajería (threads, messages, attachments)
- Módulo Foro (categorías, hilos, posts, reacciones, reportes)
- Feed Social (posts, comments, reactions)
- Centro de Notificaciones mejorado
- Videotutoría en vivo
- Multimedia (MediaFile, MediaProgress)
- Búsqueda global

### v1.2 — 07 Jul 2026
- Campos `languages_learning`/`languages_teaching` en UserProfile
- Endpoint `PATCH /api/auth/profile/update-languages/`

### v1.1 — Inicial
- Sistema base de autenticación y cursos
- Gamificación con XP, rachas y logros
- Suscripciones y pagos
- Aulas virtuales y certificados

---

## Licencia

Universidad Tecnológica Equinoccial — UTE

Facultad de Ciencias de la Ingeniería e Industrias

Desarrollado por Danny Guamán, Alex Macias, Ariel Paucar — 2026
