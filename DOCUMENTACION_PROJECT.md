# Documentación: Módulo Project

## 📋 Índice
1. [Models](#models)
2. [Schemas](#schemas)
3. [Services](#services)
4. [Routers](#routers)
5. [Flujo de Datos](#flujo-de-datos)
6. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Models

### Ubicación
`app/models/project.py`

### Descripción
Define la estructura de la tabla `proyecto` en la base de datos usando SQLAlchemy ORM.

### Estructura

```python
class Project(Base):
    __tablename__ = "proyecto"
```

#### Campos

| Campo | Tipo | Características | Descripción |
|-------|------|-----------------|-------------|
| `id` | Integer | PRIMARY KEY, INDEX | Identificador único del proyecto |
| `nombre` | String(255) | NOT NULL | Nombre del proyecto |
| `origen` | Enum(OrigenEnum) | NOT NULL | Origen del proyecto (github o carga_directa) |
| `url_github` | String(255) | NULLABLE | URL del repositorio de GitHub (opcional) |
| `estado` | Boolean | DEFAULT=True | Estado del proyecto (activo/inactivo) |
| `usuario_id` | Integer | FOREIGN KEY → usuario.id | Identificador del usuario propietario |
| `fecha_carga` | DateTime | server_default=func.now() | Timestamp de creación |

#### Relaciones

```python
usuario = relationship("User", back_populates="proyectos")
archivos = relationship("File", back_populates="proyecto")
```

- **Usuario**: Relación de muchos proyectos a un usuario (N..1)
- **Archivos**: Relación de un proyecto a muchos archivos (1..N)

#### Enum OrigenEnum

```python
class OrigenEnum(str, enum.Enum):
    github = "github"
    carga_directa = "carga_directa"
```

Define dos posibles orígenes:
- `github`: Proyecto importado desde GitHub
- `carga_directa`: Proyecto cargado manualmente

---

## Schemas

### Ubicación
`app/schemas/project.py`

### Descripción
Define los esquemas Pydantic para validación de datos en solicitudes HTTP y respuestas de API.

### Esquemas

#### 1. ProjectCreate
**Propósito**: Validar datos para crear un nuevo proyecto

```python
class ProjectCreate(BaseModel):
    nombre: str
    origen: OrigenEnum
    url_github: str | None = None
```

| Campo | Tipo | Requerido | Notas |
|-------|------|-----------|-------|
| `nombre` | str | ✅ Sí | Nombre del proyecto |
| `origen` | OrigenEnum | ✅ Sí | Origen: github o carga_directa |
| `url_github` | str \| None | ❌ No | URL solo si origen es github |

#### 2. ProjectUpdate
**Propósito**: Validar datos para actualizar un proyecto existente

```python
class ProjectUpdate(BaseModel):
    nombre: str | None = None
    origen: OrigenEnum | None = None
    url_github: str | None = None
```

- Todos los campos son opcionales
- Permite actualizar parcialmente un proyecto

#### 3. ProjectResponse
**Propósito**: Serializar datos de un proyecto en respuestas HTTP

```python
class ProjectResponse(BaseModel):
    id: int
    nombre: str
    origen: OrigenEnum
    url_github: str | None = None
    fecha_carga: datetime
    usuario_id: int
    model_config = ConfigDict(from_attributes=True)
```

- `from_attributes=True`: Permite convertir objetos SQLAlchemy a modelos Pydantic
- Incluye el `id` y `fecha_carga` generados por la BD

#### 4. ProjectListResponse
**Propósito**: Respuesta cuando se listan múltiples proyectos

```python
class ProjectListResponse(BaseModel):
    total: int
    proyectos: list[ProjectResponse]
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `total` | int | Cantidad total de proyectos |
| `proyectos` | list[ProjectResponse] | Lista de proyectos |

---

## Services

### Ubicación
`app/services/project_service.py`

### Descripción
Contiene la lógica de negocio para operaciones CRUD de proyectos. Maneja validaciones, autorizaciones y acceso a base de datos.

### Funciones

#### 1. crear_proyecto()

**Firma**
```python
def crear_proyecto(db: Session, proyecto: ProjectCreate, current_user: User) -> Project
```

**Descripción**: Crea un nuevo proyecto en la base de datos

**Parámetros**
- `db`: Sesión de base de datos
- `proyecto`: Datos del proyecto (ProjectCreate)
- `current_user`: Usuario autenticado que crea el proyecto

**Lógica**
1. Valida los datos del esquema ProjectCreate
2. Si el origen es `github`, asigna la URL proporcionada
3. Si el origen es `carga_directa`, asigna None a la URL
4. Asigna el `usuario_id` del usuario actual
5. Guarda en la base de datos y retorna el proyecto creado

**Retorna**: Objeto Project con datos completos

**Ejemplo de entrada**
```json
{
  "nombre": "Mi Proyecto",
  "origen": "github",
  "url_github": "https://github.com/usuario/repo"
}
```

---

#### 2. get_proyectos()

**Firma**
```python
def get_proyectos(db: Session, current_user: User) -> dict
```

**Descripción**: Obtiene todos los proyectos del usuario autenticado

**Parámetros**
- `db`: Sesión de base de datos
- `current_user`: Usuario autenticado

**Lógica**
1. Consulta la BD filtrando por `usuario_id` del usuario actual
2. Filtra solo proyectos con `estado=True` (activos)
3. Retorna un diccionario con total y lista de proyectos

**Retorna**: Diccionario con estructura ProjectListResponse

**Ejemplo de salida**
```json
{
  "total": 2,
  "proyectos": [
    {
      "id": 1,
      "nombre": "Proyecto 1",
      "origen": "github",
      "url_github": "https://github.com/usuario/repo1",
      "fecha_carga": "2026-05-17T10:30:00",
      "usuario_id": 1
    }
  ]
}
```

---

#### 3. get_proyecto()

**Firma**
```python
def get_proyecto(db: Session, proyecto_id: int, current_user: User) -> Project
```

**Descripción**: Obtiene un proyecto específico por su ID

**Parámetros**
- `db`: Sesión de base de datos
- `proyecto_id`: ID del proyecto a obtener
- `current_user`: Usuario autenticado

**Lógica**
1. Busca el proyecto por ID y estado=True
2. Si no existe: Lanza excepción 404 (NOT_FOUND)
3. Verifica que el usuario actual es el propietario
4. Si no es propietario: Lanza excepción 403 (FORBIDDEN)
5. Retorna el proyecto

**Excepciones**
- `404 NOT_FOUND`: Proyecto no existe o está eliminado
- `403 FORBIDDEN`: El usuario no tiene acceso al proyecto

---

#### 4. update_proyecto()

**Firma**
```python
def update_proyecto(db: Session, proyecto_id: int, proyecto_dato: ProjectUpdate, current_user: User) -> Project
```

**Descripción**: Actualiza datos de un proyecto existente

**Parámetros**
- `db`: Sesión de base de datos
- `proyecto_id`: ID del proyecto a actualizar
- `proyecto_dato`: Datos a actualizar (ProjectUpdate)
- `current_user`: Usuario autenticado

**Lógica**
1. Obtiene el proyecto usando `get_proyecto()` (valida pertenencia)
2. Actualiza campos si se proporcionan valores en proyecto_dato:
   - `nombre`
   - `origen`
   - `url_github`
3. Guarda cambios en BD
4. Retorna el proyecto actualizado

**Retorna**: Objeto Project actualizado

---

#### 5. eliminar_proyecto()

**Firma**
```python
def eliminar_proyecto(db: Session, proyecto_id: int, current_user: User) -> dict
```

**Descripción**: Elimina un proyecto (soft delete - marca como inactivo)

**Parámetros**
- `db`: Sesión de base de datos
- `proyecto_id`: ID del proyecto a eliminar
- `current_user`: Usuario autenticado

**Lógica**
1. Obtiene el proyecto usando `get_proyecto()` (valida pertenencia)
2. Establece `proyecto.estado = False`
3. Guarda cambios en BD
4. Retorna mensaje de confirmación

**Retorna**: Diccionario con mensaje de confirmación

```json
{
  "message": "Proyecto eliminado correctamente"
}
```

**Nota**: No elimina físicamente el registro, solo lo marca como inactivo

---

## Routers

### Ubicación
`app/routers/project.py`

### Descripción
Define los endpoints HTTP (API REST) para operaciones CRUD de proyectos.

### Dependencias
- `APIRouter`: Crear rutas con prefijo común
- `get_db`: Obtener sesión de base de datos
- `get_current_active_user`: Obtener usuario autenticado

### Endpoints

#### 1. Crear Proyecto
**Método**: `POST`  
**Ruta**: `/proyectos/`  
**Status Code**: `201 Created`  
**Respuesta**: `ProjectResponse`

```python
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def crear_proyecto(proyecto: ProjectCreate, db: Session = Depends(get_db), 
                   get_current_active_user: User = Depends(get_current_active_user)):
    return project_service.crear_proyecto(db, proyecto, get_current_active_user)
```

**Descripción**: Crea un nuevo proyecto para el usuario autenticado

**Body (JSON)**
```json
{
  "nombre": "Mi Proyecto",
  "origen": "github",
  "url_github": "https://github.com/usuario/repo"
}
```

**Response (201)**
```json
{
  "id": 1,
  "nombre": "Mi Proyecto",
  "origen": "github",
  "url_github": "https://github.com/usuario/repo",
  "fecha_carga": "2026-05-17T10:30:00",
  "usuario_id": 1
}
```

---

#### 2. Listar Proyectos
**Método**: `GET`  
**Ruta**: `/proyectos/`  
**Respuesta**: `ProjectListResponse`

```python
@router.get("/", response_model=ProjectListResponse)
def get_proyectos(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)):
    return project_service.get_proyectos(db, current_user)
```

**Descripción**: Obtiene todos los proyectos del usuario autenticado

**Response (200)**
```json
{
  "total": 2,
  "proyectos": [
    {
      "id": 1,
      "nombre": "Proyecto 1",
      "origen": "github",
      "url_github": "https://github.com/usuario/repo",
      "fecha_carga": "2026-05-17T10:30:00",
      "usuario_id": 1
    }
  ]
}
```

---

#### 3. Obtener Proyecto por ID
**Método**: `GET`  
**Ruta**: `/proyectos/{proyecto_id}`  
**Respuesta**: `ProjectResponse`

```python
@router.get("/{proyecto_id}", response_model=ProjectResponse)
def get_proyecto(proyecto_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_active_user)):
    return project_service.get_proyecto(db, proyecto_id, current_user)
```

**Descripción**: Obtiene un proyecto específico

**Parámetros**
- `proyecto_id` (path): ID del proyecto

**Response (200)**
```json
{
  "id": 1,
  "nombre": "Proyecto 1",
  "origen": "github",
  "url_github": "https://github.com/usuario/repo",
  "fecha_carga": "2026-05-17T10:30:00",
  "usuario_id": 1
}
```

**Errores**
- `404 NOT_FOUND`: Proyecto no encontrado
- `403 FORBIDDEN`: Sin acceso al proyecto

---

#### 4. Actualizar Proyecto
**Método**: `PUT`  
**Ruta**: `/proyectos/{proyecto_id}`  
**Respuesta**: `ProjectResponse`

```python
@router.put("/{proyecto_id}", response_model=ProjectResponse)
def update_proyecto(proyecto_id: int, proyecto_dato: ProjectUpdate,
                    current_user: User = Depends(get_current_active_user),
                    db: Session = Depends(get_db)):
    return project_service.update_proyecto(db, proyecto_id, proyecto_dato, current_user)
```

**Descripción**: Actualiza datos de un proyecto

**Parámetros**
- `proyecto_id` (path): ID del proyecto

**Body (JSON)** - Todos los campos son opcionales
```json
{
  "nombre": "Nuevo Nombre",
  "origen": "carga_directa"
}
```

**Response (200)**
```json
{
  "id": 1,
  "nombre": "Nuevo Nombre",
  "origen": "carga_directa",
  "url_github": null,
  "fecha_carga": "2026-05-17T10:30:00",
  "usuario_id": 1
}
```

**Errores**
- `404 NOT_FOUND`: Proyecto no encontrado
- `403 FORBIDDEN`: Sin acceso al proyecto

---

#### 5. Eliminar Proyecto
**Método**: `DELETE`  
**Ruta**: `/proyectos/{proyecto_id}`  

```python
@router.delete("/{proyecto_id}")
def eliminar_proyecto(proyecto_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)):
    return project_service.eliminar_proyecto(db, proyecto_id, current_user)
```

**Descripción**: Elimina un proyecto (soft delete)

**Parámetros**
- `proyecto_id` (path): ID del proyecto

**Response (200)**
```json
{
  "message": "Proyecto eliminado correctamente"
}
```

**Errores**
- `404 NOT_FOUND`: Proyecto no encontrado
- `403 FORBIDDEN`: Sin acceso al proyecto

---

## Flujo de Datos

### Flujo de Creación de Proyecto

```
Cliente HTTP
    ↓
POST /proyectos/ + JSON Body
    ↓
Router (crear_proyecto endpoint)
    ↓
Valida usando ProjectCreate schema
    ↓
Service (crear_proyecto function)
    ↓
Crea instancia Project
    ↓
Guarda en BD
    ↓
Serializa usando ProjectResponse
    ↓
Retorna JSON + 201 Created
    ↓
Cliente HTTP recibe respuesta
```

### Flujo de Obtención de Proyecto

```
Cliente HTTP
    ↓
GET /proyectos/{proyecto_id}
    ↓
Router extrae proyecto_id
    ↓
Service (get_proyecto function)
    ↓
Busca en BD
    ↓
Valida existencia (404 si no existe)
    ↓
Valida propiedad (403 si no es dueño)
    ↓
Retorna objeto Project
    ↓
Serializa usando ProjectResponse
    ↓
Retorna JSON + 200 OK
    ↓
Cliente HTTP recibe respuesta
```

---

## Ejemplos de Uso

### 1. Crear un Proyecto desde GitHub

**Solicitud**
```bash
curl -X POST "http://localhost:8000/proyectos/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Scanner Seguridad",
    "origen": "github",
    "url_github": "https://github.com/developer/security-scanner"
  }'
```

**Respuesta**
```json
{
  "id": 5,
  "nombre": "Scanner Seguridad",
  "origen": "github",
  "url_github": "https://github.com/developer/security-scanner",
  "fecha_carga": "2026-05-17T14:25:30.123456",
  "usuario_id": 1
}
```

---

### 2. Crear un Proyecto con Carga Directa

**Solicitud**
```bash
curl -X POST "http://localhost:8000/proyectos/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Proyecto Local",
    "origen": "carga_directa"
  }'
