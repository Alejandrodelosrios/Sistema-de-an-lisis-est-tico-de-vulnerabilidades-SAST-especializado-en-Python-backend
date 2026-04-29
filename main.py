from fastapi import FastAPI

app = FastAPI(
    tittle="backend con fastapi",
    description = "backend para el proyecto de taller",
    version = "0.0.1"
)

@app.get("/")
def home():
    return "hola mundo"