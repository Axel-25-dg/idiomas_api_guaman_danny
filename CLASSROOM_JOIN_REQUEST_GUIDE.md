# 📋 Guía: Solicitud de Ingreso a Aulas - Nueva Funcionalidad

## ¿Qué es Nuevo?

Implementamos un **flujo de aprobación para que estudiantes soliciten ingresar a aulas**. Antes, solo podían entrar usando un código de acceso directo. Ahora:

1. Estudiante solicita ingreso a un aula
2. Sistema notifica al profesor
3. Profesor ve la solicitud y puede aprobar o rechazar
4. Si aprueba, el estudiante es matriculado automáticamente

---

## 🔄 Flujo de Lógica

### Paso 1: Estudiante Solicita Ingreso

**Qué pasa:**
- Estudiante ve un aula disponible (puede ser del catálogo o ingresa código)
- En lugar de entrar directamente, hace clic en "Solicitar Ingreso"
- Se crea un registro `ClassroomJoinRequest` en la base de datos con estado `pending`
- Sistema envía:
  - **Notificación in-app** al profesor
  - **Correo electrónico** al profesor con detalles

**En la BD:**
```
ClassroomJoinRequest
├─ classroom: aula a la que quiere entrar
├─ student: quién solicita
├─ status: "pending"
├─ message: razón por la que quiere entrar (opcional)
└─ created_at: fecha de solicitud
```

### Paso 2: Profesor Revisa Solicitudes

**Qué pasa:**
- Profesor abre su panel de "Solicitudes de Ingreso"
- Ve lista de estudiantes que solicitan acceso
- Para cada solicitud ve:
  - Nombre y email del estudiante
  - Mensaje que escribió
  - Fecha de solicitud
  - Botones: "Aprobar" o "Rechazar"

**En la BD:**
- Solo profesor ve sus propias solicitudes (filtrado por classroom.teacher)
- Solicitudes con `status = "pending"`

### Paso 3: Profesor Aprueba

**Qué pasa:**
- Profesor hace clic en "Aprobar"
- Sistema **automáticamente**:
  1. Cambia estado de solicitud a `approved`
  2. Crea una matrícula en `ClassroomEnrollment` (ahora el estudiante está en la clase)
  3. Envía **correo al estudiante** confirmando que fue aprobado
  4. Envía **notificación in-app** al estudiante
- Estudiante ahora aparece en la lista de inscritos del aula

**En la BD:**
```
ClassroomJoinRequest.status = "approved"
ClassroomEnrollment (NUEVA FILA)
├─ classroom: la aula
├─ student: el estudiante
└─ enrolled_at: fecha de aprobación
```

### Paso 4: Rechazo (opcional)

**Qué pasa:**
- Si profesor rechaza, estado cambia a `rejected`
- Estudiante recibe notificación y correo (opcional)
- **No se crea matrícula**, estudiante no entra a la aula

---

## 📱 Cómo Implementar en Flutter

### 1. **Pantalla: Solicitar Ingreso a Aula**

Usuario ve una aula y presiona botón "Solicitar Ingreso":

```
┌─────────────────────────────┐
│ Aula: Inglés Avanzado       │
│ Profesor: prof@example.com  │
│ 15 estudiantes inscritos    │
├─────────────────────────────┤
│ Descripción:                │
│ Curso de inglés nivel B2    │
├─────────────────────────────┤
│ [Solicitar Ingreso] ← Presiona
│ [Usar Código]               │
└─────────────────────────────┘
```

**Datos a enviar al presionar:**
- ID del aula (`classroom_id`)
- Mensaje opcional (ej: "Me gustaría entrar porque necesito mejorar inglés")

**Llamada HTTP (internamente):**
```
POST /api/classrooms/request-join/
{
  "classroom_id": 5,
  "message": "Quiero aprender inglés nivel B2"
}
```

**Respuesta esperada:**
- Status 201 (Creado)
- Mensaje de éxito: "Solicitud enviada"

---

### 2. **Pantalla: Panel de Solicitudes (Profesor)**

Profesor abre su app y ve notificación "Tienes 3 nuevas solicitudes de ingreso".

Presiona y ve pantalla:

```
┌─────────────────────────────────────┐
│ Solicitudes de Ingreso a            │
│ Aula: Inglés Avanzado (5)           │
├─────────────────────────────────────┤
│ Solicitud 1                         │
│ └─ Juan García (juan@mail.com)      │
│    "Necesito práctica de listening" │
│    Enviada: hace 2 horas            │
│    [✓ Aprobar]  [✗ Rechazar]        │
├─────────────────────────────────────┤
│ Solicitud 2                         │
│ └─ María López (maria@mail.com)     │
│    "Me recomendaron tu curso"       │
│    Enviada: hace 1 hora             │
│    [✓ Aprobar]  [✗ Rechazar]        │
├─────────────────────────────────────┤
│ Solicitud 3                         │
│ └─ Carlos Ruiz (carlos@mail.com)    │
│    (Sin mensaje)                    │
│    Enviada: hace 30 min             │
│    [✓ Aprobar]  [✗ Rechazar]        │
└─────────────────────────────────────┘
```

**Datos que muestra:**
- Email del estudiante (solo lectura)
- Mensaje que escribió (si lo escribió)
- Fecha de solicitud
- Botones para aprobar/rechazar

**Llamadas HTTP (internamente):**
```
GET /api/classrooms/{aula_id}/requests/
→ Retorna lista de solicitudes pendientes
```

---

### 3. **Acción: Profesor Presiona "Aprobar"**

**Qué pasa internamente:**

```
POST /api/classrooms/{aula_id}/approve-request/
{
  "request_id": 123
}
```

