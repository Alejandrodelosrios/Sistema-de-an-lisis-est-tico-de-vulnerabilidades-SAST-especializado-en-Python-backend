import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture                        # ← limpia la BD antes de cada prueba
def db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def registered_user(client, db):      # ← ahora depende de db limpia
    response = client.post("/auth/register", json={
        "nombre_completo": "Test User",
        "correo": "test@example.com",
        "password": "Test123!"
    })
    data = response.json()
    assert "access_token" in data, f"Registro falló: {data}"
    return data

@pytest.fixture
def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['access_token']}"}


import io
from app.models.project import Project, OrigenEnum
from app.models.file import File
from app.models.analysis import Analysis
from app.models.vulnerability import Vulnerability, SeveridadEnum

@pytest.fixture
def proyecto_carga_directa(db, registered_user, auth_headers, client):
    """Crea un proyecto de carga directa con un archivo .py subido."""
    archivo_contenido = b"import os\nos.system('ls')\npassword = 'secreto123'\n"
    response = client.post(
        "/proyectos/",
        data={"nombre": "Proyecto Test", "origen": "carga_directa"},
        files={"files": ("test_vuln.py", io.BytesIO(archivo_contenido), "text/x-python")},
        headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def proyecto_sin_archivos(db, registered_user, auth_headers, client):
    """Proyecto con archivo subido pero luego eliminado — simula proyecto vacío."""
    archivo = b"x = 1\n"
    response = client.post(
        "/proyectos/",
        data={"nombre": "Proyecto Vacío", "origen": "carga_directa"},
        files={"files": ("dummy.py", io.BytesIO(archivo), "text/x-python")},
        headers=auth_headers
    )
    assert response.status_code == 201
    proyecto = response.json()

    # Eliminar el archivo para dejar el proyecto sin archivos activos
    archivos = client.get(
        f"/proyectos/{proyecto['id']}/archivos/",
        headers=auth_headers
    ).json()["archivos"]
    for archivo in archivos:
        client.delete(
            f"/proyectos/{proyecto['id']}/archivos/{archivo['id']}/",
            headers=auth_headers
        )

    return proyecto


@pytest.fixture
def proyecto_github(db, registered_user, auth_headers, client, mocker):
    """Crea un proyecto GitHub con mock de la API."""
    # Mock de cargar_desde_github para no hacer requests reales
    mocker.patch(
        "app.services.file_service.cargar_desde_github",
        return_value={"total": 2, "archivos": []}
    )
    response = client.post(
        "/proyectos/",
        data={
            "nombre": "Proyecto GitHub Test",
            "origen": "github",
            "url_github": "https://github.com/usuario/repo-test"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()