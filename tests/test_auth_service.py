import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.services.auth_service import registrar_usuario,login_usuario
from app.schemas.user import UserCreate


# ─── SEGURIDAD ───────────────────────────────────────────────

class TestSecurity:

    def test_hash_password_genera_hash(self):
        """La contraseña hasheada no debe ser igual a la original"""
        hashed = hash_password("Test123!")
        assert hashed != "Test123!"

    def test_hash_password_es_diferente_cada_vez(self):
        """Dos hashes de la misma contraseña deben ser distintos por el salt"""
        hash1 = hash_password("Test123!")
        hash2 = hash_password("Test123!")
        assert hash1 != hash2

    def test_verify_password_correcta(self):
        """Contraseña correcta debe verificar bien"""
        hashed = hash_password("Test123!")
        assert verify_password("Test123!", hashed) is True

    def test_verify_password_incorrecta(self):
        """Contraseña incorrecta no debe verificar"""
        hashed = hash_password("Test123!")
        assert verify_password("Wrongpass1!", hashed) is False

    def test_create_access_token_genera_token(self):
        """El token generado no debe estar vacío"""
        token = create_access_token(user_id=1)
        assert token is not None
        assert len(token) > 0

    def test_decode_token_devuelve_user_id(self):
        """El token decodificado debe contener el user_id correcto"""
        token = create_access_token(user_id=42)
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["type"] == "access"

    def test_decode_token_invalido_lanza_error(self):
        """Un token falso debe lanzar ValueError"""
        with pytest.raises(ValueError):
            decode_token("token.falso.aqui")


# ─── SERVICIO ────────────────────────────────────────────────

class TestAuthService:

    def test_register_crea_usuario(self, db):
        """Registrar un usuario debe guardarlo en BD"""
        user_data = UserCreate(
            nombre_completo="senku ishigami",
            correo="senku@gmail.com",
            password="Test123!"
        )
        result = registrar_usuario(db, user_data)
        assert result["access_token"] is not None
        assert result["refresh_token"] is not None

    def test_register_email_duplicado(self, db):
        """Registrar dos veces el mismo email debe fallar"""
        from fastapi import HTTPException
        user_data = UserCreate(
            nombre_completo="taiju oki",
            correo="taiju@gmail.com",
            password="Test123!"
        )
        registrar_usuario(db, user_data)

        user_data2 = UserCreate(
            nombre_completo="magma",
            correo="taiju@gmail.com",  
            password="Test123!"
        )
        with pytest.raises(HTTPException) as exc:
            registrar_usuario(db, user_data2)
        assert exc.value.status_code == 400

    def test_login_credenciales_correctas(self, db):
        """Login con credenciales correctas debe devolver tokens"""
        user_data = UserCreate(
            nombre_completo="chrome",
            correo="chrome@gmail.com",
            password="Test123!"
        )
        registrar_usuario(db, user_data)
        result = login_usuario(db, "chrome@gmail.com", "Test123!")
        assert result["access_token"] is not None
        assert result["token_type"] == "bearer"

    def test_login_password_incorrecta(self, db):
        """Login con contraseña incorrecta debe fallar con 401"""
        from fastapi import HTTPException
        user_data = UserCreate(
            nombre_completo="chrome",
            correo="chrome@gmail.com",
            password="Test123!"
        )
        registrar_usuario(db, user_data)

        with pytest.raises(HTTPException) as exc:
            login_usuario(db, "chrome@example.com", "Wrongpass1!")
        assert exc.value.status_code == 401

    def test_login_email_inexistente(self, db):
        """Login con email que no existe debe fallar con 401"""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            login_usuario(db, "drxeno@nasa.com", "Test123!")
        assert exc.value.status_code == 401