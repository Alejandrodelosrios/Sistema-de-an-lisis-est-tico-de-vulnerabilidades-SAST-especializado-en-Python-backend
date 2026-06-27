import httpx
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from app.models.activity_log import AccionEnum
from app.models.file import File
from app.models.project import Project
from app.models.user import User
from app.services.activity_service import registrar_actividad
from app.core.github_utils import github_headers, verificar_rate_limit

# ── Helpers internos ─────────────────────────────────────────────────────────

def _verificar_proyecto(db: Session, proyecto_id: int, current_user: User) -> Project:
    """Verifica que el proyecto existe y pertenece al usuario."""
    proyecto = db.query(Project).filter(
        Project.id == proyecto_id,
        Project.usuario_id == current_user.id,
        Project.estado == True
    ).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés acceso a este proyecto o no existe"
        )
    return proyecto

def _verificar_acceso_archivo(db: Session, archivo: File, current_user: User):
    """Verifica que el archivo pertenece a un proyecto del usuario."""
    proyecto = db.query(Project).filter(
        Project.id == archivo.proyecto_id,
        Project.usuario_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés acceso a este archivo"
        )

def _validar_extension(nombre: str):
    """Lanza excepción si el archivo no es .py"""
    if not nombre.endswith(".py"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se permiten archivos .py — '{nombre}' no es válido"
        )
    
# ── Cargar archivos .py directos (múltiples) ─────────────────────────────────

async def cargar_archivos(
    db: Session,
    proyecto_id: int,
    current_user: User,
    files: list[UploadFile],
    ip: str
) -> dict:
    _verificar_proyecto(db, proyecto_id, current_user)
 
    creados = []
    for file in files:
        _validar_extension(file.filename)
 
        bytes_contenido = await file.read()
        try:
            texto_contenido = bytes_contenido.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo '{file.filename}' no es texto UTF-8 válido"
            )
 
        nuevo = File(
            nombre=file.filename,
            ruta_almacenamiento=None,
            contenido=texto_contenido,
            tamaño_bytes=len(bytes_contenido),
            proyecto_id=proyecto_id,
            estado=True
        )
        db.add(nuevo)
        creados.append(nuevo)
 
    db.commit()
    for f in creados:
        db.refresh(f)
 
    registrar_actividad(
        db, current_user.id, AccionEnum.archivo_subido,
        proyecto_id=proyecto_id,
        detalle=f"{len(creados)} archivos cargados desde carga directa",
        ip_origen=ip
    )
 
    return {"total": len(creados), "archivos": creados}

# ── Cargar archivos desde GitHub (sin clonar) ────────────────────────────────

async def cargar_desde_github(
    db: Session,
    proyecto_id: int,
    current_user: User,
    url_github: str,
    ip: str
) -> dict:
    _verificar_proyecto(db, proyecto_id, current_user)
 
    partes = url_github.rstrip("/").split("/")
    if len(partes) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL de GitHub inválida. Formato esperado: https://github.com/usuario/repositorio"
        )
    owner, repo = partes[-2], partes[-1]
 
    async with httpx.AsyncClient() as client:
        repo_info_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = await client.get(repo_info_url, headers=github_headers())
 
    verificar_rate_limit(response)
    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repositorio no encontrado. Verificá que sea público y que la URL sea correcta"
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error al conectar con GitHub. Intentá de nuevo más tarde"
        )
 
    default_branch = response.json().get("default_branch", "main")
 
    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
 
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=github_headers())
 
    verificar_rate_limit(response)
    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repositorio no encontrado. Verificá que sea público y que la URL sea correcta"
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error al conectar con GitHub. Intentá de nuevo más tarde"
        )
 
    tree = response.json().get("tree", [])
    archivos_py = [item for item in tree if item["type"] == "blob" and item["path"].endswith(".py")]
 
    if not archivos_py:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El repositorio no contiene archivos .py"
        )
 
    creados = []
    for item in archivos_py:
        nombre = item["path"].replace("/", "_")
 
        nuevo = File(
            nombre=nombre,
            ruta_almacenamiento=item['path'],  # path dentro del repo, usado como identificador
            contenido=None,                    # GitHub se lee fresco en cada análisis, no se persiste aquí
            tamaño_bytes=item.get("size", None),
            proyecto_id=proyecto_id,
            estado=True
        )
        db.add(nuevo)
        creados.append(nuevo)
 
    db.commit()
    for f in creados:
        db.refresh(f)
 
    registrar_actividad(
        db, current_user.id, AccionEnum.archivo_subido,
        proyecto_id=proyecto_id,
        detalle=f"{len(creados)} archivos cargados desde GitHub",
        ip_origen=ip
    )
    return {"total": len(creados), "archivos": creados}

# ── Listar archivos activos de un proyecto ────────────────────────────────────

def get_archivos(db: Session, proyecto_id: int, current_user: User) -> dict:
    _verificar_proyecto(db, proyecto_id, current_user)
 
    archivos = db.query(File).filter(
        File.proyecto_id == proyecto_id,
        File.estado == True
    ).all()
 
    return {"total": len(archivos), "archivos": archivos}

# ── Obtener un archivo por ID ─────────────────────────────────────────────────

def get_archivo(db: Session, archivo_id: int, current_user: User) -> File:
    archivo = db.query(File).filter(
        File.id == archivo_id,
        File.estado == True
    ).first()
 
    if not archivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
 
    _verificar_acceso_archivo(db, archivo, current_user)
    return archivo

# ── Reemplazar un archivo (nueva versión) ─────────────────────────────────────

async def update_archivo(
    db: Session,
    archivo_id: int,
    current_user: User,
    file: UploadFile
) -> File:
    archivo = get_archivo(db, archivo_id, current_user)
    _validar_extension(file.filename)
 
    bytes_contenido = await file.read()
    try:
        texto_contenido = bytes_contenido.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo '{file.filename}' no es texto UTF-8 válido"
        )
 
    archivo.nombre = file.filename
    archivo.contenido = texto_contenido
    archivo.ruta_almacenamiento = None
    archivo.tamaño_bytes = len(bytes_contenido)
 
    db.commit()
    db.refresh(archivo)
    return archivo

# ── Borrado lógico ────────────────────────────────────────────────────────────

def eliminar_archivo(db: Session, archivo_id: int, current_user: User) -> dict:
    archivo = get_archivo(db, archivo_id, current_user)
    archivo.estado = False
    db.commit()
    return {"mensaje": f"Archivo '{archivo.nombre}' eliminado correctamente"}