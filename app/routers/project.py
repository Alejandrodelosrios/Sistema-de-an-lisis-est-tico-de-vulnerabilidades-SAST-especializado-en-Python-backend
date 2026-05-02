from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services import project_service

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def crear_proyecto(proyecto: ProjectCreate, db: Session = Depends(get_db), 
                   get_current_active_user: 
                   User = Depends(get_current_active_user)):
    return project_service.crear_proyecto(db,proyecto,get_current_active_user)

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

@router.put("/{proyecto_id}", response_model=ProjectResponse)
def update_proyecto(proyecto_id: int, proyecto_dato: ProjectUpdate,
                    current_user: User = Depends(get_current_active_user),
                    db: Session = Depends(get_db)):
    return project_service.update_proyecto(db, proyecto_id, proyecto_dato, current_user)

@router.delete("/{proyecto_id}")
def eliminar_proyecto(proyecto_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_active_user)):
    return project_service.eliminar_proyecto(db, proyecto_id,current_user)