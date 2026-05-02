import pytest


class TestCrearProyectoEndpoint:

    def test_crear_proyecto_autenticado(self, client, auth_headers):
        """Crear proyecto con token válido debe devolver 201"""
        response = client.post("/proyectos/", json={
            "nombre": "Mi Proyecto",
            "origen": "carga_directa"
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Mi Proyecto"
        assert data["origen"] == "carga_directa"

    def test_crear_proyecto_sin_token(self, client):
        """Crear proyecto sin token debe devolver 401"""
        response = client.post("/proyectos/", json={
            "nombre": "Mi Proyecto",
            "origen": "carga_directa"
        })
        assert response.status_code == 401

    def test_crear_proyecto_sin_nombre(self, client, auth_headers):
        """Crear proyecto sin nombre debe devolver 422"""
        response = client.post("/proyectos/", json={
            "origen": "carga_directa"
        }, headers=auth_headers)
        assert response.status_code == 422


class TestListarProyectosEndpoint:

    def test_listar_proyectos_vacio(self, client, auth_headers):
        """Usuario sin proyectos debe recibir lista vacía"""
        response = client.get("/proyectos", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["proyectos"] == []

    def test_listar_proyectos_con_datos(self, client, auth_headers):
        """Después de crear un proyecto debe aparecer en la lista"""
        # Crea un proyecto
        client.post("/proyectos/", json={
            "nombre": "Proyecto Lista",
            "origen": "carga_directa"
        }, headers=auth_headers)

        # Lista los proyectos
        response = client.get("/proyectos", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["proyectos"][0]["nombre"] == "Proyecto Lista"

    def test_listar_proyectos_sin_token(self, client):
        """Listar sin token debe devolver 401"""
        response = client.get("/proyectos/")
        assert response.status_code == 401


class TestVerProyectoEndpoint:

    def test_ver_proyecto_existente(self, client, auth_headers):
        """Ver proyecto propio debe devolver 200"""
        # Crea el proyecto
        crear = client.post("/proyectos/", json={
            "nombre": "Ver Este",
            "origen": "carga_directa"
        }, headers=auth_headers)
        project_id = crear.json()["id"]

        # Lo consulta
        response = client.get(f"/proyectos/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["nombre"] == "Ver Este"

    def test_ver_proyecto_inexistente(self, client, auth_headers):
        """Ver proyecto que no existe debe devolver 404"""
        response = client.get("/proyectos/9999", headers=auth_headers)
        assert response.status_code == 404


class TestActualizarProyectoEndpoint:

    def test_actualizar_nombre_exitoso(self, client, auth_headers):
        """Actualizar nombre debe reflejarse en la respuesta"""
        crear = client.post("/proyectos/", json={
            "nombre": "Nombre Viejo",
            "origen": "carga_directa"
        }, headers=auth_headers)
        project_id = crear.json()["id"]

        response = client.put(f"/proyectos/{project_id}", json={
            "nombre": "Nombre Nuevo"
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["nombre"] == "Nombre Nuevo"

    def test_actualizar_proyecto_inexistente(self, client, auth_headers):
        """Actualizar proyecto que no existe debe devolver 404"""
        response = client.put("/proyectos/9999", json={
            "nombre": "No importa"
        }, headers=auth_headers)
        assert response.status_code == 404


class TestEliminarProyectoEndpoint:

    def test_eliminar_proyecto_exitoso(self, client, auth_headers):
        """Eliminar proyecto debe devolver mensaje de confirmación"""
        crear = client.post("/proyectos/", json={
            "nombre": "Eliminar Este",
            "origen": "carga_directa"
        }, headers=auth_headers)
        project_id = crear.json()["id"]

        response = client.delete(f"/proyectos/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        assert "message" in response.json()

    def test_eliminar_proyecto_no_aparece_en_lista(self, client, auth_headers):
        """Proyecto eliminado no debe aparecer en el listado"""
        crear = client.post("/proyectos/", json={
            "nombre": "Por Eliminar",
            "origen": "carga_directa"
        }, headers=auth_headers)
        project_id = crear.json()["id"]

        # Elimina
        client.delete(f"/proyectos/{project_id}", headers=auth_headers)

        # Verifica que no aparece
        lista = client.get("/proyectos", headers=auth_headers)
        assert lista.json()["total"] == 0

    def test_eliminar_proyecto_inexistente(self, client, auth_headers):
        """Eliminar proyecto que no existe debe devolver 404"""
        response = client.delete("/proyectos/9999", headers=auth_headers)
        assert response.status_code == 404