```

**Respuesta**
```json
{
  "id": 6,
  "nombre": "Proyecto Local",
  "origen": "carga_directa",
  "url_github": null,
  "fecha_carga": "2026-05-17T14:26:00.654321",
  "usuario_id": 1
}
```

---

### 3. Listar Todos los Proyectos del Usuario

**Solicitud**
```bash
curl -X GET "http://localhost:8000/proyectos/" \
  -H "Authorization: Bearer <token>"
```

**Respuesta**
```json
{
  "total": 2,
  "proyectos": [
    {
      "id": 5,
      "nombre": "Scanner Seguridad",
      "origen": "github",
      "url_github": "https://github.com/developer/security-scanner",
      "fecha_carga": "2026-05-17T14:25:30.123456",
      "usuario_id": 1
    },
    {
      "id": 6,
      "nombre": "Proyecto Local",
      "origen": "carga_directa",
      "url_github": null,
      "fecha_carga": "2026-05-17T14:26:00.654321",
      "usuario_id": 1
    }
  ]
}
```

---

### 4. Obtener un Proyecto Específico

**Solicitud**
```bash
curl -X GET "http://localhost:8000/proyectos/5" \
  -H "Authorization: Bearer <token>"
```

**Respuesta**
```json
{
  "id": 5,
  "nombre": "Scanner Seguridad",
  "origen": "github",
  "url_github": "https://github.com/developer/security-scanner",
  "fecha_carga": "2026-05-17T14:25:30.123456",
  "usuario_id": 1
}
```

---

### 5. Actualizar Nombre del Proyecto

**Solicitud**
```bash
curl -X PUT "http://localhost:8000/proyectos/5" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Security Scanner v2.0"
  }'