**Sistema realiza:**
1. Cambia `ClassroomJoinRequest.status` a `"approved"`
2. Crea `ClassroomEnrollment` (estudiante está matriculado)
3. Envía correo al estudiante
4. Crea notificación in-app para estudiante

**Respuesta esperada:**
- Status 200
- Mensaje: "Solicitud aprobada"
- Solicitud desaparece de la lista

**Resultado visible:**
- Juan García ahora aparece en "Mis estudiantes" del profesor
- Juan García recibe correo: "Has sido aprobado para entrar a Inglés Avanzado"
- Juan García ve el aula en "Mis Aulas"

---

### 4. **Acción: Profesor Presiona "Rechazar"**

**Qué pasa internamente:**

```
POST /api/classrooms/{aula_id}/reject-request/
{
  "request_id": 123
}
```

**Sistema realiza:**
1. Cambia `ClassroomJoinRequest.status` a `"rejected"`
2. **NO crea matrícula**
3. (Opcional) Envía notificación al estudiante

**Resultado visible:**
- Solicitud desaparece de la lista del profesor
- Estudiante **no** entra a la aula
- Estudiante no la ve en "Mis Aulas"

---

## 📊 Estados de una Solicitud

| Estado | Significado | Quién lo ve |
|--------|-------------|-----------|
| `pending` | Esperando aprobación | Profesor (para aprobar/rechazar) |
| `approved` | Ya aprobada | Archivo, estudiante en la aula |
| `rejected` | Rechazada | Archivo |

---

## 🔔 Notificaciones Automáticas

### Al Solicitar (Estudiante envía solicitud)
- **Profesor recibe:** Notificación in-app + Correo
  - Asunto: "Nueva solicitud de ingreso a tu aula"
  - Cuerpo: "Juan García solicita entrar a Inglés Avanzado"

### Al Aprobar (Profesor aprueba)
- **Estudiante recibe:** Notificación in-app + Correo
  - Asunto: "¡Fuiste aprobado!"
  - Cuerpo: "Has sido aceptado en la aula Inglés Avanzado"

### Al Rechazar (Profesor rechaza)
- **Estudiante recibe:** Notificación in-app (sin correo por defecto)
  - Asunto: "Tu solicitud fue rechazada"

---

## 📱 Pantallas a Implementar en Flutter

### Pantalla 1: "Solicitar Ingreso a Aula"
**Lugar:** Cuando estudiante ve un aula y no está inscrito

**Elementos:**
- Campo de texto: "¿Por qué quieres entrar?" (opcional)
- Botón: "Enviar Solicitud"
- Botón alternativo: "Usar Código de Acceso"

**Flujo:**
1. Usuario escribe mensaje (o deja vacío)
2. Presiona "Enviar Solicitud"
3. Aparece spinner de carga
4. Si éxito → Mensaje: "Tu solicitud fue enviada"
5. Si error → Mostrar error

---

### Pantalla 2: "Mis Aulas" (Vista Profesor)
**Lugar:** En el menu del profesor, opción "Mis Aulas"

**Elementos:**
- Cada aula muestra:
  - Nombre del aula
  - Número de estudiantes
  - **Badge rojo:** "3 solicitudes pendientes" (si hay)

**Al tocar una aula:**
- Opción para ver "Solicitudes de Ingreso"

---

### Pantalla 3: "Solicitudes de Ingreso" (Vista Profesor)
**Lugar:** Al profesor tocar el badge de "3 solicitudes"

**Elementos:**
- Lista de solicitudes
- Cada solicitud muestra:
  - Email del estudiante
  - Mensaje enviado (si existe)
  - Fecha
  - Botones: "Aprobar" y "Rechazar"

**Acciones:**
- Tocar "Aprobar" → Spinner → Éxito/Error
- Tocar "Rechazar" → Confirmación → Spinner → Éxito/Error
- Pantalla actualiza automáticamente

---

## 💾 Datos Necesarios en Frontend

### Para Solicitar Ingreso:
```
- classroom_id: int (obligatorio)
- message: string (opcional, max 500 caracteres)
```

### Para Aprobar/Rechazar:
```
- classroom_id: int (obligatorio)
- request_id: int (obligatorio)
```

### Respuesta al listar solicitudes:
```
{
  "id": 123,
  "student_email": "juan@mail.com",
  "student_id": 45,
  "classroom_name": "Inglés Avanzado",
  "message": "Quiero mejorar mi nivel",
  "status": "pending",
  "created_at": "2026-07-13T10:30:00Z"
}
```

---

## 🔐 Permisos

- **Estudiante autenticado:** Puede enviar solicitud a cualquier aula
- **Profesor:** Solo ve y aprueba solicitudes de sus propias aulas
- **Admin:** Puede ver todo

**Validaciones en backend:**
- ✓ Estudiante no puede solicitar 2 veces la misma aula
- ✓ No puede solicitar si ya está inscrito
- ✓ Profesor no puede aprobar solicitud de otra aula
- ✓ Estudiante no puede aprobar ni rechazar

---

## ⚙️ Cómo Fluye Técnicamente en Flutter

### 1. Usuario toca "Solicitar Ingreso"
```
Flutter App → POST /api/classrooms/request-join/ → Django
                ↓
           Crea ClassroomJoinRequest
           Envía notificación + email
           ↓
           Retorna 201 ✓
           ↓
Flutter App muestra "Solicitud enviada"
```

### 2. Profesor toca botón de notificación
```
Flutter App → GET /api/classrooms/{id}/requests/ → Django
              ↓
         Retorna lista de solicitudes
         ↓
Flutter App muestra pantalla de solicitudes
```

