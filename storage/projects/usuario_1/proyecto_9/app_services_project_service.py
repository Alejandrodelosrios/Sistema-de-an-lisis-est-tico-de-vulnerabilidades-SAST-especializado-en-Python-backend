from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.project import Project, OrigenEnum
from app.models.user import User
from app.schemas.project import ProjectCreate,ProjectUpdate

def crear_proyecto(db: Session, proyecto: ProjectCreate,current_user: User)-> Project:
    """esta funcion se encarga de crear un nuevo proyecto en la base de datos"""
    nuevo_proyecto =Project(
        nombre= proyecto.nombre,
        origen= proyecto.origen,
        url_github=None if proyecto.origen != OrigenEnum.github else proyecto.url_github, 
        usuario_id=current_user.id         
    )

    db.add(nuevo_proyecto)
    db.commit()
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

def update_proyecto(db: Session, proyecto_id: int, proyecto_dato: ProjectUpdate, current_user: User) -> Project:
    """esta funcion se encarga de actualizar un proyecto por su id"""
    proyecto =get_proyecto(db,proyecto_id,current_user)
    if proyecto_dato.nombre is not None:
        proyecto.nombre = proyecto_dato.nombre
    if proyecto_dato.origen is not None:
        proyecto.origen = proyecto_dato.origen
    if proyecto_dato.url_github is not None:
        proyecto.url_github = proyecto_dato.url_github

    db.commit()
    db.refresh(proyecto)
    return proyecto     

def eliminar_proyecto(db: Session, proyecto_id: int,current_user: User)->dict:
    """esta funcion se encarga de eliminar un proyecto por su id"""
    proyecto=get_proyecto(db,proyecto_id,current_user)
    proyecto.estado=False
    db.commit()
    return {"message": "Proyecto eliminado correctamente"}