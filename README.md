<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/UTE_logo.svg/512px-UTE_logo.svg.png" width="160" alt="Universidad UTE"/>

<br/>
<br/>

# JumpUp UTE — API de Aprendizaje de Idiomas

**Backend REST para Plataforma Educativa de Idiomas**

Desarrollado con Django REST Framework + PostgreSQL

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.14+-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
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

---

## Descripción del Sistema

JumpUp UTE es una API REST completa para una plataforma de aprendizaje de idiomas. Permite gestionar cursos por niveles MCER (A1-C2), gamificación con XP y logros, clases virtuales con código de acceso, certificados verificables, suscripciones y pagos. Implementa autenticación JWT con tres roles diferenciados (admin, teacher, student) y permisos granulares.

---

## Base de Datos — 36 Tablas

| # | Modelo | Tabla | Relaciones |
|---|---|---|---|
| 1 | Role | `learning_role` | OneToMany → User |
| 2 | User | `learning_user` | FK → Role |
| 3 | UserProfile | `learning_userprofile` | OneToOne → User, M2M → Language (aprender), M2M → Language (enseñar) |
| 4 | Language | `learning_language` | OneToMany → Course |
| 5 | Course | `learning_course` | FK → Language |
| 6 | Module | `learning_module` | FK → Course |
| 7 | Lesson | `learning_lesson` | FK → Module |
| 8 | Exercise | `learning_exercise` | FK → Lesson |
| 9 | UserProgress | `learning_userprogress` | FK → User, Lesson |
| 10 | UserStats | `learning_userstats` | OneToOne → User |
| 11 | Achievement | `learning_achievement` | — |
| 12 | UserAchievement | `learning_userachievement` | FK → User, Achievement |
| 13 | Subscription | `learning_subscription` | — |
| 14 | UserSubscription | `learning_usersubscription` | FK → User, Subscription |
| 15 | Payment | `learning_payment` | FK → User |
| 16 | Order | `learning_order` | FK → User, Subscription |
| 17 | Classroom | `learning_classroom` | FK → User(teacher), Course, M2M → User(students) |
| 18 | ClassroomEnrollment | `learning_classroomenrollment` | FK → Classroom, User |
| 19 | Certificate | `learning_certificate` | FK → User(student), User(issued_by) |
| 20 | TeacherResource | `learning_teacherresource` | FK → User(teacher), Course, Lesson |
| 21 | MediaFile | `learning_mediafile` | FK → User(uploaded_by) |
| 22 | MessageThread | `learning_messagethread` | M2M → User(participants) |
| 23 | Message | `learning_message` | FK → MessageThread, User(sender) |
| 24 | MessageAttachment | `learning_messageattachment` | FK → Message |
| 25 | ForumCategory | `learning_forumcategory` | OneToMany → ForumThread |
| 26 | ForumThread | `learning_forumthread` | FK → ForumCategory, User |
| 27 | ForumPost | `learning_forumpost` | FK → ForumThread, User, self(parent) |
| 28 | ForumReaction | `learning_forumreaction` | FK → User, ForumPost |
| 29 | ForumReport | `learning_forumreport` | FK → User(reporter), ForumPost |
| 30 | SocialPost | `learning_socialpost` | FK → User |
| 31 | SocialComment | `learning_socialcomment` | FK → SocialPost, User |
| 32 | SocialReaction | `learning_socialreaction` | FK → User, SocialPost |
| 33 | LiveSession | `learning_livesession` | FK → User(teacher), Course |
| 34 | LiveParticipant | `learning_liveparticipant` | FK → LiveSession, User |
| 35 | MediaProgress | `learning_mediaprogress` | FK → User, Lesson |
| 36 | Notification | `learning_notification` | FK → User |

**Relaciones implementadas:**
- OneToOne: User ↔ UserProfile, User ↔ UserStats
- OneToMany: Language → Course → Module → Lesson → Exercise
- ManyToMany: Classroom ↔ Students (through ClassroomEnrollment), UserProfile ↔ Language (`languages_learning` para estudiantes, `languages_teaching` para profesores), MessageThread ↔ Participants

---

## Endpoints Completos

### Prerrequisitos
- Python 3.11+
- PostgreSQL 14+
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/Axel-25-dg/idiomas_api_guaman_danny.git
cd idiomas_api_guaman_danny
```

### 2. Crear y activar entorno virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env`:
```env
SECRET_KEY=tu_clave_secreta
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

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

### 8. Ejecutar servidor

```bash
python manage.py runserver
```

- API: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/
- Swagger: http://127.0.0.1:8000/api/docs/
- Redoc: http://127.0.0.1:8000/api/redoc/

---

## Despliegue en VPS (Producción)

### Servidor
- **Proveedor:** Hetzner Cloud
- **SO:** Ubuntu 22.04 LTS
- **IP/Dominio:** guaman-idiomas-ute.online

### Configuración de PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb languageapi_db
sudo -u postgres createuser --superuser api_user
```

