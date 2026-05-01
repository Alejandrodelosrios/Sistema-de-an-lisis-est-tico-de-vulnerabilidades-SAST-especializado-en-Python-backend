from pydantic import BaseModel, EmailStr,field_validator,ConfigDict
from datetime import datetime
import re

class UserBase(BaseModel):
    nombre_completo: str
    correo: EmailStr

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        """esta funcion valida que la contraseña cumpla con los requisitos de seguridad"""
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", value):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe tener al menos un número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("La contraseña debe tener al menos un símbolo")
        return value

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
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", value):
            raise ValueError("Debe tener al menos una minúscula")
        if not re.search(r"\d", value):
            raise ValueError("Debe tener al menos un número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Debe tener al menos un símbolo")
        return value

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value, values):
        if "new_password" in values.data and value != values.data["new_password"]:
            raise ValueError("Las contraseñas no coinciden")
        return value
    
class UserResponse(UserBase):
    id: int
    activo: bool
    fecha_registro:datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int | None = None