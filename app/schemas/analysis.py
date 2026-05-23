from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List


class VulnerabilityResponse(BaseModel):
    """Esquema para la respuesta de cada vulnerabilidad encontrada"""
    id:int 
    tipo_owasp: str
    severidad: str
    score_cvss: float = Field(..., ge=0.0, le=10.0)
    codigo_vulnerable: str
    linea_codigo: int = Field(..., ge=1)
    fragmento_codigo: str| None = None
    archivo_id: int
    nombre_archivo: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisResponse(BaseModel):
    """Esquema para la respuesta de un análisis"""
    id: int = Field(..., description="Identificador único del análisis")
    score_seguridad: float = Field(..., ge=0.0, le=100.0, description="Puntuación general del análisis")
    fecha_ejecucion: datetime = Field(..., description="Fecha y hora del análisis")

    model_config = ConfigDict(from_attributes=True)


class AnalysisDetailResponse(BaseModel):
    """Esquema que combina el análisis con todas las vulnerabilidades encontradas"""
    id: int = Field(..., description="Identificador único del análisis")
    score_seguridad: float = Field(..., ge=0.0, le=100.0, description="Puntuación general del análisis")
    fecha_ejecucion: datetime = Field(..., description="Fecha y hora del análisis")
    vulnerabilidades: List[VulnerabilityResponse] = Field(
        default_factory=list,
        description="Lista de vulnerabilidades encontradas en el análisis"
    )

    model_config = ConfigDict(from_attributes=True)

class AnalysisListResponse(BaseModel):
    total: int
    analisis: list[AnalysisResponse]


class VulnerabilityListResponse(BaseModel):
    """Esquema para la respuesta de lista de vulnerabilidades"""
    total: int
    vulnerabilidades: List[VulnerabilityResponse]

    model_config = ConfigDict(from_attributes=True)


class VulnerabilitySummaryResponse(BaseModel):
    """Esquema para el resumen de vulnerabilidades por severidad"""
    critica: int = Field(..., ge=0, description="Cantidad de vulnerabilidades críticas")
    alta: int = Field(..., ge=0, description="Cantidad de vulnerabilidades altas")
    media: int = Field(..., ge=0, description="Cantidad de vulnerabilidades medias")
    baja: int = Field(..., ge=0, description="Cantidad de vulnerabilidades bajas")
    total: int = Field(..., ge=0, description="Total de vulnerabilidades")