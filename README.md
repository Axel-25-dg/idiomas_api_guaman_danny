<div align="center">

<img src="https://jumpup.com.ec/wp-content/uploads/2023/01/Logo-JumpUp-Color.png" width="200" alt="JumpUp"/>

<br/>
<br/>

# JumpUp — API de Aprendizaje de Idiomas

**Backend REST + WebSocket para Plataforma Educativa de Idiomas**

Desarrollado con Django · Django REST Framework · PostgreSQL · Django Channels · OpenAI GPT-4o

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.14+-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-SimpleJWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Channels](https://img.shields.io/badge/Django_Channels-WebSocket-44B39D?style=for-the-badge&logo=django&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-Docs-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

</div>

---

## Información del Proyecto

| Campo | Detalle |
|---|---|
| **Proyecto** | JumpUp — Plataforma de Aprendizaje de Idiomas |
| **Autor** | Danny Guamán |
| **Carrera** | Ingeniería en Desarrollo de Software |
| **Universidad** | Universidad Tecnológica Equinoccial (UTE) |
| **Materia** | Seminario de Integración |
| **Repositorio** | https://github.com/Axel-25-dg/idiomas_api_guaman_danny |
| **URL Pública** | https://guaman-idiomas-ute.online |
| **Documentación API** | https://guaman-idiomas-ute.online/api/docs/ |
| **Redoc** | https://guaman-idiomas-ute.online/api/redoc/ |

---

## Descripción del Sistema

JumpUp es una plataforma completa de aprendizaje de idiomas que combina una API REST con WebSockets en tiempo real. El sistema está orientado a tres tipos de usuarios (administradores, profesores y estudiantes) y ofrece:

- **Cursos** por niveles MCER (A1–C2) con módulos, lecciones y ejercicios
- **Gamificación** con XP, rachas diarias, logros automáticos y ranking global
- **Tutor IA** integrado con OpenAI GPT-4o vía WebSocket
- **Aulas virtuales** con código de acceso para clases privadas
- **Certificados** verificables públicamente por nivel MCER
- **E-commerce propio** con catálogo, carrito y órdenes de compra (venta directa)
- **Foro comunitario** con categorías, hilos, posts anidados y reacciones
- **Feed social** con publicaciones, comentarios y reacciones entre estudiantes
- **Mensajería directa** en tiempo real vía WebSocket
- **Videotutoría en vivo** con señalización WebRTC
- **Notificaciones push** en tiempo real por WebSocket
- **Autenticación JWT** con 3 roles + login biométrico por dispositivo
- **Seguridad** con bloqueo de IPs, monitoreo de sesiones y alertas

---

## Stack Tecnológico

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.11+ | Lenguaje principal |
| Django | 4.2+ | Framework web |
| Django REST Framework | 3.14+ | API REST |
| Django Channels | 4.0+ | WebSockets / ASGI |
| Daphne | 4.0+ | Servidor ASGI |
| Channels Redis | 4.1+ | Channel Layer (WebSockets en producción) |
| djangorestframework-simplejwt | 5.3+ | Autenticación JWT |
| drf-spectacular | 0.27+ | Documentación Swagger / Redoc |
| django-cors-headers | 4.0+ | CORS |
| django-filter | 23.0+ | Filtros en la API |
| psycopg2-binary | 2.9+ | Driver PostgreSQL |
| python-decouple | 3.8+ | Variables de entorno |
| Pillow | 10.0+ | Procesamiento de imágenes |
| OpenAI | 1.0+ | Tutor IA (GPT-4o) |
| Stripe | 8.0+ | Integración de pagos (modo test) |
| PostgreSQL | 16 | Base de datos principal |
| SQLite | — | Base de datos en tests locales |
| Gunicorn | — | Servidor WSGI HTTP |
| Nginx | — | Proxy inverso |
| Redis | — | Channel Layer (WebSockets) |
| GitHub Actions | — | CI/CD automatizado |
| Hetzner Cloud | — | VPS (Ubuntu 22.04 LTS) |

---

## Arquitectura del Sistema

```
App Móvil (Flutter)
       │
       ├── HTTPS (REST API) ──────────────────────┐
       ├── WebSocket (ws/wss) ────────────────────┤
       │                                          ▼
       │                          ┌───────────────────────────┐
       │                          │  Nginx (Proxy Inverso)    │
       │                          └──────────┬────────────────┘
       │                                     │
       │                    ┌────────────────┴────────────────┐
       │                    │  Gunicorn (HTTP)  Daphne (WS)   │
       │                    └────────────────┬────────────────┘
       │                                     │
       │                          ┌──────────▼──────────┐
       │                          │   Django + Channels  │
       │                          │   REST API + WS      │
       │                          └──────────┬──────────┘
       │                                     │
       │           ┌─────────────────────────┼──────────────────┐
       │           │                         │                   │
       │     ┌─────▼──────┐        ┌─────────▼──────┐   ┌───────▼────┐
       │     │ PostgreSQL │        │  Redis (Channels│   │  OpenAI /  │
       │     │  (datos)   │        │  Channel Layer) │   │   SMTP     │
       │     └────────────┘        └────────────────┘   └────────────┘
       │
       └── JSON / WebSocket Events ◄──────────────────────────
```

### Capas internas del backend

```
┌─────────────────────────────────────────────────────────────┐
│               HTTP (REST) / WebSocket                       │
│          Gunicorn (WSGI) + Daphne (ASGI)                    │
├─────────────────────────────────────────────────────────────┤
│                Django Channels (Redis)                      │
│        Chat · Notificaciones · Sesiones en vivo             │
├─────────────────────────────────────────────────────────────┤
│             Django REST Framework                           │
│      43 ViewSets · 9 APIViews · 50+ Serializers             │
├─────────────────────────────────────────────────────────────┤
│              Capa de Negocio (Services + Signals)           │
│  GamificationService · EmailService · AIService             │
│  Signals: XP · Rachas · Logros · Notificaciones             │
├─────────────────────────────────────────────────────────────┤
│                    Capa de Modelos                          │
│         57 modelos en 3 apps (learning principal)           │
├─────────────────────────────────────────────────────────────┤
│                 PostgreSQL 16                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Estructura de Aplicaciones

```
config/                    ← Configuración global (settings, urls, asgi, wsgi)
learning/                  ← App principal
  models/                  ← 48 modelos organizados por dominio
  views/                   ← ViewSets + APIViews separados por módulo
  serializers/             ← Serializadores
  consumers/               ← WebSocket consumers (chat, notificaciones, live)
  services/                ← Lógica de negocio (AI, email, gamificación)
  migrations/              ← 16 migraciones históricas
  signals.py               ← Automatizaciones (XP, logros, notificaciones)
  filters.py               ← Filtros de búsqueda
  middleware.py            ← JWT middleware para WebSockets
dispositivos_alertas/      ← Dispositivos, ubicaciones y alertas de seguridad
seguridad_acceso/          ← Sesiones, intentos de login, IPs bloqueadas
templates/emails/          ← Templates HTML de correos transaccionales
```

---

## Base de Datos — 57 Tablas

### App `learning` (48 modelos principales)

| # | Modelo | Descripción |
|---|---|---|
| 1 | `Role` | Roles del sistema: admin, teacher, student |
| 2 | `User` | Usuario personalizado (email = USERNAME_FIELD, soft-delete, sincronización de flags) |
| 3 | `UserProfile` | Perfil extendido: avatar, idioma nativo, timezone, idiomas de aprendizaje/enseñanza |
| 4 | `Language` | Idiomas disponibles con código, slug e ícono |
| 5 | `Course` | Cursos por idioma y nivel MCER (A1–C2), slug automático, soft-delete |
| 6 | `Module` | Módulos dentro de un curso, ordenados y únicos por posición |
| 7 | `Lesson` | Lecciones con tipo de contenido (video/text/interactive/audio) y XP reward |
| 8 | `Exercise` | Ejercicios: multiple_choice, translate, listen, fill_blank, match. Soporte JSON de opciones y audio |
| 9 | `UserProgress` | Progreso por lección (in_progress / completed), score y timestamp de completado |
| 10 | `UserStats` | XP total, racha actual, racha máxima, última actividad. Nivel calculado (cada 100 XP) |
| 11 | `Achievement` | Logros configurables por trigger: XP, racha, cursos completados, manual |
| 12 | `UserAchievement` | Logros desbloqueados por usuario con timestamp |
| 13 | `Classroom` | Aulas virtuales con código de acceso de 8 caracteres, vinculadas a curso y profesor |
| 14 | `ClassroomEnrollment` | Inscripción estudiante-aula con timestamps |
| 15 | `Certificate` | Certificados MCER con código único verificable (`CERT-A1-XXXXXXXX`) |
| 16 | `TeacherResource` | Materiales del profesor (PDF, audio, video) |
| 17 | `MediaFile` | Archivos multimedia con checksum SHA-256, conversión WebP y thumbnail automático |
| 18 | `MediaProgress` | Posición de reproducción en segundos para video/audio |
| 19 | `EmailLog` | Registro de cada correo enviado (pending/sent/failed) |
| 20 | `BroadcastEmail` | Envíos masivos de correo con audiencia configurable |
| 21 | `Notification` | Notificaciones individuales con tipos (system/course/payment/achievement/etc.) |
| 22 | `Announcement` | Anuncios globales con fechas de inicio/fin |
| 23 | `UserNotificationPreference` | Preferencias por canal (email, app, SMS) |
| 24 | `MessageThread` | Hilos de chat con participantes (M2M) y sujeto opcional |
| 25 | `Message` | Mensajes con is_read y read_at. Incluye mensajes del Tutor IA |
| 26 | `MessageAttachment` | Adjuntos con URL y tipo MIME |
| 27 | `ForumCategory` | Categorías del foro con ícono y orden |
| 28 | `ForumThread` | Hilos con pin, cierre y contador de vistas |
| 29 | `ForumPost` | Publicaciones con anidación (parent self-FK) y soft-delete lógico |
| 30 | `ForumReaction` | Reacciones (like/love/helpful/confused), única por usuario+post |
| 31 | `ForumReport` | Reportes con estados pending/reviewed/resolved |
| 32 | `SocialPost` | Publicaciones del feed social (logros, certificados, progreso, general) |
| 33 | `SocialComment` | Comentarios en posts del feed |
| 34 | `SocialReaction` | Reacciones al feed (like/love/clap/fire/star) |
| 35 | `LiveSession` | Sesiones en vivo (scheduled/live/ended/cancelled) con URL de meeting |
| 36 | `LiveParticipant` | Participantes con timestamps de entrada/salida |
| 37 | `Catalogo` | Productos para venta directa (cursos o libros) con precio |
| 38 | `Carrito` | Un carrito por estudiante (OneToOne) |
| 39 | `CarritoItem` | Items del carrito con cantidad |
| 40 | `Orden` | Órdenes de compra (pendiente/pagada/cancelada) con total |
| 41 | `OrdenDetalle` | Líneas de la orden con precio unitario registrado en el momento |
| 42 | `UserActivityLog` | Log de actividad del usuario por módulo/lección |
| 43 | `UserFavorite` | Cursos/lecciones favoritos (único por usuario+contenido) |
| 44 | `Report` | Reportes de abuso/bugs con estados OPEN/IN_PROGRESS/RESOLVED/REJECTED |
| 45 | `MediaAsset` | Assets multimedia subidos por usuarios |
| 46 | `UserFeedback` | Feedback con estados PENDING/REVIEWED/ARCHIVED |
| 47 | `MaintenanceLog` | Tareas de mantenimiento (SUCCESS/FAILED/IN_PROGRESS) |
| 48 | `BackupHistory` | Historial de backups con path y tamaño |

### App `seguridad_acceso` (6 tablas)

| # | Modelo | Descripción |
|---|---|---|
| 49 | `PasswordReset` | Token de reset con expiración (15 min por defecto) |
| 50 | `LoginAttempt` | Intentos de login por IP y email |
| 51 | `ActiveSession` | Sesiones activas con dispositivo, browser e IP |
| 52 | `BlockedIp` | IPs bloqueadas con motivo y duración opcional |
| 53 | `ApiToken` | Tokens de API adicionales con expiración |
| 54 | `BiometricDevice` | Dispositivos registrados para login biométrico |

### App `dispositivos_alertas` (3 tablas)

| # | Modelo | Descripción |
|---|---|---|
| 55 | `UserDevice` | Dispositivos del usuario (SO, browser, confiable/no confiable) |
| 56 | `UserLocation` | Ubicaciones geográficas con coordenadas |
| 57 | `SecurityAlert` | Alertas de seguridad con severidad (LOW/MEDIUM/HIGH/CRITICAL) |

### Modelos Base Abstractos

| Modelo | Campos | Propósito |
|---|---|---|
| `TimestampedModel` | `created_at`, `updated_at` | Timestamps automáticos en todos los modelos |
| `SoftDeleteModel` | `is_active`, `deleted_at` | Eliminación lógica — nunca borra físicamente |

---

## Roles y Permisos

| Rol | `is_staff` | `is_superuser` | Acceso Admin | Capacidades |
|---|:---:|:---:|:---:|---|
| **admin** | ✅ | ✅ | Completo | Todos los endpoints, gestión global |
| **teacher** | ✅ | ❌ | Limitado | Crear contenido, aulas, recursos, certificados |
| **student** | ❌ | ❌ | No | Consumir contenido, progreso, foro, chat |

La sincronización de flags es automática: `User.save()` llama a `sync_flags_from_role()` que ajusta `is_staff` e `is_superuser` según el role FK asignado. Esto garantiza que el panel de administración de Django respete los mismos roles que la API.

| Clase de Permiso | Acceso |
|---|---|
| `IsAdmin` | Solo administradores |
| `IsTeacher` | Solo profesores |
| `IsStudent` | Solo estudiantes |
| `IsTeacherOrAdmin` | Profesores y administradores |
| `IsAdminOrReadOnly` | Lectura autenticada, escritura solo admin |
| `IsTeacherOrAdminOrReadOnly` | Lectura autenticada, escritura para teacher/admin |

---

## Autenticación (JWT)

| Parámetro | Valor |
|---|---|
| Access token | 1 hora |
| Refresh token | 7 días (30 días con `remember_me: true`) |
| Rotación | Activada — cada refresh invalida el anterior |
| Algoritmo | HS256 |
| Campo de login | Email (no username) |

**Payload del JWT devuelto:**
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

Permite que aplicaciones móviles registren un dispositivo y autentiquen usuarios sin contraseña:

1. `POST /api/auth/biometric/register/` con el usuario autenticado por JWT → devuelve `biometric_token`
2. `POST /api/auth/biometric/login/` con `{ "device_id": "...", "biometric_token": "..." }` → devuelve JWT completo

El token biométrico es único por usuario+dispositivo y se almacena en `BiometricDevice`.

---

## Sistema de Gamificación

La gamificación opera completamente de forma automática vía **Django Signals**, sin intervención manual:

### Flujo automático al completar una lección

```
POST /api/progress/ { "lesson": 5, "status": "completed", "score": 90 }
  ↓ signal post_save(UserProgress)
  ✅ Suma lesson.xp_reward a UserStats.total_xp
  ✅ Calcula diferencia de días desde last_activity_date:
       diff=0 → mismo día, racha no cambia
       diff=1 → día consecutivo, current_streak += 1
       diff>1 → racha rota, current_streak = 1
  ✅ Actualiza longest_streak si es nuevo récord
  ✅ Registra last_activity_date = hoy
  ↓ signal post_save(UserStats)
  ✅ Revisa todos los logros activos
  ✅ Desbloquea automáticamente los que cumple
  ✅ Envía notificación WebSocket por cada logro nuevo
  → Flutter recibe: { "type": "new_notification", "notification": { "title": "🏅 Logro: Primer Paso" } }
```

### Cálculo de nivel

```
nivel = (total_xp // 100) + 1
xp_en_nivel_actual = total_xp % 100     # 0–99
xp_para_siguiente  = nivel * 100
```

### Tipos de logros

| Trigger | Condición de desbloqueo |
|---|---|
| `xp` | `total_xp >= required_xp` |
| `streak` | `current_streak >= required_value` |
| `course` | cursos completados al 100% `>= required_value` |
| `manual` | Solo desde el panel de administración |

### GamificationService

Funciones utilitarias para usar desde cualquier parte del backend:

```python
from learning.services.gamification_service import award_xp, update_streak, check_and_unlock_achievements

award_xp(user, xp=50, reason='participacion_foro')   # Suma XP manualmente
update_streak(user)                                   # Recalcula racha del día
check_and_unlock_achievements(user)                  # Verifica y desbloquea logros
get_user_level_info(user)                             # Devuelve nivel, XP, racha completa
```

---

## WebSockets (Django Channels)

La autenticación en WebSockets se hace via JWT en el query string o en el header. El middleware `JwtAuthMiddleware` extrae el token y lo valida antes de establecer la conexión.

| URL de conexión | Propósito |
|---|---|
| `ws://host/ws/chat/{thread_id}/?token=JWT` | Chat en tiempo real + Tutor IA |
| `ws://host/ws/notifications/?token=JWT` | Notificaciones push en tiempo real |
| `ws://host/ws/live-session/{session_id}/?token=JWT` | Señalización WebRTC para videotutoría |

### Consumer de Chat (`ws/chat/<thread_id>/`)

Solo participantes del hilo pueden conectarse. Soporta mensajes, indicadores de escritura y confirmaciones de lectura.

```
Cliente → Servidor:
{ "type": "chat_message",  "body": "Hola!"         }
{ "type": "typing",        "is_typing": true        }
{ "type": "read_message",  "message_id": 42         }

Servidor → Cliente:
{ "type": "chat_message",  "message": { "id", "sender", "body", "created_at" } }
{ "type": "typing",        "username": "...", "is_typing": true }
{ "type": "read_receipt",  "message_id": 42, "reader_id": 3 }
{ "type": "error",         "detail": "..." }
```

**Tutor IA integrado:** Si el hilo tiene 1 solo participante o el asunto contiene `"IA"`, cada mensaje activa una llamada asíncrona a GPT-4o. El bot responde como usuario real (`ia@jumpup.com`) con indicador de "escribiendo..." intermedio.

### Consumer de Notificaciones (`ws/notifications/`)

Al conectar, el servidor envía inmediatamente el conteo de no leídas.

```
Al conectar:   { "type": "unread_count", "count": 5 }
Notificación:  { "type": "new_notification", "notification": { "id", "title", "message", "type" } }

Cliente → Servidor:
{ "type": "mark_read",     "notification_id": 12 }
{ "type": "mark_all_read" }
```

Desde el backend se puede enviar una notificación a cualquier usuario en tiempo real:
```python
from learning.signals import push_ws_notification
push_ws_notification(user_id=5, title="Título", message="Cuerpo", notif_type="system")
```

### Consumer de Sesión en Vivo (`ws/live-session/<session_id>/`)

Implementa señalización WebRTC completa para videollamadas entre profesor y estudiantes.

```
{ "type": "offer",         "sdp": "...", "target": 3     }
{ "type": "answer",        "sdp": "...", "target": 3     }
{ "type": "ice_candidate", "candidate": "...", "target": 3 }

Servidor → todos los participantes:
{ "type": "user_joined",   "user_id": 5, "username": "..." }
{ "type": "user_left",     "user_id": 5 }
{ "type": "participants",  "users": [...] }
```

---

## Tutor IA (OpenAI GPT-4o)

El Tutor IA es un estudiante virtual integrado en el sistema de mensajería. Funciona como un usuario real de la plataforma (`username: tutor_ia`, `email: ia@jumpup.com`).

**Configuración:** Requiere `OPENAI_API_KEY` en `.env`. Usa el cliente asíncrono de OpenAI.

**Flujo de activación desde Flutter:**

```
1. Crear un hilo de chat:
   POST /api/threads/
   { "subject": "Tutor IA", "participant_ids": [] }
   → { "id": 15 }

2. Conectar WebSocket:
   ws://servidor/ws/chat/15/?token=<jwt>

3. Enviar mensaje:
   { "type": "chat_message", "body": "How do I use present perfect?" }

4. Recibir indicador de escritura del bot:
   { "type": "typing", "username": "Tutor IA", "is_typing": true }

5. Recibir respuesta de GPT-4o guardada en BD:
   { "type": "chat_message", "message": { "sender": "ia@jumpup.com", "body": "..." } }
```

**Condición de activación:** el hilo tiene 1 solo participante, o el campo `subject` contiene `"IA"` (mayúsculas).

---

## E-Commerce y Venta Directa

El sistema abandonó Stripe como flujo principal y usa un modelo de venta directa propio:

### Modelos del flujo de compra

```
Catalogo  →  CarritoItem  →  Carrito  →  Orden  →  OrdenDetalle
(productos)                             (cabecera)  (líneas con precio)
```

### Flujo de compra

```
1. Admin carga productos en Catalogo (cursos o libros con precio)
2. Estudiante añade items al Carrito → POST /api/carrito/
3. Estudiante genera Orden → POST /api/ordenes-compra/
4. Admin aprueba la Orden (estado: pendiente → pagada)
5. Signal on_order_compra_approved se dispara automáticamente:
   ✅ Notificación WebSocket al profesor del aula vinculada
   ✅ Email al profesor: "Estudiante X compró el curso Y — envía el enlace del aula"
```

### Integración Stripe (modo paralelo/legacy)

Stripe está disponible para flujos de pago con tarjeta, aunque el modelo principal ahora es la venta directa. Las claves se configuran en `.env` pero no son obligatorias para el funcionamiento base.

**Tarjetas de prueba:**

| Número | Resultado |
|---|---|
| `4242 4242 4242 4242` | ✅ Pago exitoso |
| `4000 0000 0000 9995` | ❌ Tarjeta rechazada |
| `4000 0025 0000 3155` | 🔐 Requiere autenticación 3D Secure |

Fecha: cualquiera futura · CVV: cualquier 3 dígitos

---

## Sistema de Correos HTML

Todos los correos se envían con templates HTML profesionales que extienden `email_base.html`. Cada envío queda registrado en `EmailLog` con estado `pending → sent/failed`.

| Template | Evento disparador |
|---|---|
| `welcome_email.html` | Registro de usuario nuevo |
| `verification_email.html` | Verificación de cuenta |
| `password_reset_pin_email.html` | Solicitud de reset (envía PIN de 6 dígitos) |
| `password_reset_email.html` | Reset vía enlace |
| `certificate_email.html` | Emisión de certificado |
| `payment_confirmation_email.html` | Pago confirmado |
| `course_notification_email.html` | Nueva lección en un curso |
| `custom_email.html` | Correos personalizados con botón CTA |

El template base incluye: header degradado con logo JumpUp, footer con enlaces sociales, botones con gradiente, códigos PIN en display monospace, tablas de recibo y bloques informativos (success/warning/info). Totalmente responsive.

**Envíos masivos:** el modelo `BroadcastEmail` permite enviar a toda la plataforma, solo estudiantes, solo profesores, o al alumnado de un curso específico. Se ejecutan desde el panel de administración.

```python
# Desde el servicio:
from learning.services.email_service import send_broadcast_email
send_broadcast_email(broadcast_object)  # actualiza sent_count al terminar
```

---

## Endpoints de la API

### Autenticación

| Método | Endpoint | Auth | Descripción |
|---|---|:---:|---|
| POST | `/api/auth/register/` | ❌ | Registro con username, email, password |
| POST | `/api/auth/login/` | ❌ | Login + JWT. Soporta `remember_me` |
| POST | `/api/auth/token/refresh/` | ❌ | Refrescar access token |
| GET/PATCH | `/api/auth/me/` | ✅ | Ver/actualizar perfil propio |
| PATCH | `/api/auth/profile/update-languages/` | ✅ | Actualizar idiomas según rol |
| POST | `/api/auth/password-reset/` | ❌ | Solicitar PIN de 6 dígitos por email |
| POST | `/api/auth/password-reset-confirm/` | ❌ | Confirmar PIN y cambiar contraseña |
| POST | `/api/auth/biometric/register/` | ✅ | Registrar dispositivo biométrico |
| POST | `/api/auth/biometric/login/` | ❌ | Login con device_id + biometric_token |

### Dashboards

| Endpoint | Acceso | Contenido |
|---|---|---|
| `GET /api/dashboard/student/` | Todos | XP, nivel, racha, progreso %, logros, certificados, aulas |
| `GET /api/dashboard/teacher/` | Teacher/Admin | Aulas, estudiantes, recursos, sesiones |
| `GET /api/dashboard/admin/` | Admin | Métricas globales: usuarios, cursos, ingresos, reportes |

### Contenido Educativo

| Endpoint | Escritura | Filtros |
|---|---|---|
| `/api/languages/` | Admin | `?search=` `?ordering=` |
| `/api/courses/` | Teacher/Admin | `?language=` `?difficulty_level=` `?search=` |
| `/api/modules/` | Teacher/Admin | `?course=` `?search=` |
| `/api/lessons/` | Teacher/Admin | `?module=` `?content_type=` |
| `/api/exercises/` | Teacher/Admin | `?lesson=` `?exercise_type=` |

### Progreso y Gamificación

| Endpoint | Descripción |
|---|---|
| `POST /api/progress/` | Reportar lección completada → dispara XP + racha + logros |
| `GET /api/progress/summary/` | Resumen: XP, nivel, rachas, % completado, logros |
| `GET /api/progress/by-language/` | Progreso desglosado por idioma |
| `GET /api/stats/` | XP total, racha, nivel, `xp_progress_in_level` |
| `GET /api/ranking/` | Top 100 por XP (soporta `?language=`) |
| `GET /api/achievements/` | Catálogo de logros disponibles |
| `GET /api/my-achievements/` | Logros desbloqueados del usuario actual |

### E-Commerce (Venta Directa)

| Endpoint | Descripción |
|---|---|
| `/api/catalogo/` | Productos disponibles (cursos/libros con precio) |
| `/api/carrito/` | Carrito del estudiante |
| `/api/ordenes-compra/` | Crear y gestionar órdenes de compra |

### Aulas Virtuales

| Endpoint | Descripción |
|---|---|
| `CRUD /api/classrooms/` | Gestión de aulas |
| `POST /api/classrooms/join/` | Unirse con `access_code` |
| `GET /api/classrooms/mine/` | Mis aulas como estudiante |
| `POST /api/classrooms/{id}/remove-student/` | Expulsar estudiante (teacher/admin) |

### Certificados

| Endpoint | Descripción |
|---|---|
| `CRUD /api/certificates/` | Gestión de certificados |
| `PATCH /api/certificates/{id}/issue/` | Emitir certificado + envía email |
| `PATCH /api/certificates/{id}/revoke/` | Revocar certificado |
| `GET /api/certificates/verify/{code}/` | Verificación pública (sin autenticación) |

### Mensajería

| Endpoint | Descripción |
|---|---|
| `CRUD /api/threads/` | Hilos de chat |
| `GET/POST /api/threads/{id}/messages/` | Mensajes del hilo |
| `POST /api/messages/{id}/read/` | Marcar mensaje como leído |

### Foro Comunitario

| Endpoint | Descripción |
|---|---|
| `/api/forum-categories/` | Categorías (solo admin escribe) |
| `/api/forum-threads/` | Hilos + acciones `pin/`, `close/` |
| `/api/forum-posts/` | Publicaciones con anidación |
| `/api/forum-reactions/` | Reacciones (upsert: 1 por usuario+post) |
| `/api/forum-reports/` | Reportes de contenido |

### Feed Social

| Endpoint | Descripción |
|---|---|
| `/api/social-posts/` | Feed público + `mine/` |
| `/api/social-comments/` | Comentarios (`?post=id`) |
| `/api/social-reactions/` | Reacciones (upsert) |

### Videotutoría en Vivo

| Endpoint | Descripción |
|---|---|
| `CRUD /api/live-sessions/` | Teacher crea, todos pueden ver |
| `POST /api/live-sessions/{id}/join/` | Unirse (control de capacidad) |
| `POST /api/live-sessions/{id}/start/` | Iniciar (scheduled → live) |
| `POST /api/live-sessions/{id}/end/` | Finalizar (live → ended) |
| `GET /api/live-sessions/{id}/participants/` | Lista de participantes |

### Multimedia

| Endpoint | Descripción |
|---|---|
| `/api/media-files/` | Subir/administrar archivos (teacher/admin) |
| `/api/media-progress/` | Progreso de reproducción + `resume/{lesson_id}/` |

### Notificaciones

| Endpoint | Descripción |
|---|---|
| `/api/announcements/` | Anuncios globales |
| `/api/notifications/` | Notificaciones + `read/`, `read-all/`, `unread-count/` |
| `/api/preferences/` | Preferencias por canal |

### Sistema (solo admin)

| Endpoint | Descripción |
|---|---|
| `/api/users/` | CRUD teachers y administradores |
| `/api/admin-students/` | CRUD estudiantes |
| `/api/resources/` | Recursos de profesores |
| `/api/maintenance/` | Logs de mantenimiento |
| `/api/backups/` | Historial de backups |
| `/api/favorites/` | Favoritos por usuario |
| `/api/reports/` | Reportes del sistema |
| `/api/feedbacks/` | Feedback de usuarios |
| `/api/activity-logs/` | Logs de actividad |

### Búsqueda Global

```
GET /api/search/?q=ingles
GET /api/search/?q=ingles&type=cursos     # cursos, lecciones, recursos, foro, sesiones
GET /api/search/?q=ingles&limit=10        # límite de resultados (default 5, max 20)
```

### Documentación

| URL | Formato |
|---|---|
| `/api/docs/` | Swagger UI interactivo |
| `/api/redoc/` | Redoc |
| `/api/schema/` | OpenAPI schema JSON |

---

## Instalación y Desarrollo Local

### Prerrequisitos

- Python 3.11+
- PostgreSQL 14+ (o SQLite — se usa automáticamente si no se configura `DB_NAME`)
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Axel-25-dg/idiomas_api_guaman_danny.git
cd idiomas_api_guaman_danny

# 2. Crear entorno virtual
python -m venv .venv

# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus datos (mínimo SECRET_KEY y DB_*)

# 5. Crear la base de datos (PostgreSQL)
createdb languageapi_db
# O con psql: CREATE DATABASE languageapi_db;

# 6. Aplicar migraciones
python manage.py migrate

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Levantar el servidor de desarrollo
python manage.py runserver
```

### Accesos locales

| Recurso | URL |
|---|---|
| API REST | http://127.0.0.1:8000/api/ |
| Panel de Admin | http://127.0.0.1:8000/admin/ |
| Swagger UI | http://127.0.0.1:8000/api/docs/ |
| Redoc | http://127.0.0.1:8000/api/redoc/ |
| Landing | http://127.0.0.1:8000/ |

### Variables de entorno (`.env`)

```env
# General
SECRET_KEY=tu_secret_key_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (si se omite DB_NAME, usa SQLite automáticamente)
DB_NAME=languageapi_db
DB_USER=postgres
DB_PASSWORD=tu_contrasena
DB_HOST=localhost
DB_PORT=5432

# Email (en desarrollo se puede dejar el backend de consola)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu@gmail.com
EMAIL_HOST_PASSWORD=contraseña_de_app
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=JumpUp <no-reply@jumpup.com>
FRONTEND_URL=http://localhost:3000

# OpenAI — Tutor IA
OPENAI_API_KEY=sk-...

# Stripe — Pagos (opcional para modo básico)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Redis — WebSockets en producción (en DEBUG usa InMemory)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# CORS
CORS_ALLOW_ALL_ORIGINS=True
```

---

## Despliegue en Producción (VPS)

### Servidor

- **Proveedor:** Hetzner Cloud
- **Sistema Operativo:** Ubuntu 22.04 LTS
- **Dominio:** guaman-idiomas-ute.online
- **HTTPS:** Let's Encrypt (Certbot)

### Configuración de PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb languageapi_db
sudo -u postgres psql -c "CREATE USER api_user WITH PASSWORD 'contraseña';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE languageapi_db TO api_user;"
```

### Servicio Gunicorn (systemd)

Archivo: `/etc/systemd/system/gunicorn-shopapi.service`
```ini
[Unit]
Description=Gunicorn JumpUp API (HTTP)
After=network.target

[Service]
User=root
WorkingDirectory=/root/idiomas_api_guaman_danny
ExecStart=/root/idiomas_api_guaman_danny/.venv/bin/gunicorn \
    config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

### Servicio Daphne (systemd)

Archivo: `/etc/systemd/system/daphne-shopapi.service`
```ini
[Unit]
Description=Daphne JumpUp API (WebSocket / ASGI)
After=network.target

[Service]
User=root
WorkingDirectory=/root/idiomas_api_guaman_danny
ExecStart=/root/idiomas_api_guaman_danny/.venv/bin/daphne \
    -b 0.0.0.0 -p 8001 \
    config.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable gunicorn-shopapi daphne-shopapi
sudo systemctl start gunicorn-shopapi daphne-shopapi
```

### Nginx (HTTP + WebSocket)

```nginx
server {
    listen 443 ssl;
    server_name guaman-idiomas-ute.online;

    ssl_certificate     /etc/letsencrypt/live/guaman-idiomas-ute.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/guaman-idiomas-ute.online/privkey.pem;

    location /static/ {
        alias /root/idiomas_api_guaman_danny/staticfiles/;
    }

    location /media/ {
        alias /root/idiomas_api_guaman_danny/media/;
    }

    # WebSocket → Daphne
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }

    # HTTP → Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## CI/CD (GitHub Actions)

Archivo: `.github/workflows/deploy.yml`

Cada push a la rama `main` despliega automáticamente al servidor mediante SSH:

```
push a main
  ↓
1. git pull origin main          # Trae el código nuevo
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py collectstatic --noinput
5. systemctl restart gunicorn-shopapi
6. systemctl restart daphne-shopapi
7. Verifica que ambos servicios estén activos
```

**Secretos requeridos en GitHub → Settings → Secrets:**

| Secret | Descripción |
|---|---|
| `SERVER_IP` | IP pública del VPS |
| `SERVER_USER` | Usuario SSH (`root`) |
| `SSH_PRIVATE_KEY` | Clave privada RSA para autenticación |

Si Gunicorn o Daphne fallan al reiniciar, el workflow registra el error pero **no aborta** el pipeline, permitiendo revisión manual sin bloquear futuros deploys.

---

## Seguridad

| Medida | Configuración |
|---|---|
| HTTPS obligatorio en producción | `SECURE_SSL_REDIRECT=True` |
| HSTS activado | 1 año, subdomains, preload |
| Cookies seguras | `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` |
| Anti-clickjacking | `X_FRAME_OPTIONS = 'DENY'` |
| XSS filter | `SECURE_BROWSER_XSS_FILTER = True` |
| Content type sniffing | `SECURE_CONTENT_TYPE_NOSNIFF = True` |
| Referrer policy | `same-origin` |
| Login fallido | Registro en `LoginAttempt` por IP y email |
| IPs bloqueadas | Tabla `BlockedIp` con motivo y duración |
| Sesiones activas | Monitoreo en `ActiveSession` |
| Alertas de seguridad | `SecurityAlert` con niveles LOW/MEDIUM/HIGH/CRITICAL |

---

## Archivos Multimedia (MediaFile)

El modelo `MediaFile` aplica procesamiento automático al subir imágenes:

1. Calcula **checksum SHA-256** para evitar duplicados
2. Convierte la imagen a **WebP** (calidad 85%, máx 2048×2048 px)
3. Genera **thumbnail** 300×300 WebP (calidad 70%)
4. Registra dimensiones (width/height)

| Tipo | Tamaño máximo | Formatos aceptados |
|---|---|---|
| General | 20 MB | jpg, jpeg, png, webp, pdf |
| Avatar | 2 MB | jpeg, png, webp |

El almacenamiento es configurable vía `DEFAULT_FILE_STORAGE`: local, S3 o Cloudinary.

---

## Licencia

MIT — Danny Guamán © 2024–2025