### Configuración de Gunicorn

```bash
pip install gunicorn
```

Archivo systemd: `/etc/systemd/system/gunicorn-shopapi.service`
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

### Configuración de Nginx

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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### CI/CD con GitHub Actions

Cada push a `main` ejecuta automáticamente:
```
git pull → pip install → migrate → collectstatic → restart gunicorn
```

---

## Uso de la API

### Obtener token JWT

```bash
curl -X POST https://guaman-idiomas-ute.online/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@email.com", "password": "Pass123!"}'
```

Respuesta:
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {"id": 1, "email": "admin@email.com", "role": "admin", "is_staff": true}
}
```

### Usar endpoints protegidos

```bash
curl https://guaman-idiomas-ute.online/api/courses/ \
  -H "Authorization: Bearer eyJ..."
```

### Ejemplo: Crear un curso (teacher/admin)

```bash
curl -X POST https://guaman-idiomas-ute.online/api/courses/ \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"language": 1, "title": "Inglés A1", "description": "Curso básico", "difficulty_level": "A1"}'
```

---

## Endpoints Completos

### Autenticación (Público / Perfil)
| Método | URL | Descripción |
|---|---|---|
| POST | `/api/auth/register/` | Registro (auto-asigna role=student) |
| POST | `/api/auth/login/` | Login → access + refresh + user |
| POST | `/api/auth/token/refresh/` | Renovar token |
| GET | `/api/auth/me/` | Perfil del usuario autenticado |
| PATCH | `/api/auth/profile/update-languages/` | Actualizar idiomas según rol (estudiante: `languages_learning`, profesor: `languages_teaching`) |

> **Reglas del endpoint `update-languages`:**
> - **student / premium_student** → solo puede enviar `languages_learning` (idiomas que quiere aprender)
> - **teacher / assistant_teacher** → solo puede enviar `languages_teaching` (idiomas que enseña)
> - Enviar el campo incorrecto para el rol retorna `400 Bad Request`
>
> Ejemplo (student):
> ```json
> PATCH /api/auth/profile/update-languages/
> { "languages_learning": [1, 3] }
> ```
> Ejemplo (teacher):
> ```json
> PATCH /api/auth/profile/update-languages/
> { "languages_teaching": [2] }
> ```

### Dashboards
| Método | URL | Acceso |
|---|---|---|
| GET | `/api/dashboard/student/` | Student |
| GET | `/api/dashboard/teacher/` | Teacher/Admin |
| GET | `/api/dashboard/admin/` | Admin |

### Contenido Educativo
| Método | URL | Lectura | Escritura |
|---|---|---|---|
| GET/POST/PUT/DELETE | `/api/languages/` | Todos | Admin |
| GET/POST/PUT/DELETE | `/api/courses/` | Todos | Teacher/Admin |
| GET/POST/PUT/DELETE | `/api/modules/` | Todos | Teacher/Admin |
| GET/POST/PUT/DELETE | `/api/lessons/` | Todos | Teacher/Admin |
| GET/POST/PUT/DELETE | `/api/exercises/` | Todos | Teacher/Admin |

### Progreso y Gamificación
| Método | URL | Descripción |
|---|---|---|
| GET/POST | `/api/progress/` | Progreso por lección |
| GET | `/api/progress/summary/` | Resumen completo |
| GET | `/api/stats/` | XP, nivel, rachas |
| GET | `/api/achievements/` | Catálogo de logros |
| GET | `/api/my-achievements/` | Logros desbloqueados |
| GET | `/api/ranking/` | Top 100 por XP |

### Clases Virtuales
| Método | URL | Descripción |
|---|---|---|
| GET/POST | `/api/classrooms/` | CRUD clases (teacher) |
| GET | `/api/classrooms/{id}/` | Detalle con alumnos |
| POST | `/api/classrooms/join/` | Unirse con código |
| GET | `/api/classrooms/mine/` | Mis clases (student) |
| POST | `/api/classrooms/{id}/remove-student/` | Expulsar alumno |

### Recursos
| Método | URL | Descripción |
|---|---|---|
| GET/POST/PUT/DELETE | `/api/resources/` | Materiales (PDF, audio, video, word) |

### Certificados
| Método | URL | Descripción |
|---|---|---|
| GET/POST | `/api/certificates/` | CRUD certificados |
| PATCH | `/api/certificates/{id}/issue/` | Emitir |
| PATCH | `/api/certificates/{id}/revoke/` | Revocar |
| GET | `/api/certificates/verify/{code}/` | Verificación pública |

### Suscripciones y Pagos
| Método | URL | Descripción |
|---|---|---|
| GET/POST | `/api/subscriptions/` | Planes (admin crea) |
| GET/POST | `/api/my-subscriptions/` | Suscribirse |
| GET/POST | `/api/payments/` | Registrar pagos |
| GET/POST | `/api/orders/` | Órdenes de compra |
| GET | `/api/orders/stats/` | Estadísticas (admin) |

### Gestión de Usuarios (Admin)
| Método | URL | Descripción |
|---|---|---|
| GET/POST/PATCH/DELETE | `/api/users/` | Staff (teachers/admins) |
| GET/PATCH/DELETE | `/api/admin-students/` | Estudiantes |

### Mensajería y Comunicación
| Método | URL | Descripción |
|---|---|---|
| GET/POST | `/api/threads/` | Hilos del usuario / crear hilo |
| GET | `/api/threads/{id}/` | Detalle del hilo |
| DELETE | `/api/threads/{id}/` | Desactivar hilo |
| GET/POST | `/api/threads/{id}/messages/` | Mensajes del hilo / enviar mensaje |
| POST | `/api/messages/{id}/read/` | Marcar mensaje como leído |

### Comunidad — Foro
| Método | URL | Descripción |
|---|---|---|
| GET | `/api/forum-categories/` | Categorías activas |
| POST/PUT/DELETE | `/api/forum-categories/` | CRUD (admin) |
| GET/POST | `/api/forum-threads/` | Hilos del foro |
| POST | `/api/forum-threads/{id}/pin/` | Fijar/desfijar hilo (admin) |
| POST | `/api/forum-threads/{id}/close/` | Cerrar/abrir hilo (admin) |
| GET/POST | `/api/forum-posts/` | Posts (filtrar por `?thread=id`) |
| POST | `/api/forum-reactions/` | Reaccionar a un post (upsert) |
| GET/POST | `/api/forum-reports/` | Reportar post / gestionar reportes (admin) |

### Feed Social
| Método | URL | Descripción |
|---|---|---|
| GET/POST | `/api/social-posts/` | Feed público |
| GET | `/api/social-posts/mine/` | Solo mis publicaciones |
| GET/POST | `/api/social-comments/` | Comentarios (filtrar por `?post=id`) |
| POST | `/api/social-reactions/` | Reaccionar a post (upsert) |

### Centro de Notificaciones
| Método | URL | Descripción |
|---|---|---|
| GET | `/api/notifications/` | Mis notificaciones |
| GET | `/api/notifications/?is_read=false` | Solo no leídas |
| GET | `/api/notifications/?type=course` | Filtrar por tipo (course, payment, certificate...) |
| POST | `/api/notifications/{id}/read/` | Marcar una como leída |
| POST | `/api/notifications/read-all/` | Marcar todas como leídas |
| GET | `/api/notifications/unread-count/` | Cantidad de no leídas |

### Videotutoría — Sesiones en Vivo
| Método | URL | Acceso |
|---|---|---|
| GET/POST | `/api/live-sessions/` | Listar / crear sesión |
| GET | `/api/live-sessions/{id}/` | Detalle con participantes |
| POST | `/api/live-sessions/{id}/join/` | Unirse a sesión |
| POST | `/api/live-sessions/{id}/leave/` | Salir de sesión |
| GET | `/api/live-sessions/{id}/participants/` | Lista de participantes |
| POST | `/api/live-sessions/{id}/start/` | Iniciar sesión (teacher/admin) |
| POST | `/api/live-sessions/{id}/end/` | Finalizar sesión (teacher/admin) |

### Multimedia
| Método | URL | Descripción |
|---|---|---|
| GET | `/api/media-files/` | Listar archivos multimedia |
| POST | `/api/media-files/` | Subir archivo (teacher/admin) |
| GET/PATCH | `/api/media-progress/` | Ver / actualizar progreso de reproducción |
| POST | `/api/media-progress/` | Registrar/iniciar progreso (upsert) |
| GET | `/api/media-progress/resume/{lesson_id}/` | Reanudar desde donde se dejó |

### Búsqueda Global
| Método | URL | Descripción |
|---|---|---|
| GET | `/api/search/?q=<término>` | Búsqueda en cursos, lecciones, recursos, foro y sesiones |
| GET | `/api/search/?q=<término>&type=cursos` | Filtrar por tipo: `cursos`, `lecciones`, `usuarios` (admin), `recursos`, `foro`, `sesiones` |
| GET | `/api/search/?q=<término>&limit=10` | Limitar resultados por tipo (default 5, max 20) |

### Documentación
| URL | Formato |
|---|---|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | Redoc |
| `/api/schema/` | OpenAPI JSON |

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.11+ | Lenguaje |
| Django 4.2+ | Framework |
| Django REST Framework 3.14+ | API REST |
| drf-spectacular 0.27+ | Documentación Swagger/Redoc |
| djangorestframework-simplejwt 5.3+ | JWT |
| django-cors-headers 4.0+ | CORS |
| django-filter 23.0+ | Filtros |
| psycopg2-binary 2.9+ | PostgreSQL |
| python-decouple 3.8+ | Variables de entorno |
| PostgreSQL 14+ | Base de datos |
| Gunicorn | WSGI Server |
| Nginx | Proxy inverso |
| GitHub Actions | CI/CD |

---

## Testing

```bash
python manage.py test learning --verbosity=2
```

29 tests cubren: registro, login, roles, sincronización de flags, permisos por rol, migración de datos.

---

## Cambios Recientes

### v1.3 — 07 Jul 2026 (Módulos pendientes implementados)
- **Módulo Mensajería:** vistas y rutas para `MessageThread`, `Message`, `MessageAttachment`
  - `GET/POST /api/threads/` y `GET/POST /api/threads/{id}/messages/`
  - Marcar mensajes como leídos automáticamente al listar
  - `POST /api/messages/{id}/read/` para marcar individualmente
- **Módulo Foro:** CRUD completo para `ForumCategory`, `ForumThread`, `ForumPost`, `ForumReaction`, `ForumReport`
  - Incremento de vistas al abrir un hilo
  - Soft-delete en posts (`is_deleted=True`)
  - Acciones admin: `pin` y `close` en hilos
  - Upsert en reacciones (una reacción por usuario por post)
- **Feed Social:** vistas y rutas para `SocialPost`, `SocialComment`, `SocialReaction`
  - Feed de publicaciones públicas + las propias del usuario
  - Upsert en reacciones
  - `GET /api/social-posts/mine/`
- **Centro de Notificaciones:** mejorado con filtros y nuevas acciones
  - Filtrar por `is_read` y `type`
  - `POST /api/notifications/{id}/read/` — marcar una como leída
  - `POST /api/notifications/read-all/` — marcar todas como leídas
  - `GET /api/notifications/unread-count/` — contador de no leídas
- **Videotutoría:** vistas para `LiveSession` y `LiveParticipant`
  - Unirse/salir de sesión con control de capacidad
  - Transiciones de estado: `scheduled → live → ended`
  - Registro automático de `left_at` al finalizar
- **Multimedia:** serializers y vistas para `MediaFile` y `MediaProgress`
  - Upsert de progreso (no duplica si ya existe)
  - `GET /api/media-progress/resume/{lesson_id}/` — reanudar reproducción
- **Búsqueda Global:** `GET /api/search/?q=<término>`
  - Busca en cursos, lecciones, recursos, foro y sesiones
  - Filtro por tipo con `?type=cursos|lecciones|recursos|foro|sesiones|usuarios`
  - Usuarios solo visibles para admins
- **Migración `0010`:** tablas para Forum, Messaging, Social, LiveSession, MediaProgress
- **Serializers exportados:** todos los nuevos serializers agregados a `serializers/__init__.py`

### v1.2 — 07 Jul 2026 (`new_act` / `new_act_read`)
- **Nuevo:** campos `languages_learning` y `languages_teaching` (ManyToMany → Language) en `UserProfile`
  - Migración `0009_userprofile_languages_learning_and_more`
  - `languages_learning`: idiomas que el estudiante quiere aprender (`related_name='student_profiles'`)
  - `languages_teaching`: idiomas que el profesor enseña (`related_name='teacher_profiles'`)
- **Nuevo:** endpoint `PATCH /api/auth/profile/update-languages/` con validación por rol
  - students/premium_students → actualizan `languages_learning`
  - teachers/assistant_teachers → actualizan `languages_teaching`
- **Actualizado:** `UserProfileSerializer` para exponer y validar ambos campos M2M
- **Actualizado:** `learning/urls.py` para registrar la nueva ruta

---

## Autor

<div align="center">

Universidad Tecnológica Equinoccial — UTE

Facultad de Ciencias de la Ingeniería e Industrias

</div>
