from pydantic import BaseModel, EmailStr,field_validator,ConfigDict
from datetime import datetime
import re
from app.models.user import RolEnum

def validar_password(password: str)->str:
    """esta funcion valida que la contraseña cumpla con los requisitos de seguridad"""
    if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not re.search(r"[A-Z]", password):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
    if not re.search(r"[a-z]", password):
            raise ValueError("La contraseña debe tener al menos una minúscula")
    if not re.search(r"\d", password):
            raise ValueError("La contraseña debe tener al menos un número")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("La contraseña debe tener al menos un símbolo")
    return password

class UserBase(BaseModel):
    nombre_completo: str
    correo: EmailStr

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        return validar_password(value)

class UserLogin(BaseModel):
    correo: EmailStr
    password: str

class UserUpdate(BaseModel):
    nombre_completo: str | None = None
    correo: EmailStr | None =None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value):
        return validar_password(value)
    

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value, values):
        if "new_password" in values.data and value != values.data["new_password"]:
            raise ValueError("Las contraseñas no coinciden")
        return value
    
class UserResponse(UserBase):
    id: int
    activo: bool
    rol: RolEnum
    fecha_registro:datetime
    model_config = ConfigDict(from_attributes=True)

class UserAdminResponse(UserResponse):
     cantidad_proyectos:int
     cantidad_analisis:int
     score_promedio:float | None = None
     ultimo_analisis:datetime | None = None
         