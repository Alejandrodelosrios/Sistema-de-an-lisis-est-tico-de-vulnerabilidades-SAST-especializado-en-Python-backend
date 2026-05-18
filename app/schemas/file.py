from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FileCreate(BaseModel):
    nombre: str
    ruta_almacenamiento: str
    tamaño_bytes: int | None = None
    proyecto_id: int


class FileUpdate(BaseModel):
    nombre: str | None = None

class FileResponse(BaseModel):
    id: int
    nombre: str
    estado: bool
    tamaño_bytes: int | None
    fecha_carga: datetime
    proyecto_id: int
    
    model_config = ConfigDict(from_attributes=True)


class FileListResponse(BaseModel):
    total: int
    archivos: list[FileResponse]
