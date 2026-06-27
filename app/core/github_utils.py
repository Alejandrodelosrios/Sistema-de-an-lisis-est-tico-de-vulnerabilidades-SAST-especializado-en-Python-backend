from fastapi import HTTPException, status
import httpx
from app.core.config import settings


def github_headers() -> dict:
    """
    Headers para llamadas a api.github.com. Si hay GITHUB_TOKEN configurado,
    el límite sube de 60 a 5000 requests/hora.
    """
    headers = {"Accept": "application/vnd.github+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    return headers


def verificar_rate_limit(response: httpx.Response) -> None:
    """
    Detecta explícitamente si GitHub nos bloqueó por rate limit, en vez de
    dejar que el código siga como si el repo estuviera vacío o limpio.
    Llamar esto justo después de cada request a api.github.com.
    """
    restante = response.headers.get("x-ratelimit-remaining")
    if response.status_code == 403 and restante == "0":
        reset = response.headers.get("x-ratelimit-reset")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Se alcanzó el límite de peticiones a la API de GitHub. "
                "Configura GITHUB_TOKEN en el .env para subir el límite a 5000/hora, "
                f"o esperá unos minutos (reset: {reset})."
            )
        )