from pydantic_settings import BaseSettings
from pydantic import ConfigDict, EmailStr

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    SUPERADMIN_NOMBRE: str
    SUPERADMIN_EMAIL: EmailStr
    SUPERADMIN_PASSWORD: str

# Token de GitHub (opcional) para subir el límite de la API
    # de 60 a 5000 requests/hora. Generar en:
    # https://github.com/settings/tokens (solo necesita ser "classic",
    # sin scopes, ya que solo lees repos públicos)
    GITHUB_TOKEN: str | None = None

settings = Settings() 