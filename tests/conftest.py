import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

# Base de datos en memoria solo para pruebas
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

# Crea las tablas en la BD de pruebas
Base.metadata.create_all(bind=engine_test)

# Reemplaza get_db para que use la BD de pruebas
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Cliente HTTP para hacer requests a los endpoints
@pytest.fixture
def client():
    return TestClient(app)

# Base de datos limpia para cada prueba
@pytest.fixture
def db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# Usuario de prueba ya registrado
@pytest.fixture
def registered_user(client):
    response = client.post("/auth/register", json={
        "nombre_completo": "testuser",
        "correo": "test@example.com",
        "password": "Test123!"
    })
    return response.json()

# Fixture que devuelve el header con el token listo
@pytest.fixture
def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['access_token']}"}