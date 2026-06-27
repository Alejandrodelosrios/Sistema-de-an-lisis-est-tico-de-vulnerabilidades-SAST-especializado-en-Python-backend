from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.feedback import Opinion, RespuestaEncuesta


def listar_opiniones(db: Session) -> list[Opinion]:
    return db.query(Opinion).order_by(Opinion.creado_en.desc()).all()


def metricas_opiniones(db: Session) -> dict:
    """Coincide con schemas.feedback.MetricasOpinionesResponse"""
    total = db.query(func.count(Opinion.id)).scalar() or 0
    promedio = db.query(func.avg(Opinion.calificacion)).scalar() or 0
    pendientes = db.query(func.count(Opinion.id)).filter(Opinion.revisada == 0).scalar() or 0
    revisadas = total - pendientes

    por_categoria_query = (
        db.query(Opinion.categoria, func.count(Opinion.id))
        .group_by(Opinion.categoria)
        .all()
    )
    por_categoria = {
        (cat.value if hasattr(cat, "value") else cat): cnt
        for cat, cnt in por_categoria_query
    }

    return {
        "total_opiniones": total,
        "promedio_calificacion": round(float(promedio), 2),
        "pendientes": pendientes,
        "revisadas": revisadas,
        "por_categoria": por_categoria,
    }


def listar_encuestas(db: Session) -> list[RespuestaEncuesta]:
    return db.query(RespuestaEncuesta).order_by(RespuestaEncuesta.creado_en.desc()).all()


def metricas_encuesta(db: Session) -> dict:
    """Coincide con schemas.feedback.MetricasEncuestaResponse"""
    q = db.query(RespuestaEncuesta)
    total = q.count()

    def promedio(campo):
        valor = db.query(func.avg(campo)).scalar()
        return round(float(valor), 2) if valor is not None else 0.0

    aprendieron = q.filter(RespuestaEncuesta.aprendio_algo_nuevo == "si").count()
    porcentaje_aprendio = round((aprendieron / total) * 100, 1) if total else 0.0

    return {
        "total_respuestas": total,
        "promedio_facilidad_carga": promedio(RespuestaEncuesta.facilidad_carga),
        "promedio_relevancia_vulnerabilidades": promedio(RespuestaEncuesta.relevancia_vulnerabilidades),
        "promedio_claridad_explicaciones": promedio(RespuestaEncuesta.claridad_explicaciones),
        "promedio_claridad_recomendaciones": promedio(RespuestaEncuesta.claridad_recomendaciones),
        "promedio_intuitividad_dashboard": promedio(RespuestaEncuesta.intuitividad_dashboard),
        "promedio_nps": promedio(RespuestaEncuesta.nps),
        "porcentaje_aprendio_algo_nuevo": porcentaje_aprendio,
    }