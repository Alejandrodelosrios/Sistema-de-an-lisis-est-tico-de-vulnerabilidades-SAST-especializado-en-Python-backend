from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import auth, project, file, analysis, vulnerability
from fastapi.middleware.cors import CORSMiddleware


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

origins = [
    "https://sistema-de-an-lisis-est-tico-de-vul.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(file.router)
app.include_router(analysis.router)
app.include_router(vulnerability.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "API funcionando"}