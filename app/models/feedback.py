from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum, SmallInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.database import Base
import enum


class CategoriaOpinion(str, enum.Enum):
    bug = "bug"
    sugerencia = "sugerencia"
    felicitacion = "felicitacion"
    otro = "otro"


class Opinion(Base):
    """Burbuja flotante 'Tu opinión' visible en el dashboard."""
    __tablename__ = "opinion"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    proyecto_id = Column(Integer, ForeignKey("proyecto.id"), nullable=True)

    categoria = Column(Enum(CategoriaOpinion), default=CategoriaOpinion.sugerencia, nullable=False)
    calificacion = Column(SmallInteger, nullable=True)  # 1-5 estrellas
    comentario = Column(Text, nullable=False)
    revisada = Column(Integer, default=0)  # 0 pendiente, 1 revisada

    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("User", back_populates="opiniones")
    proyecto = relationship("Project")


class RespuestaEncuesta(Base):
    """Encuesta estructurada de validación, post-uso del sistema."""
    __tablename__ = "respuesta_encuesta"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    proyecto_id = Column(Integer, ForeignKey("proyecto.id"), nullable=True)

    # Análisis de seguridad (SAST)
    facilidad_carga = Column(SmallInteger, nullable=False)
    relevancia_vulnerabilidades = Column(SmallInteger, nullable=False)
    tiempo_analisis_adecuado = Column(String(20), nullable=False)  # si / masomenos / no

    # Retroalimentación pedagógica
    claridad_explicaciones = Column(SmallInteger, nullable=False)
    aprendio_algo_nuevo = Column(String(5), nullable=False)  # si / no
    comentario_aprendizaje = Column(Text, nullable=True)
    claridad_recomendaciones = Column(SmallInteger, nullable=False)

    # UX general
    intuitividad_dashboard = Column(SmallInteger, nullable=False)
    comentario_mejora = Column(Text, nullable=True)
    nps = Column(SmallInteger, nullable=False)  # 0-10

    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("User", back_populates="respuestas_encuesta")
    proyecto = relationship("Project")