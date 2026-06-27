from pydantic import BaseModel, ConfigDict
from datetime import datetime

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

class FileContentResponse(FileResponse):
    """
    Para ver el detalle de UN archivo puntual (GET /archivos/{id}/contenido),
    por ejemplo si quieres mostrar el código fuente en el frontend.
    """
    contenido: str | None = None