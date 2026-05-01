from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, PasswordUpdate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

def registrar_usuario(db: Session, user_create: UserCreate) -> dict:
    """esta funcion registra un nuevo usuario y lo retorna"""
    existe_correo = db.query(User).filter(User.correo == user_create.correo).first()
    if existe_correo:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "El correo ya esta registrado"
        )
    nuevo_usuario = User(
        nombre_completo=user_create.nombre_completo,
        correo= user_create.correo,
        password=hash_password(user_create.password)
        )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    access_token  = create_access_token(nuevo_usuario.id)
    refresh_token = create_refresh_token(nuevo_usuario.id)
    nuevo_usuario.refresh_token = refresh_token
    db.commit()     
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }    

def login_usuario(db:Session, correo: str, password: str)->dict:
    """esta funcion autentica al usuario y 
    retorna los tokens de acceso y refresh"""
    error_generico = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas"
    )

    usuario = db.query(User).filter(User.correo == correo).first()
    if not usuario:
        raise error_generico
    if not verify_password(password, usuario.password):
        raise error_generico
    if not usuario.activo:
       raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta cuenta ha sido eliminada"
        ) 
    
    access_token = create_access_token(usuario.id)
    refresh_token = create_refresh_token(usuario.id)
    
    usuario.refresh_token = refresh_token
    db.commit()
    return{
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
        }

def logout_usuario(db:Session, current_user: User) ->dict:
    """Esta funcion permite al usuario cerrar sesión y 
    revocar el token de refresco
    """
    current_user.refresh_token = None
    db.commit()
    return {"message": "Sesión cerrada exitosamente"}

def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """ esta funcion permite renovar 
    el access token usando un refresh token válido"""
    try: 
        playload = decode_token(refresh_token)
        if playload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    usuario_id =int(playload.get("sub"))
    usuario = db.query(User).filter(User.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    if usuario.refresh_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada, inicia sesión nuevamente"
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta cuenta ha sido eliminada"
        )
    
    return {
        "access_token": create_access_token(usuario_id),
        "token_type": "bearer"
    }

def get_perfil(current_user: User)-> User:
    """esta funcion retorna el perfil del usuario actual"""
    return current_user

def update_perfil(db: Session, current_user: User, user_data: UserUpdate) -> User:
    """esta funcion actualiza el perfil del usuario 
    actual con los datos proporcionados"""
    if user_data.correo and user_data.correo != current_user.correo: 
        existe_correo = db.query(User).filter(User.correo == user_data.correo).first()
        if existe_correo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
    if user_data.nombre_completo is not None:
        current_user.nombre_completo = user_data.nombre_completo

    if user_data.correo is not None:
        current_user.correo = user_data.correo

    db.commit()
    db.refresh(current_user)
    return current_user

def update_password(db: Session, current_user: User, password_data: PasswordUpdate) -> dict:
    """esta funcion permite al usuario actualizar su contraseña"""
    if not verify_password(password_data.current_password,current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )
    
    if verify_password(password_data.new_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser diferente a la actual"
        )
    current_user.hashed_password = hash_password(password_data.new_password)
    current_user.refresh_token = None
    db.commit()




def eliminar_cuenta(db:Session, current_user: User)-> dict:
    """esta funcion elimina la cuenta del usuario actual"""
    current_user.activo= False
    current_user.refresh_token = None
    db.commit()
    return {"message": "Cuenta eliminada exitosamente"}
