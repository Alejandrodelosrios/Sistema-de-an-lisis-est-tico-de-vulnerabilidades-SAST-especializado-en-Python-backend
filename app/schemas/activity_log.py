from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.models.activity_log import AccionEnum


class RegistroActividadResponse(BaseModel):
    id: int
    usuario_id: int
    proyecto_id: int | None
    accion: AccionEnum
    detalle: str | None
    ip_origen: str | None
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class RegistroActividadListResponse(BaseModel):
    total: int
    registros: list[RegistroActividadResponse]


# --- Para el dashboard del superadmin -------------------------------------
class ResumenActividadUsuario(BaseModel):
    """Una fila de la tabla 'Usuarios y su actividad'."""
    usuario_id: int
    nombre_completo: str
    correo: str
    fecha_registro: datetime
    ultimo_login: datetime | None = None
    total_proyectos: int = Field(..., ge=0)
    total_analisis: int = Field(..., ge=0)
    dejo_opinion: bool


class ResumenActividadListResponse(BaseModel):
    total: int
    usuarios: list[ResumenActividadUsuario]


class TimelineEvento(BaseModel):
    """Un evento dentro de la línea de tiempo de un usuario."""
    accion: AccionEnum
    detalle: str | None
    proyecto_id: int | None
    fecha: datetime


class TimelineUsuarioResponse(BaseModel):
    usuario_id: int
    eventos: list[TimelineEvento]