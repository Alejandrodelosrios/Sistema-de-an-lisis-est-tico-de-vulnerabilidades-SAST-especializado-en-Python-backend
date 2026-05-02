from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import auth,project

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas")
    yield
    print("🛑 Cerrando aplicación")

app = FastAPI(
    title="SAST API",
    description="Sistema de análisis estático de vulnerabilidades",
    version="1.0.1",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(project.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "API funcionando"}