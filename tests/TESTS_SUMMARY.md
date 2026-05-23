# 📋 Resumen de la Carpeta Tests

## 📝 Descripción General
La carpeta `tests/` contiene la suite de pruebas automatizadas para el backend del proyecto. Utiliza **pytest** como framework de testing y **TestClient** de FastAPI para pruebas de endpoints.

---

## 📂 Estructura de Archivos

### 1. **conftest.py**
**Archivo de configuración de pytest que define fixtures globales**

- **Base de Datos de Prueba:** Usa SQLite (`test.db`) en lugar de la BD principal
- **Fixtures Principales:**
  - `client`: Cliente de prueba para hacer requests HTTP
  - `db`: Sesión limpia de base de datos antes de cada prueba (drop + create)
  - `registered_user`: Usuario registrado en el sistema
  - `auth_headers`: Headers con token de autorización válido

**Nota Importante:** Cada prueba tiene una BD limpia gracias al fixture `db` que resetea las tablas

---

### 2. **test_auth_service.py**
**Pruebas unitarias del servicio de autenticación**

#### Clase `TestSecurity`
Valida funciones de seguridad:
- ✅ Hashing de contraseñas genera hashes diferentes cada vez (salt aleatorio)
- ✅ Verificación correcta de contraseñas válidas
- ✅ Rechazo de contraseñas incorrectas
- ✅ Generación de tokens JWT válidos
- ✅ Decodificación de tokens extrae el `user_id` correcto
- ✅ Tokens inválidos lanzan excepciones

#### Clase `TestAuthService`
Pruebas del servicio:
- ✅ Registro exitoso crea usuario con tokens
- ✅ Emails duplicados se rechazan (HTTP 400)
- ✅ Login con credenciales correctas devuelve tokens
- ✅ Login con password incorrecta falla (HTTP 401)
- ✅ Login con email inexistente falla (HTTP 401)

---

### 3. **tests_auth_endpoints.py**
**Pruebas de integración de los endpoints de autenticación**

#### Clase `TestRegisterEndpoint`
- ✅ Registro exitoso devuelve tokens (HTTP 201)
- ✅ Validación: contraseña sin mayúscula se rechaza (HTTP 422)
- ✅ Validación: contraseña < 8 caracteres se rechaza (HTTP 422)
- ✅ Validación: email con formato inválido se rechaza (HTTP 422)

#### Clase `TestLoginEndpoint`
- ✅ Login correcto devuelve access_token (HTTP 200)
- ✅ Login con credenciales incorrectas devuelve error (HTTP 401)

#### Clase `TestProtectedEndpoints`
- ✅ `/auth/me` con token válido devuelve perfil del usuario
- ✅ `/auth/me` sin token devuelve error (HTTP 401)
- ✅ `/auth/logout` cierra sesión correctamente
- ✅ `/auth/me` (PUT) actualiza nombre_completo del usuario

---

### 4. **test_project_service.py**
**Pruebas unitarias del servicio de proyectos**

#### Clase `TestCrearProyecto`
- ✅ Crear proyecto con datos válidos lo guarda en BD
- ✅ Crear proyecto con URL de GitHub la guarda correctamente
- ✅ Crear proyecto sin nombre falla (validación)

#### Clase `TestListarProyectos`
- ✅ Usuario sin proyectos recibe lista vacía
- ✅ Usuario con proyectos los ve en su lista
- ✅ Un usuario **no puede ver** proyectos de otros usuarios (aislamiento)

#### Clase `TestVerProyecto`
- ✅ Ver proyecto propio devuelve datos correctos
- ✅ Ver proyecto inexistente devuelve 404
- ✅ Ver proyecto de otro usuario devuelve 403 (acceso denegado)

#### Clase `TestActualizarProyecto`
- ✅ Actualizar nombre se refleja en BD
- ✅ Actualizar URL de GitHub se guarda correctamente
- ✅ Actualizar proyecto ajeno devuelve 403

---

### 5. **tests_project_endpoints.py**
**Pruebas de integración de los endpoints de proyectos**

#### Clase `TestCrearProyectoEndpoint`
- ✅ Crear proyecto autenticado devuelve 201
- ✅ Crear sin token devuelve 401
- ✅ Crear sin nombre devuelve 422

#### Clase `TestListarProyectosEndpoint`
- ✅ Listar proyectos vacío devuelve lista vacía
- ✅ Después de crear un proyecto aparece en la lista
- ✅ Listar sin token devuelve 401

#### Clase `TestVerProyectoEndpoint`
- ✅ Ver proyecto propio existente devuelve 200
- ✅ Ver proyecto inexistente devuelve 404

#### Clase `TestActualizarProyectoEndpoint`
- ✅ Actualizar nombre se refleja en respuesta
- ✅ Actualizar proyecto inexistente devuelve 404

#### Clase `TestEliminarProyectoEndpoint`
- ✅ Eliminar proyecto exitoso devuelve confirmación
- ✅ Proyecto eliminado no aparece en el listado
- ✅ Eliminar proyecto inexistente devuelve 404

---

### 6. **__init__.py**
Archivo vacío. Convierte la carpeta en paquete Python.

---

## 📊 Estadísticas de Pruebas

| Categoría | Cantidad |
|-----------|----------|
| **Pruebas de Seguridad** | 6 |
| **Pruebas de Autenticación (Service)** | 5 |
| **Pruebas de Endpoints Auth** | 7 |
| **Pruebas de Proyectos (Service)** | 8 |
| **Pruebas de Endpoints Proyectos** | 10 |
| **TOTAL** | ~36 pruebas |

---

## 🎯 Áreas Clave Probadas

### ✅ **Autenticación**
- Hashing y verificación de contraseñas
- Generación y decodificación de tokens JWT
- Validación de credenciales
- Registro y login de usuarios

### ✅ **Seguridad**
- Protección de endpoints con tokens
- Aislamiento de datos entre usuarios
- Validación de acceso (403 cuando corresponde)

### ✅ **Gestión de Proyectos**
- CRUD (Create, Read, Update, Delete)
- Aislamiento por usuario
- Validaciones de datos

### ✅ **Validaciones**
- Formato de email
- Fortaleza de contraseña
- Campos requeridos

---

## 🚀 Cómo Ejecutar las Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar un archivo específico
pytest tests/test_auth_service.py

# Ejecutar una clase específica
pytest tests/test_auth_service.py::TestSecurity

# Ejecutar una prueba específica
pytest tests/test_auth_service.py::TestSecurity::test_hash_password_genera_hash

# Ver más detalles (-v = verbose)
pytest -v

# Ver cobertura de código
pytest --cov=app
```

---

## 📌 Notas Importantes

1. **Fixtures Reutilizables:** Los fixtures en `conftest.py` se usan en múltiples archivos
2. **BD Limpia:** Cada prueba comienza con una BD vacía para evitar efectos secundarios
3. **Aislamiento de Datos:** Las pruebas validan que los usuarios no pueden ver datos de otros
4. **Validaciones Automáticas:** Pydantic valida los datos en los schemas
5. **Autenticación:** Todas las pruebas de endpoints protegidos usan el fixture `auth_headers`

---

**Última actualización:** 23 de mayo de 2026
