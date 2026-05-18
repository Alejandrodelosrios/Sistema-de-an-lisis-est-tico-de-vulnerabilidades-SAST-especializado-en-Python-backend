from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# motor de conexion a la base de datos (Neon)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Sesión para interactuar con la BD
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos
Base = declarative_base()

# Dependency — se inyecta en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()