from fastapi import APIRouter, Depends, UploadFile, File, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.file import FileResponse, FileListResponse
from app.services import file_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/proyectos", tags=["Archivos"])

# GET /proyectos/{proyecto_id}/archivos
@router.get("/{proyecto_id}/archivos", response_model=FileListResponse)
def get_archivos(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return file_service.get_archivos(db, proyecto_id, current_user)


# GET /proyectos/{proyecto_id}/archivos/{archivo_id}
@router.get("/{proyecto_id}/archivos/{archivo_id}", response_model=FileResponse)
def get_archivo(
    proyecto_id: int,
    archivo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return file_service.get_archivo(db, archivo_id, current_user)


# PUT /proyectos/{proyecto_id}/archivos/{archivo_id}
@router.put("/{proyecto_id}/archivos/{archivo_id}", response_model=FileResponse)
async def update_archivo(
    proyecto_id: int,
    archivo_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await file_service.update_archivo(db, archivo_id, current_user, file)


# DELETE /proyectos/{proyecto_id}/archivos/{archivo_id}
@router.delete("/{proyecto_id}/archivos/{archivo_id}")
def eliminar_archivo(
    proyecto_id: int,
    archivo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return file_service.eliminar_archivo(db, archivo_id, current_user)