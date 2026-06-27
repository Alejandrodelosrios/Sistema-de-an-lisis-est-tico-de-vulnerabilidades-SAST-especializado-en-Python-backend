from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User, RolEnum
from app.models.activity_log import RegistroActividad
from app.models.project import Project


def resumen_actividad_usuarios(db: Session) -> list[dict]:
    """
    Para la tabla 'Usuarios y su actividad' del dashboard del superadmin.
    Una fila por estudiante con su evidencia de uso resumida.
    """
    estudiantes = db.query(User).filter(User.rol == RolEnum.estudiante).all()
    resultado = []

    for u in estudiantes:
        total_proyectos = db.query(func.count(Project.id)).filter(
            Project.usuario_id == u.id
        ).scalar() or 0

        ultimo_login = (
            db.query(func.max(RegistroActividad.creado_en))
            .filter(RegistroActividad.usuario_id == u.id,
                     RegistroActividad.accion == "login")
            .scalar()
        )

        total_analisis = db.query(func.count(RegistroActividad.id)).filter(
            RegistroActividad.usuario_id == u.id,
            RegistroActividad.accion == "analisis_ejecutado"
        ).scalar() or 0

        dejo_opinion = db.query(func.count(RegistroActividad.id)).filter(
            RegistroActividad.usuario_id == u.id,
            RegistroActividad.accion == "opinion_enviada"
        ).scalar() > 0

        resultado.append({
            "usuario_id": u.id,
            "nombre_completo": u.nombre_completo,
            "correo": u.correo,
            "fecha_registro": u.fecha_registro,
            "ultimo_login": ultimo_login,
            "total_proyectos": total_proyectos,
            "total_analisis": total_analisis,
            "dejo_opinion": dejo_opinion,
        })

    return resultado


def timeline_usuario(db: Session, usuario_id: int) -> list[dict]:
    """Bitácora cronológica de un usuario específico (para el detalle)."""
    eventos = (
        db.query(RegistroActividad)
        .filter(RegistroActividad.usuario_id == usuario_id)
        .order_by(RegistroActividad.creado_en.asc())
        .all()
    )
    return [
        {
            "accion": e.accion.value if hasattr(e.accion, "value") else e.accion,
            "detalle": e.detalle,
            "proyecto_id": e.proyecto_id,
            "fecha": e.creado_en,
        }
        for e in eventos
    ]