### 3. Profesor toca "Aprobar"
```
Flutter App → POST /api/classrooms/{id}/approve-request/ → Django
              ↓
         Actualiza base de datos
         Crea matrícula
         Envía correo + notificación
         ↓
         Retorna 200 ✓
         ↓
Flutter App:
├─ Elimina solicitud de la lista
├─ Muestra "Aprobado"
└─ Actualiza contador de solicitantes
```

---

## 📌 Resumen

| Aspecto | Descripción |
|--------|------------|
| **Nuevo modelo** | `ClassroomJoinRequest` con campos: classroom, student, status, message |
| **Nuevos endpoints** | 4: request-join, requests, approve-request, reject-request |
| **Novedad principal** | Profesor controla quién entra a su aula |
| **Flujo** | Solicitar → Notificar → Aprobar → Matricular |
| **Pantallas Flutter** | Solicitud, Lista de solicitudes, Acciones (aprobar/rechazar) |
| **Notificaciones** | Automáticas en cada paso importante |
| **Permisos** | Solo profesor de su aula puede aprobar |

---

## 🎮 XP y Racha (Streak) - Gamificación

### ¿Qué es?

Cuando estudiante completa un ejercicio o juego, gana **puntos de experiencia (XP)**.

**XP:**
- Cada ejercicio resuelto = puntos XP
- Se acumulan en la cuenta del estudiante
- Determinan el nivel (nivel 1, 2, 3, etc.)

**Racha (Streak):**
- Contador de días consecutivos que el estudiante completa actividades
- Si hoy resuelve un ejercicio: +1 día racha
- Si mañana vuelve: +1 día racha (total 2)
- Si pasa un día sin hacer nada: la racha se reinicia a 0

### Cálculo de XP

Cuando estudiante resuelve un ejercicio:

```
XP ganado = puntos del ejercicio × multiplicador
```

**Ejemplo:**
- Ejercicio de listening: 50 puntos base
- Si lo resuelve correctamente: 50 XP
- Si lo resuelve incorrecto: 25 XP (50% del base)
- Si tiene racha de 7+ días: multiplicador 1.5x → 75 XP

### Niveles

Los niveles suben automáticamente según XP acumulado:

| Nivel | XP Necesario | Descripción |
|-------|-------------|------------|
| 1 | 0-99 | Principiante |
| 2 | 100-299 | Básico |
| 3 | 300-599 | Intermedio |
| 4 | 600-999 | Avanzado |
| 5 | 1000+ | Experto |

### Cómo Implementar en Flutter

**Pantalla: Ver mi XP y Racha**

```
┌──────────────────────────┐
│ Mi Progreso              │
├──────────────────────────┤
│                          │
│    Nivel: 3              │
│    🌟 Intermedio         │
│                          │
│    XP: 450 / 600         │
│    [█████░░░░░░░] 75%    │
│                          │
│    Racha: 🔥 12 días     │
│    Mejor racha: 28 días  │
│                          │
├──────────────────────────┤
│ XP Hoy:   +85            │
│ XP Semana: +420          │
│ XP Total: 2,150          │
└──────────────────────────┘
```

**Datos a mostrar:**
- Nivel actual
- XP actual vs XP para próximo nivel (barra de progreso)
- Racha actual (días)
- Mejor racha (histórico)
- XP ganado hoy, esta semana, total

**Llamada HTTP (internamente):**
```
GET /api/stats/mine/
```

**Respuesta:**
```
{
  "total_xp": 2150,
  "current_level": 3,
  "current_streak": 12,
  "longest_streak": 28,
  "ranking_position": 47,
  "next_level_xp": 600,
  "xp_for_next_level": 150,
  "achievements": [...]
}
```

### Pantalla: Ranking Global

```
┌─────────────────────────┐
│ Top 10 Estudiantes      │
├─────────────────────────┤
│ 🥇 #1 Juan García      │
│    3,200 XP | Lvl 5     │
├─────────────────────────┤
│ 🥈 #2 María López       │
│    2,900 XP | Lvl 5     │
├─────────────────────────┤
│ 🥉 #3 Carlos Ruiz       │
│    2,150 XP | Lvl 4     │
├─────────────────────────┤
│    #4 Ana Martínez      │
│    1,800 XP | Lvl 3     │
│    ...                  │
│                         │
│ Tú estás en #47         │
│ 450 XP | Nivel 3        │
└─────────────────────────┘
```

**Cómo lo ve estudiante:**
1. Abre app
2. Va a sección "Ranking"
3. Ve top 10 global
4. Ve su posición personal
5. Ve su XP y nivel

**Llamada HTTP:**
```
GET /api/ranking/?limit=10
```

---

## 📧 Envío Automático de Correos

### ¿Cuándo se envía?

El sistema envía correos automáticamente en estos momentos:

| Evento | A Quién | Asunto |
|--------|--------|--------|
| Estudiante solicita ingreso | Profesor | "Nueva solicitud de ingreso a tu aula" |
| Profesor aprueba solicitud | Estudiante | "¡Fuiste aprobado en {aula}!" |
| Profesor rechaza solicitud | Estudiante | "Tu solicitud fue rechazada" |
| Estudiante compra curso | Estudiante | "Compra confirmada - {curso}" |
| Admin envía anuncio | Todos | Según mensaje admin |

### Flujo del Correo

```
1. EVENTO ocurre (ej: profesor aprueba solicitud)
   ↓
2. Backend crea un registro en BD (EmailLog)
   ├─ Destinatario: email del usuario
   ├─ Asunto: "¡Fuiste aprobado!"
   ├─ Estado: "pending"
   └─ Fecha: ahora
   ↓
3. Backend envía correo via SMTP
   ├─ Usa servidor de correo configurado
   ├─ Aplica template HTML
   └─ Incluye datos del evento
   ↓
4. EmailLog actualiza estado
   ├─ Si éxito: "sent"
   ├─ Si error: "failed"
   └─ Fecha de envío
   ↓
5. Usuario recibe correo en su email
```

