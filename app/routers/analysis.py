from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.analysis import (
    AnalysisDetailResponse,
    AnalysisListResponse,
    AnalysisHistoryResponse
)
from app.services import analysis_service
from app.services.report_service import generar_reporte_pdf
from app.services import vulnerability_service
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


@router.get("/{proyecto_id}/history/", response_model=AnalysisHistoryResponse)
def get_project_history(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene el historial y evolución de seguridad de un proyecto (CU6).
    
    - **proyecto_id**: ID del proyecto
    - Devuelve lista de análisis ordenados por fecha descendente con conteo de vulnerabilidades por severidad
    """
    return analysis_service.get_project_history(db, proyecto_id, current_user)


@router.get("/{proyecto_id}/analisis/{analisis_id}/reporte")
def descargar_reporte(
    proyecto_id: int,
    analisis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Descarga el reporte PDF de un análisis específico.
    
    - **proyecto_id**: ID del proyecto
    - **analisis_id**: ID del análisis
    - Devuelve un PDF con el reporte completo del análisis
    """
    analisis = analysis_service.get_analisis(db, proyecto_id, analisis_id, current_user)
    resultado = vulnerability_service.get_vulnerabilidades_por_analisis(
        db, analisis_id, proyecto_id, current_user
    )
    vulnerabilidades = resultado["vulnerabilidades"]
    proyecto = db.query(Project).filter(Project.id == proyecto_id).first()

    pdf_buffer = generar_reporte_pdf(proyecto.nombre, analisis, vulnerabilidades)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=reporte_analisis_{analisis_id}.pdf"
        }
    )
