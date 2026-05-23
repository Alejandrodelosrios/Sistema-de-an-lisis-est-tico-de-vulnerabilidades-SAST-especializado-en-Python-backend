import pytest


class TestCrearProyectoEndpoint:

   async def test_crear_proyecto_autenticado(self, client, auth_headers):
        """Crear proyecto con token válido debe devolver 201"""
        response = await client.post("/proyectos/", data={
            "nombre": "Mi Proyecto",
            "origen": "carga_directa"
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Mi Proyecto"
        assert data["origen"] == "carga_directa"

async def test_crear_proyecto_sin_token(self, client):
        """Crear proyecto sin token debe devolver 401"""
        response = await client.post("/proyectos/", data={
            "nombre": "Mi Proyecto",
            "origen": "carga_directa"
        })
        assert response.status_code == 401

async def test_crear_proyecto_sin_nombre(self, client, auth_headers):
        """Crear proyecto sin nombre debe devolver 422"""
        response = await client.post("/proyectos/", data={
            "origen": "carga_directa"
        }, headers=auth_headers)
        assert response.status_code == 422


class TestListarProyectosEndpoint:

    async def test_listar_proyectos_vacio(self, client, auth_headers):
        """Usuario sin proyectos debe recibir lista vacía"""
        response = await client.get("/proyectos", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["proyectos"] == []

    async def test_listar_proyectos_con_datos(self, client, auth_headers):
        """Después de crear un proyecto debe aparecer en la lista"""
        # Crea un proyecto
        await client.post("/proyectos/", data={
            "nombre": "Proyecto Lista",
            "origen": "carga_directa"
        }, headers=auth_headers)

        # Lista los proyectos
        response = await client.get("/proyectos", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["proyectos"][0]["nombre"] == "Proyecto Lista"

    async def test_listar_proyectos_sin_token(self, client):
        """Listar sin token debe devolver 401"""
        response = await client.get("/proyectos/")
        assert response.status_code == 401


class TestVerProyectoEndpoint:

    async def test_ver_proyecto_existente(self, client, auth_headers):
        """Ver proyecto propio debe devolver 200"""
        # Crea el proyecto
        crear = await client.post("/proyectos/", data={
            "nombre": "Ver Este",
            "origen": "carga_directa"
        }, headers=auth_headers)
        project_id = crear.json()["id"]

        # Lo consulta
        response = await client.get(f"/proyectos/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["nombre"] == "Ver Este"

    async def test_ver_proyecto_inexistente(self, client, auth_headers):
        """Ver proyecto que no existe debe devolver 404"""
        response = await client.get("/proyectos/9999", headers=auth_headers)
        assert response.status_code == 404


class TestActualizarProyectoEndpoint:

    async def test_actualizar_nombre_exitoso(self, client, auth_headers):
        """Actualizar nombre debe reflejarse en la respuesta"""
        crear = await client.post("/proyectos/", data={
            "nombre": "Nombre Viejo",
            "origen": "carga_directa"
        }, headers=auth_headers)
        project_id = crear.json()["id"]

        response = await client.put(f"/proyectos/{project_id}", data={
            "nombre": "Nombre Nuevo"
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["nombre"] == "Nombre Nuevo"

    async def test_actualizar_proyecto_inexistente(self, client, auth_headers):
        """Actualizar proyecto que no existe debe devolver 404"""
        response = await client.put("/proyectos/9999", data={
            "nombre": "No importa"
        }, headers=auth_headers)
        assert response.status_code == 404


class TestEliminarProyectoEndpoint:

    async def test_eliminar_proyecto_exitoso(self, client, auth_headers):
        """Eliminar proyecto debe devolver mensaje de confirmación"""
        crear = await client.post("/proyectos/", data={
            "nombre": "Eliminar Este",
            "origen": "carga_directa"
        }, headers=auth_headers)
        project_id = crear.json()["id"]

        response = await client.delete(f"/proyectos/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        assert "message" in response.json()

    async def test_eliminar_proyecto_no_aparece_en_lista(self, client, auth_headers):
        """Proyecto eliminado no debe aparecer en el listado"""
        crear = await client.post("/proyectos/", data={
            "nombre": "Por Eliminar",
            "origen": "carga_directa"
        }, headers=auth_headers)
        project_id = crear.json()["id"]

        # Elimina
        await client.delete(f"/proyectos/{project_id}", headers=auth_headers)

        # Verifica que no aparece
        lista = await client.get("/proyectos", headers=auth_headers)
        assert lista.json()["total"] == 0

    async def test_eliminar_proyecto_inexistente(self, client, auth_headers):
        """Eliminar proyecto que no existe debe devolver 404"""
        response = await client.delete("/proyectos/9999", headers=auth_headers)
        assert response.status_code == 404