### Qué ve el usuario en correo

**Ejemplo: Correo de aprobación de aula**

```
De: noreply@jumpup.com
Asunto: ¡Fuiste aprobado en Inglés Avanzado!

Hola Juan García,

Excelentes noticias! Tu solicitud para entrar al aula "Inglés Avanzado"
ha sido aprobada por el profesor.

Ya puedes acceder a todos los recursos y ejercicios del curso.

Aula: Inglés Avanzado
Profesor: prof@example.com
Fecha de aprobación: 13 de julio de 2026

[Acceder al Aula] ← Link clickeable

¿Preguntas? Contáctanos a soporte@jumpup.com

---
JumpUp Idiomas
```

### En Flutter: Nada que hacer

**No necesitas implementar nada en Flutter para correos.**

El backend maneja todo automáticamente. El estudiante solo ve:
- Notificación in-app (si está en la app)
- Correo en su bandeja de entrada

Si quieres mostrar un "Correo enviado" en la app:
```
Cuando estudiante presiona "Solicitar Ingreso":
- App muestra: "✓ Solicitud enviada"
- Backend envia correo al profesor (usuario no ve esto)
```

---

## 🎥 Sesiones en Vivo (Llamadas de Video)

### ¿Qué es?

Profesor puede organizar una **clase en vivo** (como zoom o WhatsApp call pero integrado).

**Funciona así:**
- Profesor crea sesión en vivo a cierta hora
- Sistema genera un `room_id` único (código de sala)
- Estudiantes ven que hay clase en vivo
- Al conectarse, entran a video llamada con el profesor
- Pueden ver, escuchar y hablar

### Cómo Funciona la Conexión

```
1. Profesor crea sesión
   ├─ Nombre: "Clase de Pronunciación"
   ├─ Hora: 14:00 (hoy)
   ├─ room_id: "sala_12345abc" ← Auto-generado
   └─ Aula: Inglés Avanzado

2. Sistema notifica a estudiantes
   "Tu profesor inició clase en vivo"

3. Estudiante presiona "Unirse"
   ├─ App conecta a room_id: "sala_12345abc"
   ├─ Video se abre (pantalla de video)
   ├─ Micrófono se activa
   └─ Puede escuchar/hablar

4. Sesión termina
   ├─ Profesor cierra
   ├─ room_id se invalida
   └─ Nadie puede entrar
```

### Pantalla: Ver Sesiones en Vivo Disponibles

```
┌────────────────────────────┐
│ Clases en Vivo             │
├────────────────────────────┤
│ 🔴 EN VIVO AHORA           │
│                            │
│ Pronunciación Inglés       │
│ Profesor: Prof. García     │
│ 23 estudiantes conectados  │
│ [UNIRSE A VIDEOLLAMADA]    │
├────────────────────────────┤
│ ⏰ PRÓXIMAS (HOY)           │
│                            │
│ Listening Avanzado         │
│ 14:30                      │
│ [RECORDARME]               │
├────────────────────────────┤
│ Gramática B2               │
│ Mañana 10:00               │
│ [RECORDARME]               │
└────────────────────────────┘
```

### Cómo Implementar en Flutter

**Datos a obtener:**
```
GET /api/live-sessions/?classroom=5
```

**Respuesta:**
```
{
  "id": 1,
  "title": "Pronunciación Inglés",
  "room_id": "sala_12345abc",
  "status": "active",
  "classroom_name": "Inglés Avanzado",
  "participants_count": 23,
  "scheduled_at": "2026-07-13T14:00:00Z",
  "duration_minutes": 60
}
```

**Flujo en Flutter:**

1. **Mostrar lista de sesiones en vivo**
   - Obtener sesiones con estado "active"
   - Mostrar nombre, profesor, # participantes

2. **Estudiante presiona "Unirse"**
   - App obtiene `room_id` de la sesión
   - Abre plugin de video (Jitsi Meet, Agora, etc.)
   - Se conecta a la sala

3. **En la videollamada**
   - Profesor y estudiantes conectados
   - Pueden verse y escucharse
   - Profesor puede compartir pantalla (opcional)

4. **Salir de videollamada**
   - Presiona "Salir"
   - Vuelve a la app
   - Sistema registra que participó

---

## 📁 Recursos: Imágenes, Audios, Videos

### ¿Qué es?

Profesor sube materiales educativos (imágenes, PDF, audios, videos, links) a un aula.

Estudiantes pueden:
- Ver imágenes
- Escuchar audios
- Ver/descargar videos
- Abrir links externos

### Tipos de Recursos

| Tipo | Extensión | Qué Hace |
|------|-----------|---------|
| **Imagen** | .jpg, .png, .gif | Se muestra en pantalla |
| **Audio** | .mp3, .wav, .m4a | Abre reproductor de audio |
| **Video** | .mp4, .webm | Abre reproductor de video |
| **PDF** | .pdf | Se descarga y abre |
| **Link** | https://... | Se abre en navegador |

### Cómo se Guardan

Profesor sube archivo (o pega URL):

```
Profesor (en web o app):
└─ "Subir recurso"
   ├─ Selecciona archivo: "listening_exercise.mp3"
   ├─ Tipo: Audio
   ├─ Descripción: "Ejercicio de escucha Level B1"
   └─ [Subir]

Sistema (Backend):
├─ Guarda archivo en servidor: /media/teacher_resources/listening_exercise.mp3
├─ Crea registro en BD:
│  ├─ file: listening_exercise.mp3
│  ├─ content_type: "audio"
│  ├─ teacher: prof@example.com
│  └─ course: Inglés B1
└─ Retorna URL descargable
```

