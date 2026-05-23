import io
import pytest


class TestEjecutarAnalisis:

    def test_ejecutar_analisis_carga_directa(self, client, auth_headers, proyecto_carga_directa):
        """El archivo tiene os.system y password hardcodeada — debe detectar vulnerabilidades."""
        proyecto_id = proyecto_carga_directa["id"]
        response = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "score_seguridad" in data
        assert data["score_seguridad"] >= 0.0
        assert data["score_seguridad"] <= 100.0
        assert "vulnerabilidades" in data
        assert len(data["vulnerabilidades"]) > 0

    def test_analisis_detecta_vulnerabilidades_correctas(self, client, auth_headers, proyecto_carga_directa):
        """Verifica que detecta os.system (A03) y password hardcodeada (A07)."""
        proyecto_id = proyecto_carga_directa["id"]
        response = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        )
        assert response.status_code == 201
        vulns = response.json()["vulnerabilidades"]
        tipos = [v["tipo_owasp"] for v in vulns]
        assert any("A03" in t for t in tipos)
        assert any("A07" in t for t in tipos)

    def test_analisis_score_menor_100_con_vulnerabilidades(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        response = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        )
        assert response.status_code == 201
        assert response.json()["score_seguridad"] < 100.0

    def test_ejecutar_analisis_proyecto_sin_archivos(self, client, auth_headers, proyecto_sin_archivos):
        proyecto_id = proyecto_sin_archivos["id"]
        response = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        )
        assert response.status_code == 400

    def test_ejecutar_analisis_sin_token(self, client, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        response = client.post(f"/proyectos/{proyecto_id}/analisis/")
        assert response.status_code == 401

    def test_ejecutar_analisis_proyecto_inexistente(self, client, auth_headers):
        response = client.post("/proyectos/99999/analisis/", headers=auth_headers)
        assert response.status_code == 404


class TestListarAnalisis:

    def test_listar_analisis_vacio(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        response = client.get(f"/proyectos/{proyecto_id}/analisis/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "analisis" in data

    def test_listar_analisis_despues_de_ejecutar(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        client.post(f"/proyectos/{proyecto_id}/analisis/", headers=auth_headers)

        response = client.get(f"/proyectos/{proyecto_id}/analisis/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_listar_analisis_sin_token(self, client, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        response = client.get(f"/proyectos/{proyecto_id}/analisis/")
        assert response.status_code == 401


class TestDetalleAnalisis:

    def test_obtener_analisis_existente(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        analisis_id = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        ).json()["id"]

        response = client.get(
            f"/proyectos/{proyecto_id}/analisis/{analisis_id}/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == analisis_id
        assert "vulnerabilidades" in data

    def test_obtener_analisis_inexistente(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        response = client.get(
            f"/proyectos/{proyecto_id}/analisis/99999/",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_no_acceder_analisis_de_otro_proyecto(self, client, auth_headers, proyecto_carga_directa, proyecto_sin_archivos):
        """Un análisis del proyecto A no debe ser accesible desde el proyecto B."""
        proyecto_id = proyecto_carga_directa["id"]
        otro_proyecto_id = proyecto_sin_archivos["id"]

        analisis_id = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        ).json()["id"]

        response = client.get(
            f"/proyectos/{otro_proyecto_id}/analisis/{analisis_id}/",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestVulnerabilidades:

    def test_listar_vulnerabilidades_de_analisis(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        analisis_id = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        ).json()["id"]

        response = client.get(
            f"/proyectos/{proyecto_id}/analisis/{analisis_id}/vulnerabilidades/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "vulnerabilidades" in data
        assert data["total"] > 0

    def test_resumen_por_severidad(self, client, auth_headers, proyecto_carga_directa):
        proyecto_id = proyecto_carga_directa["id"]
        analisis_id = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        ).json()["id"]

        response = client.get(
            f"/proyectos/{proyecto_id}/analisis/{analisis_id}/vulnerabilidades/resumen/severidad/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "critica" in data
        assert "alta" in data
        assert "media" in data
        assert "baja" in data
        assert "total" in data
