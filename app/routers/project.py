from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.project import OrigenEnum
from app.services import project_service

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def crear_proyecto(nombre: str = Form(...),
    origen: OrigenEnum = Form(...),
    url_github: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.schemas.project import ProjectCreate
    proyecto_data = ProjectCreate(nombre=nombre, origen=origen, url_github=url_github)
    return await project_service.crear_proyecto(db, proyecto_data, current_user, files)

@router.get("/", response_model=ProjectListResponse)
def get_proyectos(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_active_user)
                     ):
    return project_service.get_proyectos(db,current_user)

@router.get("/{proyecto_id}", response_model=ProjectResponse)
def get_proyecto(proyecto_id:int, db:Session =Depends(get_db),
                 current_user: User = Depends(get_current_active_user)
                 ):
    return project_service.get_proyecto(db,proyecto_id,current_user)

@router.put("/{proyecto_id}/", response_model=ProjectResponse)
async def update_proyecto(
    proyecto_id: int,
    nombre: str = Form(None),
    url_github: str = Form(None),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.schemas.project import ProjectUpdate
    proyecto_dato = ProjectUpdate(nombre=nombre, url_github=url_github)
    return await project_service.update_proyecto(
        db, proyecto_id, proyecto_dato, current_user, files if files else None
    )

@router.delete("/{proyecto_id}")
def eliminar_proyecto(proyecto_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_active_user)):
    return project_service.eliminar_proyecto(db, proyecto_id,current_user)