from sqlalchemy.orm import Session
from app.models.activity_log import RegistroActividad, AccionEnum


def registrar_actividad(
    db: Session,
    usuario_id: int,
    accion: AccionEnum,
    proyecto_id: int | None = None,
    detalle: str | None = None,
    ip_origen: str | None = None,
) -> None:
    """
    Llamar a esta función dentro de los servicios existentes,
    justo después de la acción real. Ejemplos de dónde insertarla:

    - auth_service.registrar_usuario()      -> AccionEnum.registro
    - auth_service.login_usuario()          -> AccionEnum.login
    - project_service.crear_proyecto()      -> AccionEnum.proyecto_creado
    - analysis_service.ejecutar_analisis()  -> AccionEnum.analisis_ejecutado
    - opinion (router) al crear opinión     -> AccionEnum.opinion_enviada
    - encuesta (router) al responder        -> AccionEnum.encuesta_respondida
    """
    log = RegistroActividad(
        usuario_id=usuario_id,
        proyecto_id=proyecto_id,
        accion=accion,
        detalle=detalle,
        ip_origen=ip_origen,
    )
    db.add(log)
    db.commit()


# Ejemplo de uso dentro de login_usuario() en auth_service.py:
#
# from app.services.activity_service import registrar_actividad
# from app.models.activity_log import AccionEnum
#
# def login_usuario(db, correo, password):
#     ...
#     usuario.refresh_token = refresh_token
#     db.commit()
#     registrar_actividad(db, usuario.id, AccionEnum.login)
#     return {...}