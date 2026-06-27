import httpx
from app.models.activity_log import AccionEnum
from app.services.activity_service import registrar_actividad
import app.services.file_service as file_service
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.analysis import Analysis
from app.models.vulnerability import Vulnerability, SeveridadEnum
from app.models.recommendation import Recommendation
from app.models.project import Project, OrigenEnum
from app.models.user import User
from app.models.file import File
from app.services.motor_ast import analizar_contenido
from app.services.recommendation_service import obtener_recomendacion
from app.core.github_utils import github_headers, verificar_rate_limit

def _verificar_proyecto_usuario(db: Session, proyecto_id: int, current_user: User) -> Project:
    """
    Verifica que el proyecto existe, está activo y pertenece al usuario actual.
    
    Args:
        db: Sesión de base de datos
        proyecto_id: ID del proyecto a verificar
        current_user: Usuario autenticado
        
    Returns:
        Objeto Project si existe y pertenece al usuario
        
    Raises:
        HTTPException 404 si el proyecto no existe o no pertenece al usuario
    """
    proyecto = db.query(Project).filter(
        Project.id == proyecto_id,
        Project.estado == True,
        Project.usuario_id == current_user.id
    ).first()
    
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    return proyecto


async def _leer_contenido(archivo, proyecto: Project):
    if proyecto.origen == OrigenEnum.github:
        partes_url = proyecto.url_github.rstrip("/").split("/")
        repo = partes_url[-1]
        owner = partes_url[-2]
 
        async with httpx.AsyncClient() as client:
            r_repo = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=github_headers()
            )
            verificar_rate_limit(r_repo)  # ← lanza 429 explícito si fue rate limit
            if r_repo.status_code != 200:
                return None
 
            rama = r_repo.json().get("default_branch", "main")
 
            # raw.githubusercontent.com NO tiene rate limit estricto, no necesita headers especiales
            url_raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{rama}/{archivo.ruta_almacenamiento}"
            r = await client.get(url_raw)
 
            if r.status_code != 200:
                return None
 
            return r.text
    else:
        # Carga directa: el código vive en la columna 'contenido' de la BD,
        # no en disco (Render no tiene almacenamiento persistente entre reinicios).
        return archivo.contenido

def _calcular_score(vulnerabilidades_guardadas: list) -> float:
    """
    Calcula el score de seguridad del proyecto en escala 0 a 100,
    basado en la cantidad y severidad de los hallazgos (RF3).
    """
    if not vulnerabilidades_guardadas:
        return 100.0

    descuentos_severidad = {
        SeveridadEnum.critica: 30.0,
        SeveridadEnum.alta:    20.0,
        SeveridadEnum.media:   10.0,
        SeveridadEnum.baja:     5.0
    }

    total_descuento = 0.0
    for vuln in vulnerabilidades_guardadas:
        total_descuento += descuentos_severidad.get(vuln.severidad, 0.0)

    score = max(0.0, round(100.0 - total_descuento, 1))
    return score


async def _obtener_archivos_github(url_github: str) -> list[dict]:
    """
    Consulta la API de GitHub y retorna la lista de archivos .py del repo.
    Cada item tiene: 'path' y 'nombre'
    """
    partes = url_github.rstrip("/").split("/")
    owner = partes[-2]
    repo = partes[-1]
 
    async with httpx.AsyncClient() as client:
        r_repo = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=github_headers()
        )
        verificar_rate_limit(r_repo)
        if r_repo.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo obtener información del repositorio de GitHub"
            )
 
        rama = r_repo.json().get("default_branch", "main")
 
        r_tree = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/{rama}?recursive=1",
            headers=github_headers()
        )
        verificar_rate_limit(r_tree)
        if r_tree.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo obtener el árbol de archivos del repositorio"
            )
 
        tree = r_tree.json().get("tree", [])
 
        return [
            {
                "path": item["path"],
                "nombre": item["path"].replace("/", "_")
            }
            for item in tree
            if item["type"] == "blob" and item["path"].endswith(".py")
        ]

async def _leer_contenido_github(url_github: str, path_archivo: str) -> str | None:
    """
    Lee el contenido de un archivo .py desde raw.githubusercontent.com
    """
    partes = url_github.rstrip("/").split("/")
    owner = partes[-2]
    repo = partes[-1]
 
    async with httpx.AsyncClient() as client:
        r_repo = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=github_headers()
        )
        verificar_rate_limit(r_repo)
        if r_repo.status_code != 200:
            return None
 
        rama = r_repo.json().get("default_branch", "main")
 
        url_raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{rama}/{path_archivo}"
        r = await client.get(url_raw)
 
        if r.status_code != 200:
            return None
 
        return r.text

