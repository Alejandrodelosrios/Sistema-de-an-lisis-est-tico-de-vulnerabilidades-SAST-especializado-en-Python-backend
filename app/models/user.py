from sqlalchemy import Column, Integer, String,Boolean, DateTime,Enum
from sqlalchemy import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RolEnum(str, enum.Enum):
    superadmin = "superadmin"
    estudiante = "estudiante"

class User(Base):
    __tablename__ = "usuario"

    id=Column(Integer, primary_key=True, index=True) 
    nombre_completo=Column(String(150), nullable=False)
    correo=Column(String(100), unique=True, index=True, nullable=False)
    password=Column(String(255), nullable=False)
    activo=Column(Boolean, default=True)
    rol=Column(Enum(RolEnum), nullable=False, default=RolEnum.estudiante)
    fecha_registro=Column(DateTime(timezone=True), server_default=func.now())
    refresh_token=Column(String,nullable=True)
    
    #relaciones
    proyectos=relationship("Project",back_populates="usuario")
    opiniones = relationship("Opinion", back_populates="usuario")
    respuestas_encuesta = relationship("RespuestaEncuesta", back_populates="usuario")
