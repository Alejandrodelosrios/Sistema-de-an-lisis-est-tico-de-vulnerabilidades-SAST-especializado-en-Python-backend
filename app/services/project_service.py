from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from typing import Optional
from app.models.activity_log import AccionEnum
from app.models.project import Project, OrigenEnum
from app.models.user import User
from app.schemas.project import ProjectCreate,ProjectUpdate
from app.services.activity_service import registrar_actividad
import app.services.file_service as file_service

async def crear_proyecto(
    db: Session,
    proyecto: ProjectCreate,
    current_user: User,
    ip:str,
    files: Optional[list[UploadFile]] = None   # ← parámetro nuevo
) -> Project:

    # Validación según origen — antes no existía esto
    if proyecto.origen == OrigenEnum.github:
        if not proyecto.url_github:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debés proporcionar la URL del repositorio de GitHub"
            )
    elif proyecto.origen == OrigenEnum.carga_directa:
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debés subir al menos un archivo .py"
            )

    # Crear el proyecto en BD — igual que antes
    nuevo_proyecto = Project(
        nombre=proyecto.nombre,
        origen=proyecto.origen,
        url_github=proyecto.url_github if proyecto.origen == OrigenEnum.github else None,
        usuario_id=current_user.id
    )
    db.add(nuevo_proyecto)
    db.commit()
    db.refresh(nuevo_proyecto)

    registrar_actividad(db,nuevo_proyecto.usuario_id,AccionEnum.proyecto_creado,
                        proyecto_id=nuevo_proyecto.id,
                        detalle=f"Proyecto: {nuevo_proyecto.nombre} ({nuevo_proyecto.origen.value})",
                        ip_origen=ip
                       )

    # Disparar carga de archivos internamente según origen
    if proyecto.origen == OrigenEnum.github:
        await file_service.cargar_desde_github(
            db=db,
            proyecto_id=nuevo_proyecto.id,
            current_user=current_user,
            url_github=proyecto.url_github,
            ip=ip
        )
    else:
        await file_service.cargar_archivos(
            db=db,
            proyecto_id=nuevo_proyecto.id,
            current_user=current_user,
            files=files,
            ip=ip
        )

    db.refresh(nuevo_proyecto)
    return nuevo_proyecto

def get_proyectos(db: Session ,current_user:User)-> dict:
    """esta funcion se encarga de obtener todos los proyectos del usuario autenticado"""
    proyectos = db.query(Project).filter(Project.usuario_id == current_user.id,Project.estado == True).all()
    total = len(proyectos)
    return {
        "total": total,
        "proyectos": proyectos
    }

def get_proyecto(db:Session, proyecto_id: int,current_user: User)-> Project:
    """esta funcion se encarga de obtener un proyecto por su id"""
    proyecto = db.query(Project).filter(Project.id == proyecto_id,
                                        Project.estado==True).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    if proyecto.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés acceso a este proyecto"
        )
    return proyecto

async def update_proyecto(db: Session, proyecto_id: int, proyecto_dato: ProjectUpdate, current_user: User,ip:str, files=None) -> Project:
    """esta funcion se encarga de actualizar un proyecto por su id"""
    proyecto = get_proyecto(db, proyecto_id, current_user)
    if proyecto_dato.nombre is not None:
        proyecto.nombre = proyecto_dato.nombre
    
    if proyecto.origen == OrigenEnum.github and proyecto_dato.url_github:
        if proyecto.url_github != proyecto_dato.url_github:
            proyecto.url_github = proyecto_dato.url_github

        # Traer todos los archivos activos del proyecto usando el service existente
        resultado = file_service.get_archivos(db, proyecto.id, current_user)
        archivos_actuales = resultado["archivos"]

        # Borrado lógico uno por uno usando el service existente
        for archivo in archivos_actuales:
            file_service.eliminar_archivo(db, archivo.id, current_user)

        # Descargar archivos frescos desde GitHub
        await file_service.cargar_desde_github(
            db=db,
            proyecto_id=proyecto.id,
            current_user=current_user,
            url_github=proyecto.url_github,
            ip=ip
        )
    
    # Si es carga_directa y vienen archivos → agregar
    if proyecto.origen == OrigenEnum.carga_directa and files:
        await file_service.cargar_archivos(
            db=db,
            proyecto_id=proyecto.id,
            current_user=current_user,
            files=files,
            ip=ip
            
        )
    # Si el proyecto es github pero vienen archivos → rechazar explícitamente
    elif proyecto.origen == OrigenEnum.github and files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este proyecto usa GitHub como origen. No se pueden subir archivos directamente. Actualizá la URL del repositorio."
        )
    
    # Si es carga_directa pero intentan poner una URL de GitHub → rechazar
    if proyecto.origen == OrigenEnum.carga_directa and proyecto_dato.url_github:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este proyecto usa carga directa. No se puede cambiar a origen GitHub. Crea un nuevo proyecto si necesitás usar GitHub."
        )

    db.commit()
    db.refresh(proyecto)
    registrar_actividad(db,proyecto.usuario_id,AccionEnum.proyecto_actualizado,
                        proyecto_id=proyecto.id,
                        detalle=f"Proyecto: {proyecto.nombre} ({proyecto.origen.value})",
                        ip_origen=ip
                        )
    return proyecto     

def eliminar_proyecto(db: Session, proyecto_id: int,current_user: User,ip:str)->dict:
    """esta funcion se encarga de eliminar un proyecto por su id"""
    proyecto=get_proyecto(db,proyecto_id,current_user)
    proyecto.estado=False
    db.commit()
    registrar_actividad(db,proyecto.usuario_id,AccionEnum.proyecto_eliminado,
                        proyecto_id=proyecto.id,
                        detalle=f"Proyecto: {proyecto.nombre} ({proyecto.origen.value})",
                        ip_origen=ip
                        )
    return {"message": "Proyecto eliminado correctamente"}