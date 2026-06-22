from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List


class RecommendationResponseForVuln(BaseModel):
    """Esquema de recomendación para incluir en vulnerabilidades"""
    id: int
    titulo: str
    explicacion_riesgo: str
    codigo_corregido_ejemplo: str | None = None
    fecha_creacion: datetime
    
    model_config = ConfigDict(from_attributes=True)


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


class VulnerabilityWithRecommendationResponse(BaseModel):
    """Esquema para la respuesta de vulnerabilidad con sus recomendaciones asociadas"""
    id: int
    tipo_owasp: str
    severidad: str
    score_cvss: float = Field(..., ge=0.0, le=10.0)
    codigo_vulnerable: str
    linea_codigo: int = Field(..., ge=1)
    fragmento_codigo: str | None = None
    archivo_id: int
    nombre_archivo: str | None = None
    recomendaciones: List[RecommendationResponseForVuln] = Field(
        default_factory=list,
        description="Lista de recomendaciones asociadas a la vulnerabilidad"
    )

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
    vulnerabilidades: List[VulnerabilityWithRecommendationResponse] = Field(
        default_factory=list,
        description="Lista de vulnerabilidades encontradas en el análisis"
    )

    model_config = ConfigDict(from_attributes=True)

class AnalysisListResponse(BaseModel):
    total: int
    analisis: list[AnalysisResponse]


class VulnerabilityListResponse(BaseModel):
    """Esquema para la respuesta de lista de vulnerabilidades con recomendaciones"""
    total: int
    vulnerabilidades: List[VulnerabilityWithRecommendationResponse]

    model_config = ConfigDict(from_attributes=True)


class VulnerabilitySummaryResponse(BaseModel):
    """Esquema para el resumen de vulnerabilidades por severidad"""
    critica: int = Field(..., ge=0, description="Cantidad de vulnerabilidades críticas")
    alta: int = Field(..., ge=0, description="Cantidad de vulnerabilidades altas")
    media: int = Field(..., ge=0, description="Cantidad de vulnerabilidades medias")
    baja: int = Field(..., ge=0, description="Cantidad de vulnerabilidades bajas")
    total: int = Field(..., ge=0, description="Total de vulnerabilidades")


class AnalysisHistoryItem(BaseModel):
    """Esquema para un elemento del historial de análisis de seguridad"""
    id: int = Field(..., description="Identificador único del análisis")
    fecha_ejecucion: datetime = Field(..., description="Fecha y hora de ejecución del análisis")
    score_seguridad: float = Field(..., ge=0.0, le=100.0, description="Puntuación de seguridad del análisis")
    vulnerabilidades_por_severidad: VulnerabilitySummaryResponse = Field(
        ...,
        description="Conteo de vulnerabilidades agrupadas por severidad"
    )

    model_config = ConfigDict(from_attributes=True)


class AnalysisHistoryResponse(BaseModel):
    """Esquema para la respuesta del historial de análisis"""
    total: int = Field(..., ge=0, description="Total de análisis en el historial")
    historial: List[AnalysisHistoryItem] = Field(
        ...,
        description="Lista de análisis ordenados por fecha descendente"
    )

    model_config = ConfigDict(from_attributes=True)