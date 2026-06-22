from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.database import Base


class Recommendation(Base):
    __tablename__ = "recomendacion"
    
    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilidad.id"), nullable=False)
    titulo = Column(String(255), nullable=False)
    explicacion_riesgo = Column(Text, nullable=False)
    codigo_corregido_ejemplo = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # relaciones
    vulnerabilidad = relationship("Vulnerability", back_populates="recomendaciones")
