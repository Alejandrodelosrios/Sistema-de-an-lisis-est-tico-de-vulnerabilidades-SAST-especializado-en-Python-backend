from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings

def hash_password(password: str)-> str:
    """esta funcion encripta la contraseña del usuario"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """esta funcion verifica que la cntraseña ingresada por el usuario 
    coincida con la contraseña de la base de datos"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def create_access_token(user_id: int)-> str:
    """ esta funcion crea un token de corta duracion 
    para autenticar requests"""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    playload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(playload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def create_refresh_token(user_id: int) -> str:
    """esta funcion crea un token de larga duración para renovar el access token"""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    """ esta funcion decodifica y valida un JWT, lanza excepcion si es
    invalido"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise ValueError("Token inválido o expirado")