from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.activity_log import AccionEnum
from app.models.user import RolEnum, User
from app.schemas.user import UserCreate, UserUpdate, PasswordUpdate
from app.core.config import settings
from app.core.security import (

    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.services.activity_service import registrar_actividad

def registrar_usuario(db: Session, user_create: UserCreate,ip:str) -> dict:
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
        password=hash_password(user_create.password),
        rol=RolEnum.estudiante
        )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    access_token  = create_access_token(nuevo_usuario.id,nuevo_usuario.rol)
    refresh_token = create_refresh_token(nuevo_usuario.id)
    nuevo_usuario.refresh_token = refresh_token
    db.commit()
    registrar_actividad(db, nuevo_usuario.id, AccionEnum.registro,ip_origen=ip)     
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }    

def login_usuario(db:Session, correo: str, password: str,ip:str)->dict:
    """esta funcion autentica al usuario y 
    retorna los tokens de acceso y refresh"""
    error_generico = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas"
    )

    usuario = db.query(User).filter(User.correo == correo).first()
    if not usuario:
        raise error_generico
    
    if not usuario.activo:
       raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta cuenta ha sido eliminada"
        ) 
    if not verify_password(password, usuario.password):
        raise error_generico
    
    access_token = create_access_token(usuario.id, usuario.rol)
    refresh_token = create_refresh_token(usuario.id)
    
    usuario.refresh_token = refresh_token
    db.commit()
    registrar_actividad(db,usuario.id, AccionEnum.login,ip_origen=ip)
    return{
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
        }

def logout_usuario(db:Session, current_user: User,ip:str) ->dict:
    """Esta funcion permite al usuario cerrar sesión y 
    revocar el token de refresco
    """
    current_user.refresh_token = None
    db.commit()
    registrar_actividad(db, current_user.id, AccionEnum.logout,ip_origen=ip)
    return {"message": "Sesión cerrada exitosamente"}

def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """ esta funcion permite renovar 
    el access token usando un refresh token válido"""
    try: 
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    usuario_id =int(payload.get("sub"))
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
        "access_token": create_access_token(usuario_id, usuario.rol),
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
    current_user.password = hash_password(password_data.new_password)
    current_user.refresh_token = None

    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo actualizar la base de datos"
        )
            
    return {"status": "success", "message": "Contraseña actualizada exitosamente"}

def eliminar_cuenta(db:Session, current_user: User)-> dict:
    """esta funcion elimina la cuenta del usuario actual"""
    current_user.activo= False
    current_user.refresh_token = None
    db.commit()
    return {"message": "Cuenta eliminada exitosamente"}

def crear_superadmin_inicial(db: Session) -> None:
    """
    Crea el SuperAdmin inicial únicamente si no existe.
    Esta función debe ejecutarse al iniciar la aplicación.
    """

    superadmin = (
        db.query(User)
        .filter(User.rol == RolEnum.superadmin)
        .first()
    )

    if superadmin:
        print("ℹ️ El SuperAdmin ya existe.")
        return

    nuevo_superadmin = User(
        nombre_completo=settings.SUPERADMIN_NOMBRE,
        correo=settings.SUPERADMIN_EMAIL,
        password=hash_password(settings.SUPERADMIN_PASSWORD),
        rol=RolEnum.superadmin,
        activo=True
    )

    db.add(nuevo_superadmin)
    db.commit()
    db.refresh(nuevo_superadmin)

    refresh_token = create_refresh_token(nuevo_superadmin.id)
    nuevo_superadmin.refresh_token = refresh_token

    db.commit()

    print("✅ SuperAdmin inicial creado correctamente.")

    