async def ejecutar_analisis(db: Session, proyecto_id: int, current_user: User, ip:str) -> Analysis:
    # Paso 1: Verificar proyecto
    proyecto = _verificar_proyecto_usuario(db, proyecto_id, current_user)

    # Paso 2: Crear registro de análisis
    nuevo_analisis = Analysis(
        proyecto_id=proyecto_id,
        estado=True,
        score_seguridad=0.0
    )
    db.add(nuevo_analisis)
    db.commit()
    db.refresh(nuevo_analisis)

    vulnerabilidades_guardadas = []

    # Paso 3: Bifurcar según origen
    if proyecto.origen == OrigenEnum.github:
        # Obtener lista de archivos desde GitHub
        archivos_github = await _obtener_archivos_github(proyecto.url_github)

        if not archivos_github:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontraron archivos .py en el repositorio"
            )

        for item in archivos_github:
            contenido = await _leer_contenido_github(proyecto.url_github, item["path"])
            if contenido is None:
                continue

            nombre_para_reporte = item["nombre"]
            vulnerabilidades_detectadas = analizar_contenido(contenido, nombre_para_reporte)

            # Buscar el archivo en BD solo para tener archivo_id (puede ser None)
            archivo_bd = db.query(File).filter(
                File.proyecto_id == proyecto_id,
                File.ruta_almacenamiento == item["path"],
                File.estado == True
            ).first()

            if archivo_bd is None:
                continue  # skip — no debería pasar pero protege el NOT NULL

            for v in vulnerabilidades_detectadas:
                nueva_vuln = Vulnerability(
                    tipo_owasp=v.tipo_owasp,
                    severidad=SeveridadEnum(v.severidad),
                    score_cvss=v.score_cvss,
                    codigo_vulnerable=v.codigo_vulnerable,
                    linea_codigo=v.linea_codigo,
                    fragmento_codigo=v.fragmento_codigo,
                    analisis_id=nuevo_analisis.id,
                    archivo_id=archivo_bd.id,
                    nombre_archivo=item["nombre"]
                )

                # Crear recomendación automáticamente
                recom_data = obtener_recomendacion(v.tipo_owasp)
                nueva_recom = Recommendation(
                    titulo=recom_data["titulo"],
                    explicacion_riesgo=recom_data["explicacion_riesgo"],
                    codigo_corregido_ejemplo=recom_data["codigo_corregido_ejemplo"]
                )
                nueva_vuln.recomendaciones.append(nueva_recom)  # 👈 SQLAlchemy resuelve el FK al hacer flush/commit
                db.add(nueva_vuln)
                vulnerabilidades_guardadas.append(nueva_vuln)
    else:
        # Carga directa — leer desde BD y disco
        resultado_archivos = file_service.get_archivos(db, proyecto_id, current_user)
        archivos = resultado_archivos["archivos"]

        if not archivos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El proyecto no tiene archivos para analizar"
            )

        for archivo in archivos:
            contenido = await _leer_contenido(archivo, proyecto)
            if contenido is None:
                continue

            nombre_para_reporte = archivo.nombre or archivo.ruta_almacenamiento or "archivo_desconocido"
            vulnerabilidades_detectadas = analizar_contenido(contenido, nombre_para_reporte)

            for v in vulnerabilidades_detectadas:
                nueva_vuln = Vulnerability(
                    tipo_owasp=v.tipo_owasp,
                    severidad=SeveridadEnum(v.severidad),
                    score_cvss=v.score_cvss,
                    codigo_vulnerable=v.codigo_vulnerable,
                    linea_codigo=v.linea_codigo,
                    fragmento_codigo=v.fragmento_codigo,
                    analisis_id=nuevo_analisis.id,
                    archivo_id=archivo.id,
                    nombre_archivo=archivo.nombre
                )

                # Crear recomendación automáticamente
                recom_data = obtener_recomendacion(v.tipo_owasp)
                nueva_recom = Recommendation(
                    titulo=recom_data["titulo"],
                    explicacion_riesgo=recom_data["explicacion_riesgo"],
                    codigo_corregido_ejemplo=recom_data["codigo_corregido_ejemplo"]
                )
                nueva_vuln.recomendaciones.append(nueva_recom)  # 👈 SQLAlchemy resuelve el FK al hacer flush/commit
                db.add(nueva_vuln)
                vulnerabilidades_guardadas.append(nueva_vuln)

    # Paso 4: Guardar vulnerabilidades
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error al guardar vulnerabilidades: {str(e)}"
    )    

    # Paso 5: Calcular y guardar score
    score = _calcular_score(vulnerabilidades_guardadas)
    nuevo_analisis.score_seguridad = score
    db.commit()
    db.refresh(nuevo_analisis)
    registrar_actividad(db,current_user.id,AccionEnum.analisis_ejecutado,
                        proyecto_id=proyecto_id,
                        detalle=f"Score: {nuevo_analisis.score_seguridad} | Vulnerabilidades: {len(vulnerabilidades_guardadas)}",
                        ip_origen=ip
                        )
    return nuevo_analisis