```

**Respuesta**
```json
{
  "id": 5,
  "nombre": "Security Scanner v2.0",
  "origen": "github",
  "url_github": "https://github.com/developer/security-scanner",
  "fecha_carga": "2026-05-17T14:25:30.123456",
  "usuario_id": 1
}
```

---

### 6. Cambiar Origen de Proyecto

**Solicitud**
```bash
curl -X PUT "http://localhost:8000/proyectos/6" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "origen": "github",
    "url_github": "https://github.com/developer/proyecto-local"
  }'
```

---

### 7. Eliminar Proyecto

**Solicitud**
```bash
curl -X DELETE "http://localhost:8000/proyectos/5" \
  -H "Authorization: Bearer <token>"
```

**Respuesta**
```json
{
  "message": "Proyecto eliminado correctamente"
}
```

---

## Consideraciones Importantes

### Seguridad
- ✅ Solo el propietario puede ver sus proyectos
- ✅ Solo el propietario puede actualizar o eliminar
- ✅ Se valida usuario_id en cada operación
- ✅ Requiere autenticación (Bearer token)

### Validaciones
- ✅ Campo `nombre` es obligatorio y no puede estar vacío
- ✅ Campo `origen` solo acepta valores del Enum (github, carga_directa)
- ✅ `url_github` se valida automáticamente en esquema de creación/actualización

### Soft Delete
- Los proyectos no se eliminan físicamente, solo se marcan como `estado=False`
- Las consultas filtran automáticamente por `estado=True`
- Permite recuperación de datos si es necesario

### Timestamps
- `fecha_carga` se genera automáticamente en la base de datos
- No puede ser modificado por el usuario
- Registra cuándo se creó el proyecto

---

## Diagrama de Relaciones

```
┌─────────────────┐
│     Usuario     │
├─────────────────┤
│ id (PK)         │
│ email           │
│ password        │
└────────┬────────┘
         │
         │ 1..N
         │
┌────────▼────────────┐         ┌──────────────────┐
│     Proyecto        │─────────┤    Archivo       │
├─────────────────────┤  1..N   ├──────────────────┤
│ id (PK)             │         │ id (PK)          │
│ nombre              │         │ nombre           │
│ origen              │         │ estado           │
│ url_github          │         │ ruta_almacenam.  │
│ estado              │         │ tamaño_bytes     │
│ usuario_id (FK)     │         │ fecha_carga      │
│ fecha_carga         │         │ proyecto_id (FK) │
└─────────────────────┘         └──────────────────┘
```

---

**Última actualización**: 17 de mayo de 2026  
**Versión de API**: 1.0.1  
**Autor**: Equipo de Desarrollo SAST API
