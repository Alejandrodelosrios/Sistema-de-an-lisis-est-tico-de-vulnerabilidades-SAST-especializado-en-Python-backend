from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.database import Base


class File(Base):
    __tablename__ = "archivo"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    estado = Column(Boolean, default=True)
    ruta_almacenamiento = Column(String(255))
    tamaño_bytes = Column(Integer)
    fecha_carga = Column(DateTime(timezone=True), server_default=func.now())
    proyecto_id = Column(Integer, ForeignKey("proyecto.id"), nullable=False)
    
    # relaciones
    proyecto = relationship("Project", back_populates="archivos")
