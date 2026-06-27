from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.request_utils import obtener_ip_cliente
from app.database import get_db
from app.core.dependencies import get_current_user, require_superadmin
from app.models.project import Project
from app.models.user import User
from app.models.feedback import Opinion
from app.schemas.feedback import (
    OpinionCreate, OpinionResponse, OpinionListResponse,
    OpinionUpdateEstado, MetricasOpinionesResponse
)
from app.services import feedback_service
from app.services.activity_service import registrar_actividad
from app.models.activity_log import AccionEnum

router = APIRouter(prefix="/opiniones", tags=["Opiniones"])


@router.post("/", response_model=OpinionResponse, status_code=201)
def crear_opinion(
    data: OpinionCreate,
    request:Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Se llama desde la burbuja flotante 'Tu opinión'."""
    if data.proyecto_id is not None:
        proyecto = db.query(Project).filter(
        Project.id == data.proyecto_id,
        Project.usuario_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(status_code=403, detail="Ese proyecto no te pertenece")
    
    nueva = Opinion(
        usuario_id=current_user.id,
        proyecto_id=data.proyecto_id,
        categoria=data.categoria,
        calificacion=data.calificacion,
        comentario=data.comentario,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    registrar_actividad(
        db, current_user.id, AccionEnum.opinion_enviada,
        proyecto_id=data.proyecto_id,
        detalle=f"Categoría: {data.categoria.value}",
        ip_origen=obtener_ip_cliente(request)
    )
    return nueva


@router.get("/", response_model=OpinionListResponse)
def listar_opiniones(
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    opiniones = db.query(Opinion).order_by(Opinion.creado_en.desc()).all()
    return {"total": len(opiniones), "opiniones": opiniones}


@router.patch("/{opinion_id}/estado", response_model=OpinionResponse)
def marcar_estado(
    opinion_id: int,
    data: OpinionUpdateEstado,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    opinion = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not opinion:
        raise HTTPException(status_code=404, detail="Opinión no encontrada")
    opinion.revisada = data.revisada
    db.commit()
    db.refresh(opinion)
    return opinion


@router.get("/metricas", response_model=MetricasOpinionesResponse)
def metricas_opiniones(
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return feedback_service.metricas_opiniones(db)