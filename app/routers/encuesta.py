from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.request_utils import obtener_ip_cliente
from app.database import get_db
from app.core.dependencies import get_current_user, require_superadmin
from app.models.project import Project
from app.models.user import User
from app.models.feedback import RespuestaEncuesta
from app.schemas.feedback import (
    EncuestaCreate, EncuestaResponse, EncuestaListResponse, MetricasEncuestaResponse
)
from app.services import feedback_service
from app.services.activity_service import registrar_actividad
from app.models.activity_log import AccionEnum, RegistroActividad

router = APIRouter(prefix="/encuestas", tags=["Encuestas"])


@router.post("/", response_model=EncuestaResponse, status_code=201)
def responder_encuesta(
    data: EncuestaCreate,
    request:Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ya_uso_el_sistema = db.query(RegistroActividad).filter(
    RegistroActividad.usuario_id == current_user.id,
    RegistroActividad.accion == AccionEnum.analisis_ejecutado).first()
    
    if not ya_uso_el_sistema:
        raise HTTPException(
        status_code=400,
        detail="Debes ejecutar al menos un análisis antes de responder la encuesta"
    )

    if data.proyecto_id is not None:
        proyecto = db.query(Project).filter(
        Project.id == data.proyecto_id,
        Project.usuario_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(status_code=403, detail="Ese proyecto no te pertenece")
    
    nueva = RespuestaEncuesta(
        usuario_id=current_user.id,
        **data.model_dump(),
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    registrar_actividad(
        db, current_user.id, AccionEnum.encuesta_respondida,
        proyecto_id=data.proyecto_id,
        ip_origen=obtener_ip_cliente(request)
    )
    return nueva


@router.get("/", response_model=EncuestaListResponse)
def listar_encuestas(
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    respuestas = feedback_service.listar_encuestas(db)
    return {"total": len(respuestas), "respuestas": respuestas}


@router.get("/metricas", response_model=MetricasEncuestaResponse)
def metricas_encuesta(
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return feedback_service.metricas_encuesta(db)