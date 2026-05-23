from sqlalchemy import Column, Integer, String,Boolean, DateTime, ForeignKey,Enum
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.database import Base
import enum

class OrigenEnum(str,enum.Enum):
    github="github"
    carga_directa="carga_directa"

class Project(Base):
    __tablename__ = "proyecto"
    id=Column(Integer, primary_key=True, index=True)
    nombre=Column(String(255), nullable=False)
    origen=Column(Enum(OrigenEnum),nullable=False)
    url_github=Column(String(255), nullable=True)
    estado=Column(Boolean(),default=True)
    usuario_id=Column(Integer,ForeignKey("usuario.id"),nullable=False)
    fecha_carga=Column(DateTime(timezone=True), server_default=func.now())
    
    #relaciones
    usuario=relationship("User",back_populates="proyectos")
    archivos=relationship("File", back_populates="proyecto")
    analisis=relationship("Analysis", back_populates="proyecto")
