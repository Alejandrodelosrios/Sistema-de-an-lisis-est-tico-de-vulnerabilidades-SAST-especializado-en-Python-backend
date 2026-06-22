# 📋 Resumen del Proyecto Backend - SAST API

## 🎯 Descripción General
Sistema API REST construido con **FastAPI** para análisis estático de vulnerabilidades en código (SAST - Static Application Security Testing). La aplicación permite gestionar proyectos, usuarios, archivos de código y realizar análisis de vulnerabilidades.

**Versión:** 1.0.1

---

## 📦 Dependencias Principales
- **FastAPI** (0.136.1) - Framework web moderno
- **PostgreSQL** (psycopg2-binary 2.9.12) - Base de datos
- **Pydantic** (2.13.3) - Validación de datos
- **JWT (python-jose)** - Autenticación
- **Bcrypt** (5.0.0) - Encriptación de contraseñas
- **Pytest** (9.0.3) - Testing
- **SQLAlchemy** - ORM

---

## 🗂️ Estructura del Proyecto

```
backend/
├── main.py                    # Punto de entrada de la aplicación
├── prueba_carga.py            # Script de prueba de carga
├── pytest.ini                 # Configuración de pytest
├── requirements.txt           # Dependencias del proyecto
├── RESUMEN_PROYECTO.md        # Este archivo
│
├── app/                       # Aplicación principal
│   ├── __init__.py
│   ├── database.py            # Configuración de la base de datos
│   │
│   ├── core/                  # Configuración y seguridad
│   │   ├── config.py          # Variables de configuración
│   │   ├── dependencies.py    # Inyección de dependencias
│   │   └── security.py        # Funciones de seguridad/JWT
│   │
│   ├── models/                # Modelos de la base de datos (ORM)
│   │   ├── user.py            # Modelo de Usuario
│   │   ├── project.py         # Modelo de Proyecto
│   │   ├── file.py            # Modelo de Archivo
│   │   ├── analysis.py        # Modelo de Análisis
│   │   └── vulnerability.py   # Modelo de Vulnerabilidad
│   │
│   ├── routers/               # Rutas/Endpoints de la API
│   │   ├── auth.py            # Endpoints de autenticación
│   │   ├── project.py         # Endpoints de proyectos
│   │   ├── file.py            # Endpoints de archivos
│   │   ├── analysis.py        # Endpoints de análisis
│   │   └── vulnerability.py   # Endpoints de vulnerabilidades
│   │
│   ├── schemas/               # Esquemas Pydantic (DTOs)
│   │   ├── user.py            # Esquemas de Usuario
│   │   ├── project.py         # Esquemas de Proyecto
│   │   ├── file.py            # Esquemas de Archivo
│   │   └── analysis.py        # Esquemas de Análisis
│   │
│   └── services/              # Lógica de negocio
│       ├── auth_service.py    # Servicio de autenticación
│       ├── project_service.py # Servicio de proyectos
│       ├── file_service.py    # Servicio de archivos
│       ├── analysis_service.py# Servicio de análisis
│       ├── vulnerability_service.py # Servicio de vulnerabilidades
│       └── motor_ast.py       # Motor de análisis AST
│
├── storage/                   # Almacenamiento de archivos
│   └── projects/
│       └── usuario_1/
│           └── proyecto_2/
│               └── prueba_carga.py
│
└── tests/                     # Suite de pruebas
    ├── conftest.py            # Configuración de pytest
    ├── test_auth_service.py    # Pruebas de autenticación
    ├── test_auth_endpoints.py  # Pruebas de endpoints auth
    ├── test_project_service.py # Pruebas de proyectos
    ├── test_project_endpoints.py # Pruebas de endpoints proyectos
    ├── test_file_endpoints.py  # Pruebas de endpoints archivos
    ├── test_analysis_endpoints.py # Pruebas de endpoints análisis
    ├── tests_auth_endpoints.py # Pruebas adicionales auth
    └── TESTS_SUMMARY.md        # Resumen de pruebas
```

---

## 🔧 Módulos Clave

### **Core**
- **config.py** - Configuración centralizada (DATABASE_URL, SECRET_KEY, ALGORITHM, etc.)
- **security.py** - Manejo de tokens JWT y autenticación
- **dependencies.py** - Inyección de dependencias (usuario actual, BD, etc.)

### **Models** (ORM SQLAlchemy)
- **user.py** - Usuarios del sistema
- **project.py** - Proyectos de análisis
- **file.py** - Archivos de código a analizar
- **analysis.py** - Resultados de análisis
- **vulnerability.py** - Vulnerabilidades encontradas

### **Routers** (Endpoints REST)
- `/api/auth` - Login, registro, tokens
- `/api/projects` - CRUD de proyectos
- `/api/files` - Carga y gestión de archivos
- `/api/analysis` - Lanzar y consultar análisis
- `/api/vulnerabilities` - Consultar vulnerabilidades

### **Services** (Lógica de Negocio)
- **auth_service.py** - Autenticación, JWT
- **project_service.py** - Gestión de proyectos
- **file_service.py** - Gestión de archivos
- **analysis_service.py** - Coordinación de análisis
- **vulnerability_service.py** - Gestión de vulnerabilidades
- **motor_ast.py** - Motor de análisis estático (AST)

### **Schemas** (Validación Pydantic)
- DTOs para validar requests/responses
- Separación de datos internos vs públicos

---

## 🔐 Características de Seguridad

✅ **Autenticación JWT**
- Tokens de acceso y refresco
- Expiración configurable (30 min acceso, 7 días refresco)

✅ **Encriptación**
- Bcrypt para contraseñas
- RSA para firma de tokens

✅ **CORS**
- Configurado para dominios específicos:
  - Production: sistema-de-an-lisis-est-tico-de-vul.vercel.app
  - Development: localhost:3000, localhost:5173

---

## 🗄️ Base de Datos

- **Motor:** PostgreSQL
- **ORM:** SQLAlchemy
- **Automigración:** Tablas creadas automáticamente al iniciar

---

## 🧪 Testing

- **Framework:** Pytest + pytest-asyncio
- **Cobertura:** Tests para auth, projects, files, analysis
- **Ejecución:** `pytest` o `python -m pytest`

---

## 🚀 Punto de Entrada

**main.py**
- Inicializa la aplicación FastAPI
- Configura CORS
- Registra todos los routers
- Crea las tablas de la BD automáticamente
- Incluye middleware y lifespan events

---

## 📊 Flujo Principal

1. **Usuario se autentica** → auth.router → auth_service.py
2. **Crea proyecto** → project.router → project_service.py
3. **Carga archivo de código** → file.router → file_service.py → storage/
4. **Solicita análisis** → analysis.router → analysis_service.py → motor_ast.py
5. **Motor AST analiza** → Detecta vulnerabilidades
6. **Guarda resultados** → vulnerability.router → BD
7. **Consulta vulnerabilidades** → vulnerability.router → BD

---

## 📝 Notas Adicionales

- API documentada automáticamente en `/docs` (Swagger UI)
- Almacenamiento de archivos en `storage/projects/` organizados por usuario/proyecto
- Sistema modular y escalable
- Pruebas bien estructuradas
- Configuración centralizada con variables de entorno

---

**Última actualización:** 21 de junio de 2026
