# 🌍 LanguageAPI — Backend App de Idiomas

Backend completo estilo Duolingo construido con **Django + Django REST Framework**.
Basado en la estructura del proyecto `shopapi` del profesor.

---

## ⚙️ Tecnologías

| Tecnología | Versión |
|---|---|
| Python | 3.11+ |
| Django | 4.2+ |
| Django REST Framework | 3.14+ |
| Simple JWT | 5.3+ |
| PostgreSQL | 14+ |

---

## 🚀 Instalación desde cero (Windows PowerShell)

### 1. Clonar / entrar a la carpeta
```powershell
cd languageapi
```

### 2. Crear y activar entorno virtual
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 4. Crear archivo .env (copiar del ejemplo)
```powershell
copy .env.example .env
```
Luego edita `.env` con tus datos reales de PostgreSQL.

### 5. Crear la base de datos en PostgreSQL
```sql
CREATE DATABASE languageapi_db;
```

### 6. Aplicar migraciones
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear superusuario (administrador)
```powershell
python manage.py createsuperuser
```

### 8. Ejecutar el servidor
```powershell
python manage.py runserver
```

Abre: **http://127.0.0.1:8000/**

---

## 🔌 Endpoints de la API

### Autenticación (no requiere token)
| Método | URL | Descripción |
|---|---|---|
| POST | `/api/auth/register/` | Registrar nuevo usuario |
| POST | `/api/auth/login/` | Login → retorna JWT |
| POST | `/api/auth/token/refresh/` | Renovar token |

### Contenido Educativo (requiere token)
| Método | URL | Descripción |
|---|---|---|
| GET/POST | `/api/languages/` | Idiomas disponibles |
| GET/POST | `/api/courses/` | Cursos |
| GET/POST | `/api/modules/` | Unidades / Módulos |
| GET/POST | `/api/lessons/` | Lecciones |
| GET/POST | `/api/exercises/` | Ejercicios |

### Progreso y Gamificación (requiere token)
| Método | URL | Descripción |
|---|---|---|
| GET/POST | `/api/progress/` | Progreso del usuario |
| GET | `/api/stats/` | Estadísticas (XP, racha) |
| GET | `/api/achievements/` | Logros disponibles |
| GET | `/api/my-achievements/` | Tus logros desbloqueados |

### Pagos y Suscripciones (requiere token)
| Método | URL | Descripción |
|---|---|---|
| GET/POST | `/api/subscriptions/` | Planes disponibles |
| GET/POST | `/api/my-subscriptions/` | Tus suscripciones |
| GET/POST | `/api/payments/` | Historial de pagos |

---

## 🧪 Ejecutar tests
```powershell
python manage.py test
```

---

## 📁 Estructura del proyecto

```
languageapi/
├── config/                  ← Configuración Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── learning/                ← App principal
│   ├── models/              ← 15 modelos de BD
│   ├── serializers/         ← Serializers DRF
│   ├── views/               ← ViewSets y endpoints
│   ├── tests/               ← Tests unitarios
│   ├── migrations/
│   ├── urls.py              ← Rutas con DefaultRouter
│   ├── pagination.py
│   ├── permissions.py
│   └── filters.py
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 🔐 Autenticación con JWT

Incluye el token en el header de cada request:
```
Authorization: Bearer <tu_access_token>
```
