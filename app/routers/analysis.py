from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.analysis import (
    AnalysisDetailResponse,
    AnalysisListResponse
)
from app.services import analysis_service
from app.core.dependencies import get_current_active_user


router = APIRouter(prefix="/proyectos", tags=["Análisis"])


@router.post("/{proyecto_id}/analisis/", response_model=AnalysisDetailResponse, status_code=status.HTTP_201_CREATED)
async def ejecutar_analisis(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ejecuta un análisis de seguridad en todos los archivos de un proyecto.
    
    - **proyecto_id**: ID del proyecto a analizar
    - Devuelve el análisis creado con todas sus vulnerabilidades detectadas
    """
    return await analysis_service.ejecutar_analisis(db, proyecto_id, current_user)


@router.get("/{proyecto_id}/analisis/", response_model=AnalysisListResponse)
def listar_analisis(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todos los análisis realizados en un proyecto.
    
    - **proyecto_id**: ID del proyecto
    - Devuelve lista de análisis ordenados por fecha descendente
    """
    return analysis_service.listar_analisis(db, proyecto_id, current_user)


@router.get("/{proyecto_id}/analisis/{analisis_id}/", response_model=AnalysisDetailResponse)
def get_analisis(
    proyecto_id: int,
    analisis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene los detalles de un análisis específico.
    
    - **proyecto_id**: ID del proyecto (utilizado para verificación de acceso)
    - **analisis_id**: ID del análisis a obtener
    - Devuelve el análisis con todas sus vulnerabilidades
    """
    return analysis_service.get_analisis(db,proyecto_id, analisis_id, current_user)
