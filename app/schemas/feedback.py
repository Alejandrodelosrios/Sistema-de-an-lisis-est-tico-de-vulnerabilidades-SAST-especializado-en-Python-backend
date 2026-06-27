from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Annotated, Literal
from app.models.feedback import CategoriaOpinion

Calificacion5 = Annotated[int, Field(ge=1, le=5)]
NpsScore = Annotated[int, Field(ge=0, le=10)]
EstadoRevisado = Annotated[int, Field(ge=0, le=1)]


# ---------------------------------------------------------------------------
# OPINIONES (burbuja flotante "Tu opinión")
# ---------------------------------------------------------------------------
class OpinionCreate(BaseModel):
    proyecto_id: int | None = None
    categoria: CategoriaOpinion = CategoriaOpinion.sugerencia
    calificacion: Calificacion5 | None = None
    comentario: str = Field(..., min_length=3, max_length=1000)


class OpinionUpdateEstado(BaseModel):
    revisada: EstadoRevisado


class OpinionResponse(BaseModel):
    id: int
    usuario_id: int
    proyecto_id: int | None
    categoria: CategoriaOpinion
    calificacion: int | None
    comentario: str
    revisada: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class OpinionListResponse(BaseModel):
    total: int
    opiniones: list[OpinionResponse]


class MetricasOpinionesResponse(BaseModel):
    total_opiniones: int = Field(..., ge=0)
    promedio_calificacion: float = Field(..., ge=0.0, le=5.0)
    pendientes: int = Field(..., ge=0)
    revisadas: int = Field(..., ge=0)
    por_categoria: dict[str, int]


# ---------------------------------------------------------------------------
# ENCUESTA DE VALIDACIÓN (post-uso)
# ---------------------------------------------------------------------------
class EncuestaCreate(BaseModel):
    proyecto_id: int | None = None

    facilidad_carga: Calificacion5
    relevancia_vulnerabilidades: Calificacion5
    tiempo_analisis_adecuado: Literal["si", "masomenos", "no"]

    claridad_explicaciones: Calificacion5
    aprendio_algo_nuevo: Literal["si", "no"]
    comentario_aprendizaje: str | None = None
    claridad_recomendaciones: Calificacion5

    intuitividad_dashboard: Calificacion5
    comentario_mejora: str | None = None
    nps: NpsScore


class EncuestaResponse(EncuestaCreate):
    id: int
    usuario_id: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class EncuestaListResponse(BaseModel):
    total: int
    respuestas: list[EncuestaResponse]


class MetricasEncuestaResponse(BaseModel):
    total_respuestas: int = Field(..., ge=0)
    promedio_facilidad_carga: float
    promedio_relevancia_vulnerabilidades: float
    promedio_claridad_explicaciones: float
    promedio_claridad_recomendaciones: float
    promedio_intuitividad_dashboard: float
    promedio_nps: float = Field(..., ge=0.0, le=10.0)
    porcentaje_aprendio_algo_nuevo: float = Field(..., ge=0.0, le=100.0)