### Pantalla: Ver Recursos del Curso

```
┌────────────────────────────┐
│ Recursos - Inglés B1       │
├────────────────────────────┤
│ 📄 Unit 1 Vocabulary       │
│    PDF - Profesor García   │
│    [Descargar]             │
├────────────────────────────┤
│ 🎵 Listening Exercise 1    │
│    Audio - 3 min           │
│    [▶ Escuchar]            │
├────────────────────────────┤
│ 🎬 Grammar Explanation     │
│    Video - 15 min          │
│    [▶ Ver Video]           │
├────────────────────────────┤
│ 🖼️  Vocabulary Images      │
│    Imagen - 2 MB           │
│    [Ver Imagen]            │
├────────────────────────────┤
│ 🌐 External Resource       │
│    Link: bbc-learning.com  │
│    [Abrir en Navegador]    │
└────────────────────────────┘
```

### Cómo Implementar en Flutter

**1. Obtener lista de recursos:**
```
GET /api/resources/?course=5
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "title": "Listening Exercise 1",
    "content_type": "audio",
    "file": "/media/teacher_resources/audio_001.mp3",
    "external_url": null,
    "teacher_email": "prof@example.com",
    "created_at": "2026-07-13T10:00:00Z"
  },
  {
    "id": 2,
    "title": "Grammar Video",
    "content_type": "video",
    "file": null,
    "external_url": "https://youtube.com/watch?v=xyz",
    "teacher_email": "prof@example.com",
    "created_at": "2026-07-13T09:00:00Z"
  },
  {
    "id": 3,
    "title": "Vocabulary Images",
    "content_type": "image",
    "image": "/media/teacher_resources/images/vocab.png",
    "file": null,
    "external_url": null,
    "teacher_email": "prof@example.com",
    "created_at": "2026-07-13T08:00:00Z"
  }
]
```

**2. Según tipo, actuar diferente:**

- **Audio:** Mostrar reproductor (play, pausa, progreso)
- **Video:** Mostrar video player (play, fullscreen)
- **Imagen:** Mostrar imagen, opción de fullscreen
- **Link:** Abrir en navegador
- **PDF:** Descargar y abrir con app de PDF

**3. Acciones del usuario:**

```
Usuario toca recurso:
├─ Si es Audio:
│  └─ Abre reproductor
│     ├─ Muestra duración
│     ├─ Control play/pausa
│     └─ Barra de progreso
├─ Si es Video:
│  └─ Abre video player
│     ├─ Pantalla completa disponible
│     ├─ Controles de reproducción
│     └─ Calidad ajustable
├─ Si es Imagen:
│  └─ Muestra imagen
│     ├─ Opción de fullscreen
│     └─ Botón de compartir
├─ Si es PDF:
│  └─ Descarga y abre
│     └─ Usar app nativa de PDF
└─ Si es Link:
   └─ Abre navegador web
      └─ Navega a URL
```

### Ejemplo: Reproducir Audio

Estudiante en la app presiona recurso "Listening Exercise 1":

```
1. App obtiene URL: /media/teacher_resources/audio_001.mp3
2. Abre reproductor de audio
3. Muestra:
   - Nombre: "Listening Exercise 1"
   - Profesor: "García"
   - Duración: 3:45
   - [◀◀]  [◀]  [▶]  [▶▶]  [❚❚]
   - Barra de progreso: [████░░░░░] 1:30 / 3:45
   - Volumen control
4. Usuario presiona play
5. Se escucha el audio
6. Puede pausar, avanzar, retroceder
7. Al terminar, vuelve al inicio
```

### Ejemplo: Ver Imagen

Estudiante presiona "Vocabulary Images":

```
1. App obtiene URL: /media/teacher_resources/images/vocab.png
2. Muestra imagen en la pantalla
3. Opciones:
   - [🔍] Zoom
   - [↔] Fullscreen
   - [↓] Descargar
   - [📤] Compartir
4. Estudiante puede hacer zoom con dos dedos
5. Tocar X para cerrar
```

### Información del Recurso

Cada recurso tiene:
- **id:** Identificador único
- **title:** Nombre del recurso
- **description:** Descripción (opcional)
- **content_type:** Tipo (audio, video, image, url, file)
- **file:** URL del archivo si está en servidor
- **image:** URL de imagen si es imagen
- **external_url:** URL externa si es link
- **teacher_email:** Quién lo subió
- **course_title:** De qué curso es
- **created_at:** Fecha de creación
- **is_public:** Si todos pueden verlo o solo inscritos

---

---

## 📚 Lecciones (Lessons/Unidades)

### ¿Qué es?

Una **lección** es una subdivisión de un curso. Agrupa contenido sobre un tema específico.

**Ejemplo:**
```
Curso: Inglés B1
└─ Lección 1: Present Simple
   ├─ Recursos: Explicación, videos, audios
   ├─ Ejercicios: 5 preguntas
   └─ Duración: ~20 minutos
   
└─ Lección 2: Past Tense
   ├─ Recursos: Explicación, ejemplos
   ├─ Ejercicios: 7 preguntas
   └─ Duración: ~25 minutos
```

### Estructura

Cada lección tiene:
- **id:** Identificador único
- **title:** Nombre ("Present Simple")
- **description:** Descripción del contenido
- **course:** A qué curso pertenece
- **order:** Número de orden (1, 2, 3...)
- **resources:** Lista de materiales (audios, videos, PDFs, etc.)
- **exercises:** Lista de ejercicios para practicar
- **is_published:** Si está visible para estudiantes

