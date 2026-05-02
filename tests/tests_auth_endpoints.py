class TestRegisterEndpoint:

    def test_register_exitoso(self, client,db):
        """Registro exitoso debe devolver tokens"""
        response = client.post("/auth/register", json={
            "nombre_completo": "newuser",
            "correo": "new@example.com",
            "password": "Test123!"
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_register_password_sin_mayuscula(self, client):
        """Contraseña sin mayúscula debe devolver 422"""
        response = client.post("/auth/register", json={
            "nombre_completo": "user",
            "correo": "user@example.com",
            "password": "test123!"   # sin mayúscula
        })
        assert response.status_code == 422

    def test_register_password_corta(self, client):
        """Contraseña menor a 8 caracteres debe devolver 422"""
        response = client.post("/auth/register", json={
            "nombre_completo": "user",
            "correo": "user@example.com",
            "password": "Ab1!"   # menos de 8
        })
        assert response.status_code == 422

    def test_register_email_invalido(self, client):
        """Email con formato incorrecto debe devolver 422"""
        response = client.post("/auth/register", json={
            "nombre_completo": "user",
            "correo": "estonoesuncorreo",
            "password": "Test123!"
        })
        assert response.status_code == 422


class TestLoginEndpoint:

    def test_login_exitoso(self, client, registered_user):
        """Login correcto debe devolver tokens"""
        response = client.post("/auth/login", json={
            "correo": "test@example.com",
            "password": "Test123!"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_credenciales_incorrectas(self, client, registered_user):
        """Login con datos incorrectos debe devolver 401"""
        response = client.post("/auth/login", json={
            "correo": "test@example.com",
            "password": "Wrongpass1!"
        })
        assert response.status_code == 401


class TestProtectedEndpoints:

    def test_get_perfil_autenticado(self, client, auth_headers):
        """Con token válido debe devolver el perfil"""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["correo"] == "test@example.com"

    def test_get_perfil_sin_token(self, client):
        """Sin token debe devolver 403"""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_logout_exitoso(self, client, registered_user, auth_headers):
        """Logout debe cerrar sesión correctamente"""
        response = client.post(
            "/auth/logout",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Sesión cerrada exitosamente"

    def test_update_perfil(self, client, auth_headers):
        """Actualizar nombre_completo debe reflejarse en el perfil"""
        response = client.put("/auth/me", json={
            "nombre_completo": "Updated User"
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["nombre_completo"] == "Updated User"