from sqlalchemy import Column, Integer, String,Boolean, DateTime
from sqlalchemy import func
from app.database import Base

class User(Base):
    __tablename__ = "usuario"

    id=Column(Integer, primary_key=True, index=True) 
    nombre_completo=Column(String(150), nullable=False)
    correo=Column(String(100), unique=True, index=True, nullable=False)
    password=Column(String(255), nullable=False)
    activo=Column(Boolean, default=True)
    fecha_registro=Column(DateTime(timezone=True), server_default=func.now())
    refresh_token=Column(String,nullable=True)