### Pantalla: Ver Lecciones de un Curso

```
┌──────────────────────────────┐
│ Curso: Inglés B1             │
│ Profesor: García             │
├──────────────────────────────┤
│ Lección 1: Present Simple   │
│ 👁 Visto                     │
│ 3 recursos                   │
│ 5 ejercicios                 │
│ Duración: ~20 min            │
│ [Abrir Lección]              │
├──────────────────────────────┤
│ Lección 2: Past Tense        │
│ 🔒 Bloqueado                 │
│ (Completa Lección 1 primero) │
├──────────────────────────────┤
│ Lección 3: Future            │
│ 🔒 Próxima                   │
│ (Disponible después)         │
└──────────────────────────────┘
```

### Cómo Fluye

**1. Abrir una lección:**
```
GET /api/lessons/{lesson_id}/
```

**Respuesta:**
```json
{
  "id": 5,
  "title": "Present Simple",
  "description": "Aprende a usar Present Simple...",
  "course": 1,
  "order": 1,
  "resources": [
    {"id": 1, "title": "Video explicativo", "content_type": "video"},
    {"id": 2, "title": "Ejercicio de listening", "content_type": "audio"}
  ],
  "exercises": [
    {"id": 101, "title": "Completa las oraciones", "type": "multiple_choice"},
    {"id": 102, "title": "Traduce al inglés", "type": "text_input"}
  ],
  "is_published": true,
  "duration_minutes": 20,
  "is_locked": false,
  "progress": 60
}
```

**2. Mostrar lección en Flutter:**
- Mostrar título y descripción
- Listar recursos (el estudiante puede verlos)
- Listar ejercicios (con botones para hacer cada uno)
- Mostrar barra de progreso

**3. Progreso de lección:**
- Al completar todos los ejercicios → Lección marcada como completa
- Siguiente lección se desbloquea
- Se ganan XP por completar la lección

---

## ✏️ Ejercicios (Exercises)

### ¿Qué es?

Un **ejercicio** es una pregunta o tarea para practicar el idioma.

**Tipos:**
- Multiple choice (selecciona opción correcta)
- Verdadero/Falso
- Escribir respuesta (texto)
- Escuchar y repetir
- Matching (unir con líneas)
- Llenar espacios en blanco

### Estructura de un Ejercicio

```
Ejercicio: "Escoge el verbo correcto"

Pregunta: "She _____ coffee every morning"
A) drink
B) drinks       ← Respuesta correcta
C) drinking
D) drank

Puntos: 10 XP
Dificultad: Easy
Lección: Present Simple
```

### Pantalla: Hacer Ejercicio

```
┌────────────────────────────────┐
│ Ejercicio 1 de 5               │
│ Progreso: [██░░░░░░░░] 20%     │
├────────────────────────────────┤
│                                │
│ She _____ coffee every morning │
│                                │
│ ⚪ drink                       │
│ ⚫ drinks                      │
│ ⚪ drinking                    │
│ ⚪ drank                       │
│                                │
│ [Enviar Respuesta]             │
└────────────────────────────────┘
```

### Cómo Funciona

**1. Obtener ejercicio:**
```
GET /api/exercises/{exercise_id}/
```

**Respuesta:**
```json
{
  "id": 101,
  "title": "Escoge el verbo correcto",
  "question": "She _____ coffee every morning",
  "exercise_type": "multiple_choice",
  "options": [
    {"id": 1, "text": "drink", "is_correct": false},
    {"id": 2, "text": "drinks", "is_correct": true},
    {"id": 3, "text": "drinking", "is_correct": false},
    {"id": 4, "text": "drank", "is_correct": false}
  ],
  "points": 10,
  "difficulty": "easy",
  "explanation": "Con 'she' usamos tercera persona singular..."
}
```

**2. Enviar respuesta:**
```
POST /api/exercises/{exercise_id}/submit/
{
  "selected_option_id": 2
}
```

**Respuesta:**
```json
{
  "is_correct": true,
  "xp_gained": 10,
  "explanation": "¡Correcto! Con 'she' (tercera persona singular) usamos 'drinks'",
  "streak_updated": true,
  "current_streak": 5,
  "next_exercise_id": 102
}
```

**3. Mostrar resultado:**
```
Si es correcto:
┌────────────────────────┐
│ ✅ ¡Correcto!          │
│                        │
│ +10 XP                 │
│ Racha: 🔥 5 días       │
│                        │
│ Explicación:           │
│ Con 'she' usamos...    │
│                        │
│ [Siguiente Ejercicio]  │
└────────────────────────┘

Si es incorrecto:
┌────────────────────────┐
│ ❌ Incorrecto          │
│                        │
│ La respuesta correcta: │
│ drinks                 │
│                        │
│ Explicación:           │
│ Con 'she' usamos...    │
│                        │
│ [Reintentar]           │
│ [Ver Recurso]          │
└────────────────────────┘
```

### Importante: Ocultar Respuestas

**Para estudiantes:** NO se ve la respuesta correcta en el HTML/respuesta
- Solo ve si está correcto o incorrecto
- Ve la explicación

**Para admin/profesor:** Puede ver respuesta correcta (para validar)

Esto evita que se copien respuestas viendo el código.

---

## 🏅 Certificados

### ¿Qué es?

Un **certificado** es un documento que demuestra que el estudiante completó un curso.

