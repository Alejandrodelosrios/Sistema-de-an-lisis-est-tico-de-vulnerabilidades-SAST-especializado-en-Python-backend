"""
Ejemplo: cómo capturar la IP del cliente en cualquier endpoint
y pasarla a registrar_actividad().
"""

from fastapi import Request, Depends
from sqlalchemy.orm import Session


def obtener_ip_cliente(request: Request) -> str:
    """
    Obtiene la IP real del cliente. Si la app está detrás de un proxy/load
    balancer (Render, Railway, Vercel, etc.), la IP real viene en el header
    'X-Forwarded-For'; si no, se usa request.client.host directamente.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # x-forwarded-for puede traer varias IPs separadas por coma;
        # la primera es la del cliente original.
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "desconocida"