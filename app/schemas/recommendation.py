from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RecommendationBase(BaseModel):
    titulo: str
    explicacion_riesgo: str
    codigo_corregido_ejemplo: str | None = None


class RecommendationCreate(RecommendationBase):
    vulnerability_id: int


class RecommendationResponse(RecommendationBase):
    id: int
    vulnerability_id: int
    fecha_creacion: datetime
    
    model_config = ConfigDict(from_attributes=True)
