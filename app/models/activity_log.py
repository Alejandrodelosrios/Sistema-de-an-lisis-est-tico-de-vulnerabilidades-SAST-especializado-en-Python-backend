from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.database import Base
import enum


class AccionEnum(str, enum.Enum):
    registro = "registro"
    login = "login"
    logout = "logout"
    proyecto_creado = "proyecto_creado"
    proyecto_eliminado = "proyecto_eliminado"
    proyecto_actualizado = "proyecto_actualizado"
    archivo_subido = "archivo_subido"
    analisis_ejecutado = "analisis_ejecutado"
    reporte_descargado = "reporte_descargado"
    opinion_enviada = "opinion_enviada"
    encuesta_respondida = "encuesta_respondida"


class RegistroActividad(Base):
    """
    Bitácora de eventos clave por usuario. No reemplaza a 'Opinion' ni a
    'RespuestaEncuesta': los complementa, dando evidencia de que detrás
    de cada opinión hay un usuario que realmente usó el sistema antes
    de opinar.
    """
    __tablename__ = "registro_actividad"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    proyecto_id = Column(Integer, ForeignKey("proyecto.id"), nullable=True)

    accion = Column(Enum(AccionEnum), nullable=False)
    detalle = Column(String(255), nullable=True)  # ej. "Vulnerabilidades encontradas: 7"
    ip_origen = Column(String(45), nullable=True)

    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("User")
    proyecto = relationship("Project")