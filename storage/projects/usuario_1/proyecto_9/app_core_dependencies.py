from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.security import decode_token

security = HTTPBearer()

def get_current_user(
        credentials:HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
    ) -> User:
    """esta funcion extrae y valida el token del header, luego devuelve
    el usuario actual se inyecta en cualquier endpoint que requiera
    autenticacion"""

    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "No autenticado o token inválido",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    try:
        playload = decode_token(credentials.credentials)
        user_id: str = playload.get("sub")
        token_type: str = playload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception
    except ValueError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id==int(user_id)).first()

    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)
) -> User:
    """esta funcion verifica ademas que el usuario este activo
    para usar en endpoint donde un usuario desactivado no deberia entrar"""

    if not current_user.activo:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "usuario inactivo"
        )    
    return current_user