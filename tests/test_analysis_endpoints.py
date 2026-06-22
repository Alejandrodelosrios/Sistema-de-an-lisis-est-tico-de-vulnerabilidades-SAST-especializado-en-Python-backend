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

    def test_vulnerabilidad_genera_recomendacion_automatica(self, client, auth_headers, proyecto_carga_directa, db):
        """Verifica que al crear una vulnerabilidad se genera automáticamente su recomendación asociada."""
        proyecto_id = proyecto_carga_directa["id"]
        
        # Ejecutar análisis que cree vulnerabilidades
        response = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        )
        assert response.status_code == 201
        vulns_data = response.json()["vulnerabilidades"]
        assert len(vulns_data) > 0
        
        # Verificar que cada vulnerabilidad tiene recomendaciones asociadas
        for vuln in vulns_data:
            assert "recomendaciones" in vuln
            assert isinstance(vuln["recomendaciones"], list)
            assert len(vuln["recomendaciones"]) > 0
            
            # Verificar que la recomendación tiene los campos esperados
            for recom in vuln["recomendaciones"]:
                assert "id" in recom
                assert "titulo" in recom
                assert "explicacion_riesgo" in recom
                assert "fecha_creacion" in recom
                # El código corregido ejemplo puede ser None
                assert "codigo_corregido_ejemplo" in recom


class TestHistorial:

    def test_get_project_history_vacio(self, client, auth_headers, proyecto_carga_directa):
        """Proyecto sin análisis debe devolver historial vacío."""
        proyecto_id = proyecto_carga_directa["id"]
        response = client.get(
            f"/proyectos/{proyecto_id}/history/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "historial" in data
        assert data["total"] == 0

    def test_get_project_history_un_analisis(self, client, auth_headers, proyecto_carga_directa):
        """Proyecto con un solo análisis debe devolver historial con un elemento."""
        proyecto_id = proyecto_carga_directa["id"]
        
        # Crear un análisis
        analisis_resp = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        )
        assert analisis_resp.status_code == 201
        analisis_data = analisis_resp.json()
        
        # Consultar historial
        response = client.get(
            f"/proyectos/{proyecto_id}/history/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["historial"]) == 1
        
        item = data["historial"][0]
        assert item["id"] == analisis_data["id"]
        assert item["score_seguridad"] == analisis_data["score_seguridad"]
        assert "fecha_ejecucion" in item
        assert "vulnerabilidades_por_severidad" in item
        
        # Verificar que el conteo de severidades es correcto
        sumario = item["vulnerabilidades_por_severidad"]
        assert "critica" in sumario
        assert "alta" in sumario
        assert "media" in sumario
        assert "baja" in sumario
        assert "total" in sumario
        assert sumario["total"] == len(analisis_data["vulnerabilidades"])

    def test_get_project_history_multiples_analisis_orden_descendente(self, client, auth_headers, proyecto_carga_directa):
        """Verifica que el historial devuelve análisis ordenados por fecha descendente."""
        proyecto_id = proyecto_carga_directa["id"]
        
        # Crear 3 análisis
        ids = []
        for i in range(3):
            resp = client.post(
                f"/proyectos/{proyecto_id}/analisis/",
                headers=auth_headers
            )
            assert resp.status_code == 201
            ids.append(resp.json()["id"])
        
        # Consultar historial
        response = client.get(
            f"/proyectos/{proyecto_id}/history/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["historial"]) == 3
        
        # Verificar orden descendente (último análisis primero)
        historial_ids = [item["id"] for item in data["historial"]]
        assert historial_ids == list(reversed(ids))

    def test_get_project_history_conteo_severidades_correcto(self, client, auth_headers, proyecto_carga_directa):
        """Verifica que el conteo de vulnerabilidades por severidad es correcto."""
        proyecto_id = proyecto_carga_directa["id"]
        
        # Crear un análisis
        analisis_resp = client.post(
            f"/proyectos/{proyecto_id}/analisis/",
            headers=auth_headers
        )
        assert analisis_resp.status_code == 201
        analisis_data = analisis_resp.json()
        
        # Contar vulnerabilidades por severidad en el análisis
        conteo_analisis = {
            "critica": 0,
            "alta": 0,
            "media": 0,
            "baja": 0
        }
        for vuln in analisis_data["vulnerabilidades"]:
            severidad = vuln["severidad"]
            if severidad in conteo_analisis:
                conteo_analisis[severidad] += 1
        
        # Consultar historial
        response = client.get(
            f"/proyectos/{proyecto_id}/history/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        sumario = data["historial"][0]["vulnerabilidades_por_severidad"]
        assert sumario["critica"] == conteo_analisis["critica"]
        assert sumario["alta"] == conteo_analisis["alta"]
        assert sumario["media"] == conteo_analisis["media"]
        assert sumario["baja"] == conteo_analisis["baja"]

    def test_get_project_history_sin_autenticacion(self, client, proyecto_carga_directa):
        """Debe devolver 401 si no hay usuario autenticado."""
        proyecto_id = proyecto_carga_directa["id"]
        response = client.get(f"/proyectos/{proyecto_id}/history/")
        assert response.status_code == 401

    def test_get_project_history_proyecto_inexistente(self, client, auth_headers):
        """Debe devolver 404 si el proyecto no existe."""
        response = client.get("/proyectos/99999/history/", headers=auth_headers)
        assert response.status_code == 404
