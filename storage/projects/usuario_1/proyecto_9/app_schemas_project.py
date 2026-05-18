from pydantic import BaseModel, HttpUrl
from pydantic import ConfigDict
from datetime import datetime
from app.models.project import OrigenEnum

class ProjectCreate(BaseModel):
    nombre: str
    origen: OrigenEnum
    url_github: str | None = None

class ProjectUpdate(BaseModel):
    nombre: str | None = None
    origen: OrigenEnum | None = None
    url_github: str | None = None

class ProjectResponse(BaseModel):
    id: int
    nombre: str
    origen: OrigenEnum
    url_github: str | None = None
    fecha_carga: datetime
    usuario_id: int
    model_config = ConfigDict(from_attributes=True)
class ProjectListResponse(BaseModel):
    total: int
    proyectos: list[ProjectResponse]