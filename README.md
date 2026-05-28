````markdown
<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/UTE_logo.svg/512px-UTE_logo.svg.png" width="180" alt="Universidad UTE"/>

# LanguageAPI

### Backend REST para Plataforma de Aprendizaje de Idiomas

Proyecto desarrollado con Django y Django REST Framework inspirado en plataformas de aprendizaje como Duolingo y Babbel.

<br>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-3.14+-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Authentication-black?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

</div>

---

# Tabla de Contenido

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Características Principales](#características-principales)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Modelo de Base de Datos](#modelo-de-base-de-datos)
- [Endpoints de la API](#endpoints-de-la-api)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Instalación y Configuración](#instalación-y-configuración)
- [Pruebas de la API](#pruebas-de-la-api)
- [Seguridad](#seguridad)
- [Testing](#testing)
- [Autor](#autor)

---

# Descripción del Proyecto

LanguageAPI es un backend REST desarrollado con Django y Django REST Framework para una plataforma de aprendizaje de idiomas.

El sistema permite gestionar:

- Usuarios y autenticación JWT
- Idiomas y cursos
- Módulos y lecciones
- Ejercicios interactivos
- Progreso del estudiante
- Estadísticas y gamificación
- Logros y recompensas
- Suscripciones y pagos

La arquitectura del proyecto está diseñada bajo una estructura modular y escalable, utilizando buenas prácticas de desarrollo backend y APIs RESTful.

---

# Características Principales

- Autenticación segura con JWT
- API REST completa
- Arquitectura modular
- Sistema de roles y permisos
- Gestión de progreso del estudiante
- Sistema de gamificación
- Manejo de suscripciones
- Integración con PostgreSQL
- Validaciones avanzadas con serializers
- Filtros y paginación personalizados

---

# Arquitectura del Proyecto

```bash
languageapi/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── learning/
│   ├── models/
│   │   ├── user.py
│   │   ├── language.py
│   │   ├── course.py
│   │   ├── progress.py
│   │   └── subscription.py
│   │
│   ├── serializers/
│   │   ├── user_serializer.py
│   │   ├── course_serializer.py
│   │   ├── progress_serializer.py
│   │   └── subscription_serializer.py
│   │
│   ├── views/
│   │   ├── auth_views.py
│   │   ├── course_views.py
│   │   ├── progress_views.py
│   │   └── subscription_views.py
│   │
│   ├── permissions.py
│   ├── pagination.py
│   ├── filters.py
│   ├── admin.py
│   ├── tests/
│   └── urls.py
│
├── requirements.txt
├── manage.py
├── .env.example
└── README.md
````

---

# Modelo de Base de Datos

## Módulo de Usuarios

| Modelo        | Descripción                   |
| ------------- | ----------------------------- |
| `Role`        | Roles del sistema             |
| `User`        | Usuario principal autenticado |
| `UserProfile` | Perfil extendido del usuario  |

---

## Módulo Educativo

| Modelo     | Descripción                  |
| ---------- | ---------------------------- |
| `Language` | Idiomas disponibles          |
| `Course`   | Cursos organizados por nivel |
| `Module`   | Unidades de aprendizaje      |
| `Lesson`   | Lecciones individuales       |
| `Exercise` | Ejercicios interactivos      |

---

## Módulo de Progreso

| Modelo            | Descripción                |
| ----------------- | -------------------------- |
| `UserProgress`    | Seguimiento del estudiante |
| `UserStats`       | Estadísticas y experiencia |
| `Achievement`     | Logros disponibles         |
| `UserAchievement` | Logros desbloqueados       |

---

## Módulo de Pagos

| Modelo             | Descripción           |
| ------------------ | --------------------- |
| `Subscription`     | Planes premium        |
| `UserSubscription` | Suscripciones activas |
| `Payment`          | Historial de pagos    |

---

# Endpoints de la API

## Autenticación

| Método | Endpoint                   | Descripción         |
| ------ | -------------------------- | ------------------- |
| `POST` | `/api/auth/register/`      | Registro de usuario |
| `POST` | `/api/auth/login/`         | Inicio de sesión    |
| `POST` | `/api/auth/token/refresh/` | Renovación de token |

---

## Cursos y Contenido

| Método       | Endpoint          |
| ------------ | ----------------- |
| `GET / POST` | `/api/languages/` |
| `GET / POST` | `/api/courses/`   |
| `GET / POST` | `/api/modules/`   |
| `GET / POST` | `/api/lessons/`   |
| `GET / POST` | `/api/exercises/` |

---

## Progreso

| Método       | Endpoint                |
| ------------ | ----------------------- |
| `GET / POST` | `/api/progress/`        |
| `GET`        | `/api/stats/`           |
| `GET`        | `/api/achievements/`    |
| `GET`        | `/api/my-achievements/` |

---

## Suscripciones

| Método       | Endpoint                 |
| ------------ | ------------------------ |
| `GET / POST` | `/api/subscriptions/`    |
| `GET / POST` | `/api/my-subscriptions/` |
| `GET / POST` | `/api/payments/`         |

---

# Tecnologías Utilizadas

| Tecnología            | Uso                 |
| --------------------- | ------------------- |
| Python 3.11+          | Lenguaje principal  |
| Django 4.2+           | Framework backend   |
| Django REST Framework | API REST            |
| PostgreSQL            | Base de datos       |
| JWT                   | Autenticación       |
| django-filter         | Filtros avanzados   |
| django-cors-headers   | Manejo de CORS      |
| psycopg2-binary       | Conexión PostgreSQL |

---

# Instalación y Configuración

## 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/languageapi.git
cd languageapi
```

---

## 2. Crear entorno virtual

### Windows

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Configurar variables de entorno

```bash
copy .env.example .env
```

Editar `.env`:

```env
SECRET_KEY=your_secret_key
DEBUG=True

DB_NAME=languageapi_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 5. Crear base de datos

```sql
CREATE DATABASE languageapi_db;
```

---

## 6. Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 7. Crear superusuario

```bash
python manage.py createsuperuser
```

---

## 8. Ejecutar servidor

```bash
python manage.py runserver
```

Servidor disponible en:

```bash
http://127.0.0.1:8000/
```

---

# Pruebas de la API

## Registrar usuario

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
-H "Content-Type: application/json" \
-d '{
  "username":"testuser",
  "email":"test@example.com",
  "password":"TestPass123!",
  "password2":"TestPass123!"
}'
```

---

## Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{
  "email":"test@example.com",
  "password":"TestPass123!"
}'
```

---

## Consumir endpoint protegido

```bash
curl http://127.0.0.1:8000/api/courses/ \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

# Seguridad

* Autenticación JWT
* Protección de endpoints privados
* Permisos personalizados
* Restricción de escritura para administradores
* Validaciones mediante serializers
* Variables sensibles protegidas con `.env`

---

# Testing

Ejecutar pruebas unitarias:

```bash
python manage.py test
```

---

# Autor

## Danny Alexander Guamán Pillajo

Estudiante de Desarrollo de Software
Universidad UTE — Cuarto Semestre

---

<div align="center">

Universidad UTE
Facultad de Ciencias de la Ingeniería e Industrias

</div>
```
