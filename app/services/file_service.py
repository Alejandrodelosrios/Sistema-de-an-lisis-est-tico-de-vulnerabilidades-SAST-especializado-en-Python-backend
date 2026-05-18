import os
import shutil
import httpx
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status

from app.models.file import File
from app.models.project import Project
from app.models.user import User

UPLOAD_DIR = Path("storage/projects")


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


def _generar_ruta(usuario_id: int, proyecto_id: int, nombre: str) -> Path:
    """Crea la carpeta y devuelve la ruta completa del archivo."""
    carpeta = UPLOAD_DIR / f"usuario_{usuario_id}" / f"proyecto_{proyecto_id}"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta / nombre


# ── Cargar archivos .py directos (múltiples) ─────────────────────────────────

async def cargar_archivos(
    db: Session,
    proyecto_id: int,
    current_user: User,
    files: list[UploadFile]
) -> dict:
    _verificar_proyecto(db, proyecto_id, current_user)

    creados = []
    for file in files:
        # 1. Validar que sea .py
        _validar_extension(file.filename)

        # 2. Guardar en disco
        ruta = _generar_ruta(current_user.id, proyecto_id, file.filename)
        with open(ruta, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Registrar en BD
        nuevo = File(
            nombre=file.filename,
            ruta_almacenamiento=str(ruta),
            tamaño_bytes=os.path.getsize(ruta),
            proyecto_id=proyecto_id,
            estado=True
        )
        db.add(nuevo)
        creados.append(nuevo)

    db.commit()
    for f in creados:
        db.refresh(f)

    return {"total": len(creados), "archivos": creados}


# ── Cargar archivos desde GitHub (sin clonar) ────────────────────────────────

async def cargar_desde_github(
    db: Session,
    proyecto_id: int,
    current_user: User,
    url_github: str  # ej: https://github.com/usuario/repositorio
) -> dict:
    _verificar_proyecto(db, proyecto_id, current_user)

    # Extraer usuario y repo de la URL
    # https://github.com/owner/repo  →  owner, repo
    partes = url_github.rstrip("/").split("/")
    if len(partes) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL de GitHub inválida. Formato esperado: https://github.com/usuario/repositorio"
        )
    owner, repo = partes[-2], partes[-1]

    # Obtener la rama por defecto del repositorio
    async with httpx.AsyncClient() as client:
        repo_info_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = await client.get(repo_info_url, headers={"Accept": "application/vnd.github+json"})

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

    # Consultar el árbol completo del repo usando la rama por defecto
    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers={"Accept": "application/vnd.github+json"})

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

    # Filtrar solo archivos .py
    archivos_py = [item for item in tree if item["type"] == "blob" and item["path"].endswith(".py")]

    if not archivos_py:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El repositorio no contiene archivos .py"
        )

    creados = []
    async with httpx.AsyncClient() as client:
        for item in archivos_py:
            # Descargar contenido del archivo (API de contenidos de GitHub)
            contenido_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{item['path']}"
            r = await client.get(contenido_url, headers={"Accept": "application/vnd.github.raw+json"})

            if r.status_code != 200:
                continue  # si falla uno, sigue con el siguiente

            # El nombre visible es solo el filename, no la ruta completa
            nombre = item["path"].replace("/", "_")  # main_utils_helper.py
            ruta = _generar_ruta(current_user.id, proyecto_id, nombre)

            with open(ruta, "wb") as f:
                f.write(r.content)

            nuevo = File(
                nombre=nombre,
                ruta_almacenamiento=str(ruta),
                tamaño_bytes=len(r.content),
                proyecto_id=proyecto_id,
                estado=True
            )
            db.add(nuevo)
            creados.append(nuevo)

    db.commit()
    for f in creados:
        db.refresh(f)

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

    # Pisar el archivo en disco
    ruta = _generar_ruta(current_user.id, archivo.proyecto_id, file.filename)
    with open(ruta, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Actualizar registro en BD
    archivo.nombre = file.filename
    archivo.ruta_almacenamiento = str(ruta)
    archivo.tamaño_bytes = os.path.getsize(ruta)

    db.commit()
    db.refresh(archivo)
    return archivo


# ── Borrado lógico ────────────────────────────────────────────────────────────

def eliminar_archivo(db: Session, archivo_id: int, current_user: User) -> dict:
    archivo = get_archivo(db, archivo_id, current_user)
    archivo.estado = False
    db.commit()
    return {"mensaje": f"Archivo '{archivo.nombre}' eliminado correctamente"}