from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserResponse, Token, PasswordUpdate
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def registrar(user_data: UserCreate, db: Session = Depends(get_db)):
    return auth_service.registrar_usuario(db, user_data)

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    return auth_service.login_usuario(db, user_data.correo, user_data.password)

@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ← requiere estar autenticado
):
    return auth_service.logout_usuario(db, current_user)

@router.post("/refresh")
def refresh(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(db, body.refresh_token)

@router.get("/me", response_model=UserResponse)
def get_perfil(current_user: User = Depends(get_current_active_user)):
    return auth_service.get_perfil(current_user)

@router.put("/me", response_model=UserResponse)
def update_perfil(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return auth_service.update_perfil(db, current_user, user_data)

@router.put("/me/password")
def update_password(
    password_data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return auth_service.update_password(db, current_user, password_data)

@router.delete("/me")
def eliminar_cuenta(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return auth_service.eliminar_cuenta(db, current_user)