```
┌────────────────────────────────────┐
│                                    │
│     CERTIFICADO DE FINALIZACIÓN    │
│                                    │
│  Felicitamos a Juan García         │
│                                    │
│  Por completar exitosamente:       │
│  "Inglés Avanzado B2"              │
│                                    │
│  Fecha: 13 de Julio de 2026        │
│  Profesor: Prof. María García      │
│  Calificación: 92%                 │
│                                    │
│  Código: CERT-2026-001234          │
│                                    │
└────────────────────────────────────┘
```

### Cómo se Obtiene

Estudiante debe:
1. Completar todas las lecciones del curso
2. Hacer todos los ejercicios
3. Obtener puntuación mínima (ej: 70%)
4. (Opcional) Pasar examen final

Sistema automáticamente:
1. Valida que completó todo
2. Genera certificado PDF
3. Envía correo al estudiante con descarga
4. Almacena en perfil del estudiante

### Pantalla: Mis Certificados

```
┌──────────────────────────────┐
│ Mis Certificados             │
├──────────────────────────────┤
│ ✅ Inglés Avanzado B2       │
│    Completado: 13/07/2026   │
│    Calificación: 92%        │
│    [Ver PDF] [Compartir]    │
├──────────────────────────────┤
│ ✅ Business English         │
│    Completado: 10/07/2026   │
│    Calificación: 87%        │
│    [Ver PDF] [Compartir]    │
├──────────────────────────────┤
│ ⏳ Inglés Básico            │
│    En progreso: 45%         │
│    Faltan 2 lecciones       │
└──────────────────────────────┘
```

### En Flutter

**1. Obtener certificados:**
```
GET /api/certificates/mine/
```

**2. Descargar PDF:**
```
GET /api/certificates/{id}/download/
```

**3. Compartir:**
- Botón de compartir → Comparte link o PDF
- Ejemplo: "He completado Inglés B2: [link]"

---

## 🔔 Notificaciones In-App

### ¿Qué es?

Mensajes que el usuario ve **dentro de la app** (no son correos).

**Ejemplos:**
- "Nueva solicitud de ingreso en Inglés Avanzado"
- "¡Fuiste aprobado!"
- "Tu clase en vivo empieza en 5 minutos"
- "Completaste una lección - +50 XP"
- "Tienes un nuevo mensaje privado"

### Pantalla: Centro de Notificaciones

```
┌──────────────────────────────┐
│ 📬 Notificaciones (7)        │
├──────────────────────────────┤
│ 🔴 Hace 2 min                │
│ ✅ ¡Fuiste aprobado!        │
│ Has sido aceptado en         │
│ "Inglés Avanzado"            │
│ [Marcar como leído]          │
├──────────────────────────────┤
│ ⚪ Hace 30 min               │
│ 👥 Nuevo estudiante          │
│ María López solicita entrar  │
│ a tu aula                    │
│ [Ver Solicitud]              │
├──────────────────────────────┤
│ ⚪ Hace 1 hora               │
│ 🎥 Tu clase en vivo           │
│ Pronunciación Inglés comienza│
│ en 5 minutos                 │
│ [Unirse Ahora]               │
└──────────────────────────────┘
```

### Tipos de Notificaciones

| Tipo | Cuándo | Acción |
|------|--------|--------|
| Solicitud | Estudiante pide ingreso | Ver solicitud |
| Aprobación | Profesor aprueba | Ir a aula |
| Clase en vivo | Sesión próxima | Unirse a video |
| Ejercicio | Completó ejercicio | Ver progreso |
| Compra | Compró curso | Acceder a curso |
| Mensaje | Recibió mensaje | Ver chat |

### Cómo Funciona

**1. Obtener notificaciones:**
```
GET /api/notifications/
```

**Respuesta:**
```json
[
  {
    "id": "notif-123",
    "type": "classroom_approved",
    "title": "¡Fuiste aprobado!",
    "message": "Has sido aceptado en Inglés Avanzado",
    "is_read": false,
    "action_url": "/classrooms/5/",
    "created_at": "2026-07-13T14:30:00Z"
  }
]
```

**2. Marcar como leído:**
```
PATCH /api/notifications/{id}/
{
  "is_read": true
}
```

**3. En Flutter:**
- Mostrar badge rojo con # de no leídos
- Al tocar una notificación → Navega a la acción correspondiente

---

## 📊 Dashboard

### Estudiante - Dashboard

```
┌────────────────────────────────┐
│ 👤 Mi Dashboard                │
├────────────────────────────────┤
│ PROGRESO                       │
│ Nivel: 3 🌟 Intermedio        │
│ XP: 450 / 600 [██░░░░░]       │
│ Racha: 🔥 12 días             │
│ Posición: #47                  │
│                                │
│ MIS AULAS (3)                  │
│ ✅ Inglés Avanzado (100%)      │
│ ✅ Business English (65%)      │
│ 📚 Francés Básico (0%)         │
│ [Ver Todas]                    │
│                                │
│ PRÓXIMAS CLASES EN VIVO        │
│ 🎥 Pronunciación (14:30 hoy)   │
│ [Recordar]                     │
│                                │
│ RECOMENDACIONES                │
│ 📝 Completa Unit 5 de Inglés   │
│ 🎮 Juega para racha de 15 días │
└────────────────────────────────┘
```

**Llamada HTTP:**
```
GET /api/dashboard/student/
```

**Respuesta:**
```json
{
  "user": {...},
  "stats": {
    "current_level": 3,
    "current_xp": 450,
    "next_level_xp": 600,
    "current_streak": 12,
    "ranking_position": 47
  },
  "classrooms": [...],
  "live_sessions_upcoming": [...],
  "recommendations": [...]
}
```

### Profesor - Dashboard