def listar_analisis(db: Session, proyecto_id: int, current_user: User) -> dict:
    """
    Lista todos los análisis realizados en un proyecto.
    
    Args:
        db: Sesión de base de datos
        proyecto_id: ID del proyecto
        current_user: Usuario autenticado propietario del proyecto
        
    Returns:
        Diccionario con keys "total" y "analisis"
        
    Raises:
        HTTPException 404 si el proyecto no existe
        HTTPException 403 si el usuario no es propietario
    """
    # Paso 1: Verificar proyecto
    _verificar_proyecto_usuario(db, proyecto_id, current_user)
    
    # Paso 2: Obtener análisis ordenados por fecha descendente
    analisis_list = db.query(Analysis).filter(
        Analysis.proyecto_id == proyecto_id
    ).order_by(Analysis.fecha_ejecucion.desc(),Analysis.id.desc()).all()
    
    # Paso 3: Devolver resultado
    return {
        "total": len(analisis_list),
        "analisis": analisis_list
    }


def get_analisis(db: Session, proyecto_id: int,analisis_id: int, current_user: User) -> Analysis:
    """
    Obtiene un análisis específico verificando acceso del usuario.
    
    Args:
        db: Sesión de base de datos
        analisis_id: ID del análisis a obtener
        current_user: Usuario autenticado
        
    Returns:
        Objeto Analisis solicitado
        
    Raises:
        HTTPException 404 si el análisis no existe
        HTTPException 403 si el usuario no tiene acceso
    """
    # Paso 1: Buscar análisis por ID
    analisis = db.query(Analysis).filter(
        Analysis.id == analisis_id,
        Analysis.proyecto_id == proyecto_id
        ).first()
    
    if not analisis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado"
        )
    
    # Paso 2: Verificar que el usuario es propietario del proyecto asociado
    proyecto = db.query(Project).filter(
        Project.id == analisis.proyecto_id,
        Project.usuario_id == current_user.id
    ).first()
    
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés acceso a este análisis"
        )
    
    # Paso 3: Devolver el análisis
    return analisis


def get_project_history(db: Session, proyecto_id: int, current_user: User) -> dict:
    """
    Obtiene el historial de análisis de un proyecto con conteos de vulnerabilidades por severidad.
    
    Args:
        db: Sesión de base de datos
        proyecto_id: ID del proyecto
        current_user: Usuario autenticado propietario del proyecto
        
    Returns:
        Diccionario con keys "total" y "historial" (lista de AnalysisHistoryItem)
        
    Raises:
        HTTPException 404 si el proyecto no existe
    """
    # Paso 1: Verificar que el proyecto existe y pertenece al usuario
    _verificar_proyecto_usuario(db, proyecto_id, current_user)
    
    # Paso 2: Obtener todos los análisis del proyecto ordenados por fecha descendente
    analisis_list = db.query(Analysis).filter(
        Analysis.proyecto_id == proyecto_id
    ).order_by(Analysis.fecha_ejecucion.desc(),Analysis.id.desc()).all()
    
    # Paso 3: Para cada análisis, calcular conteo de vulnerabilidades por severidad
    historial = []
    for analisis in analisis_list:
        # Contar vulnerabilidades por severidad usando agregación en BD
        conteo = {
            "critica": db.query(Vulnerability).filter(
                Vulnerability.analisis_id == analisis.id,
                Vulnerability.severidad == SeveridadEnum.critica
            ).count(),
            "alta": db.query(Vulnerability).filter(
                Vulnerability.analisis_id == analisis.id,
                Vulnerability.severidad == SeveridadEnum.alta
            ).count(),
            "media": db.query(Vulnerability).filter(
                Vulnerability.analisis_id == analisis.id,
                Vulnerability.severidad == SeveridadEnum.media
            ).count(),
            "baja": db.query(Vulnerability).filter(
                Vulnerability.analisis_id == analisis.id,
                Vulnerability.severidad == SeveridadEnum.baja
            ).count(),
        }
        conteo["total"] = sum(conteo.values())
        
        historial.append({
            "id": analisis.id,
            "fecha_ejecucion": analisis.fecha_ejecucion,
            "score_seguridad": analisis.score_seguridad,
            "vulnerabilidades_por_severidad": conteo
        })
    
    return {
        "total": len(historial),
        "historial": historial
    }