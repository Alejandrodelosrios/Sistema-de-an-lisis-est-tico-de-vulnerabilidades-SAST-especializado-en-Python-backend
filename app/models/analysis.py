from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.database import Base


class Analysis(Base):
    __tablename__ = "analisis"
    
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(Boolean, default=True, nullable=False)
    score_seguridad = Column(Float, nullable=False)
    fecha_ejecucion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    proyecto_id = Column(Integer, ForeignKey("proyecto.id"), nullable=False)
    
    # relaciones
    proyecto = relationship("Project", back_populates="analisis")
    vulnerabilidades = relationship("Vulnerability", back_populates="analisis")