```
┌────────────────────────────────┐
│ 👨‍🏫 Panel del Profesor           │
├────────────────────────────────┤
│ MIS AULAS (5)                  │
│ 📚 Inglés Avanzado             │
│    👥 32 estudiantes           │
│    🔴 3 solicitudes nuevas     │
│    [Ver Aula]                  │
│                                │
│ 📚 Business English            │
│    👥 18 estudiantes           │
│    ✅ Sin solicitudes          │
│    [Ver Aula]                  │
│                                │
│ ESTADÍSTICAS                   │
│ Total estudiantes: 87          │
│ Promedio progreso: 68%         │
│ Clases en vivo: 5 (semana)     │
│                                │
│ ACTIVIDADES RECIENTES          │
│ • María López completó Unit 3  │
│ • Juan García solicitó acceso  │
│ • 12 ejercicios enviados hoy   │
└────────────────────────────────┘
```

**Llamada HTTP:**
```
GET /api/dashboard/teacher/
```

---

## 🛒 E-Commerce: Carrito y Compras

### ¿Qué es?

Estudiantes pueden **comprar cursos** para acceder a ellos.

**Flujo:**
```
1. Ver catálogo de cursos
2. Seleccionar un curso
3. Agregar al carrito
4. Pagar
5. Acceso inmediato al curso
```

### Pantalla: Catálogo de Cursos

```
┌──────────────────────────────┐
│ 📚 Cursos Disponibles        │
├──────────────────────────────┤
│ Inglés Avanzado B2           │
│ ⭐⭐⭐⭐⭐ (142 reseñas)      │
│ $29.99                       │
│ 12 lecciones | 150 ejercicios│
│ Profesor: García             │
│ [Agregar al Carrito]         │
├──────────────────────────────┤
│ Business English             │
│ ⭐⭐⭐⭐ (87 reseñas)        │
│ $39.99                       │
│ 15 lecciones | 200 ejercicios│
│ Profesor: López              │
│ [Agregar al Carrito]         │
├──────────────────────────────┤
│ 🛒 Carrito (2 cursos)        │
│ Total: $69.98                │
│ [Ver Carrito]                │
└──────────────────────────────┘
```

### Pantalla: Carrito

```
┌──────────────────────────────┐
│ 🛒 Mi Carrito (2 cursos)     │
├──────────────────────────────┤
│ ✅ Inglés Avanzado B2        │
│    $29.99                    │
│    [Quitar]                  │
├──────────────────────────────┤
│ ✅ Business English          │
│    $39.99                    │
│    [Quitar]                  │
├──────────────────────────────┤
│ Subtotal:  $69.98            │
│ Impuesto:  $5.60             │
│ ────────────────────         │
│ TOTAL:     $75.58            │
│                              │
│ [Proceder al Pago]           │
└──────────────────────────────┘
```

### Flujo de Compra

**1. Agregar al carrito:**
```
POST /api/carrito/agregar/
{
  "course_id": 5,
  "quantity": 1
}
```

**2. Ver carrito:**
```
GET /api/carrito/
```

**3. Realizar compra:**
```
POST /api/carrito/comprar/
{
  "payment_method": "credit_card",
  "card_token": "tok_visa_123"
}
```

**Respuesta:**
```json
{
  "order_id": "ORDER-2026-001",
  "status": "completed",
  "total": 75.58,
  "courses_purchased": [
    {"id": 5, "title": "Inglés Avanzado B2"},
    {"id": 8, "title": "Business English"}
  ],
  "access_granted": true
}
```

**4. Confirmación:**
```
✅ Compra realizada
Orden: ORDER-2026-001
Email confirmación enviado
Ya puedes acceder a tus cursos
```

### Pantalla: Mis Compras

```
┌──────────────────────────────┐
│ 📦 Mis Compras               │
├──────────────────────────────┤
│ Compra: ORDER-2026-001       │
│ Fecha: 13/07/2026           │
│ Total: $75.58                │
│ Estado: ✅ Completada       │
│                              │
│ Cursos:                      │
│ • Inglés Avanzado B2         │
│ • Business English           │
│                              │
│ [Ver Factura] [Descargar]    │
├──────────────────────────────┤
│ Compra: ORDER-2026-002       │
│ Fecha: 10/07/2026           │
│ Total: $29.99                │
│ Estado: ✅ Completada       │
│ Cursos: Francés Básico       │
└──────────────────────────────┘
```

---

## 📊 Resumen de Todas las Funcionalidades

| Funcionalidad | Qué Es | Dónde se Usa |
|---------------|--------|------------|
| **Solicitud Ingreso** | Estudiante solicita entrar a aula | Control de acceso |
| **XP & Racha** | Puntos + días consecutivos | Motivación, gamificación |
| **Niveles** | Automáticos según XP | Perfil, ranking |
| **Ranking** | Top 10 global | Competencia sana |
| **Correos** | Automáticos en eventos | Notificaciones por email |
| **Lecciones** | Subdivisiones de cursos | Estructura de contenido |
| **Ejercicios** | Preguntas para practicar | Evaluación, XP |
| **Certificados** | Comprobante de finalización | Credencial del estudiante |
| **Sesiones en Vivo** | Videollamadas integradas | Clases sincrónicas |
| **Recursos** | Archivos multimedia | Materiales de estudio |
| **Imágenes** | Visuales en recursos | Vocabulario, guías |
| **Audios** | Listening exercises | Pronunciación, comprensión |
| **Videos** | Explicaciones visuales | Gramática, pronunciación |
| **Notificaciones** | Mensajes in-app | Alertas a usuario |
| **Dashboard** | Panel de usuario | Vista general de progreso |
| **E-Commerce** | Compra de cursos | Monetización |

**Implementación completada y testeada ✅**
