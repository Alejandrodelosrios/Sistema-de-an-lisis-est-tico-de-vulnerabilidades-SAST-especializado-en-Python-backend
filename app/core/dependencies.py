from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import RolEnum, User
from app.core.security import decode_token

security = HTTPBearer()

def get_current_user(
        credentials:HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
    ) -> User:
    """esta funcion extrae y valida el token del header, luego devuelve
    el usuario actual se inyecta en cualquier endpoint que requiera
    autenticacion"""

    auth_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "No autenticado o token inválido",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        rol: str = payload.get("rol")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise auth_exception
    except ValueError:
        raise auth_exception
    
    user = db.query(User).filter(User.id==int(user_id)).first()

    if user is None:
        raise auth_exception

    if not user.activo:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "usuario inactivo"
        )    
    
    return user

def require_superadmin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Permite acceder únicamente a usuarios con rol SuperAdmin.
    """

    if current_user.rol != RolEnum.superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción."
        )

    return current_user