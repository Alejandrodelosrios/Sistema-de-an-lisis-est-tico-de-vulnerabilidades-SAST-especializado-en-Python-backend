import io
import pytest


class TestListarArchivos:

    def test_listar_archivos_proyecto_con_archivos(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        response = client.get(f"/proyectos/{proyecto_id}/archivos/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["archivos"]) >= 1

    def test_listar_archivos_proyecto_vacio(self, client, auth_headers, proyecto_sin_archivos):
        proyecto_id = proyecto_sin_archivos["id"]
        response = client.get(f"/proyectos/{proyecto_id}/archivos/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_listar_archivos_sin_token(self, client, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        response = client.get(f"/proyectos/{proyecto_id}/archivos/")
        assert response.status_code == 401

    def test_listar_archivos_proyecto_inexistente(self, client, auth_headers):
        response = client.get("/proyectos/99999/archivos/", headers=auth_headers)
        assert response.status_code in [403, 404]


class TestDetalleArchivo:

    def test_obtener_archivo_existente(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        archivos = client.get(
            f"/proyectos/{proyecto_id}/archivos/",
            headers=auth_headers
        ).json()["archivos"]
        archivo_id = archivos[0]["id"]

        response = client.get(
            f"/proyectos/{proyecto_id}/archivos/{archivo_id}/",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["id"] == archivo_id

    def test_obtener_archivo_inexistente(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        response = client.get(
            f"/proyectos/{proyecto_id}/archivos/99999/",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestEliminarArchivo:

    def test_eliminar_archivo_exitoso(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        archivos = client.get(
            f"/proyectos/{proyecto_id}/archivos/",
            headers=auth_headers
        ).json()["archivos"]
        archivo_id = archivos[0]["id"]

        response = client.delete(
            f"/proyectos/{proyecto_id}/archivos/{archivo_id}/",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_archivo_eliminado_no_aparece_en_lista(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        archivos = client.get(
            f"/proyectos/{proyecto_id}/archivos/",
            headers=auth_headers
        ).json()["archivos"]
        archivo_id = archivos[0]["id"]

        client.delete(
            f"/proyectos/{proyecto_id}/archivos/{archivo_id}/",
            headers=auth_headers
        )

        archivos_post = client.get(
            f"/proyectos/{proyecto_id}/archivos/",
            headers=auth_headers
        ).json()["archivos"]
        ids_restantes = [a["id"] for a in archivos_post]
        assert archivo_id not in ids_restantes

    def test_eliminar_archivo_sin_token(self, client, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        response = client.delete(f"/proyectos/{proyecto_id}/archivos/1/")
        assert response.status_code == 401
