from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import require_superadmin
from app.models.user import User
from app.schemas.activity_log import (
    ResumenActividadListResponse, TimelineUsuarioResponse
)
from app.services import dashboard_service

router = APIRouter(prefix="/admin/actividad", tags=["Actividad (Superadmin)"])


@router.get("/usuarios", response_model=ResumenActividadListResponse)
def resumen_usuarios(
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    """Tabla 'Usuarios y su actividad' del dashboard del superadmin."""
    usuarios = dashboard_service.resumen_actividad_usuarios(db)
    return {"total": len(usuarios), "usuarios": usuarios}


@router.get("/usuarios/{usuario_id}/timeline", response_model=TimelineUsuarioResponse)
def timeline_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    """Línea de tiempo cronológica de un usuario específico."""
    eventos = dashboard_service.timeline_usuario(db, usuario_id)
    if not eventos:
        # No es error fatal: puede que el usuario simplemente no tenga actividad aún
        return {"usuario_id": usuario_id, "eventos": []}
    return {"usuario_id": usuario_id, "eventos": eventos}