import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from app.services.vulnerability_service import contar_vulnerabilidades_por_severidad


def generar_grafico_severidad(conteo: dict):
    """
    Genera un gráfico de barras PNG con el conteo de vulnerabilidades por severidad.
    
    Args:
        conteo: Diccionario con claves 'critica', 'alta', 'media', 'baja' (números enteros)
    
    Returns:
        io.BytesIO: Buffer con la imagen PNG del gráfico
    """
    fig, ax = plt.subplots(figsize=(5, 3))
    
    severidades = ["Crítica", "Alta", "Media", "Baja"]
    valores = [conteo["critica"], conteo["alta"], conteo["media"], conteo["baja"]]
    colores = ["#dc2626", "#f97316", "#eab308", "#3b82f6"]
    
    ax.bar(severidades, valores, color=colores)
    ax.set_title("Vulnerabilidades por Severidad")
    ax.set_ylabel("Cantidad")
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    
    buffer.seek(0)
    return buffer


def generar_reporte_pdf(proyecto_nombre: str, analisis, vulnerabilidades: list):
    """
    Genera un reporte PDF completo con el análisis de seguridad.
    
    Args:
        proyecto_nombre: Nombre del proyecto
        analisis: Objeto análisis con atributos id, fecha_ejecucion, score_seguridad
        vulnerabilidades: Lista de objetos vulnerabilidad
    
    Returns:
        io.BytesIO: Buffer con el PDF generado
    """
    # PASO 1 - Preparar el documento
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elementos = []
    
    # PASO 2 - Encabezado
    elementos.append(Paragraph("Reporte de Seguridad — SAST", styles["Title"]))
    elementos.append(Spacer(1, 0.5*cm))
    elementos.append(Paragraph(f"Proyecto: {proyecto_nombre}", styles["Normal"]))
    elementos.append(Paragraph(f"Análisis Nro.: {analisis.id}", styles["Normal"]))
    elementos.append(Paragraph(f"Fecha: {analisis.fecha_ejecucion}", styles["Normal"]))
    elementos.append(Spacer(1, 0.3*cm))
    elementos.append(Paragraph(f"Score de Seguridad: {analisis.score_seguridad}/100", styles["Heading2"]))
    elementos.append(Spacer(1, 0.5*cm))
    
    # PASO 3 - Calcular conteo por severidad
    conteo = {"critica": 0, "alta": 0, "media": 0, "baja": 0}
    for vuln in vulnerabilidades:
        severidad_valor = vuln.severidad.value
        if severidad_valor == "critica":
            conteo["critica"] += 1
        elif severidad_valor == "alta":
            conteo["alta"] += 1
        elif severidad_valor == "media":
            conteo["media"] += 1
        elif severidad_valor == "baja":
            conteo["baja"] += 1
    
    # PASO 4 - Tabla resumen
    tabla_data = [
        ["Severidad", "Cantidad"],
        ["Crítica", conteo["critica"]],
        ["Alta", conteo["alta"]],
        ["Media", conteo["media"]],
        ["Baja", conteo["baja"]],
        ["Total", len(vulnerabilidades)]
    ]
    tabla = Table(tabla_data)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 0.5*cm))
    
    # PASO 5 - Insertar el gráfico
    buffer_grafico = generar_grafico_severidad(conteo)
    elementos.append(Image(buffer_grafico, width=12*cm, height=7*cm))
    elementos.append(Spacer(1, 0.7*cm))
    
    # PASO 6 - Si la lista de vulnerabilidades está vacía
    if not vulnerabilidades:
        elementos.append(Paragraph("No se detectaron vulnerabilidades en este análisis.", styles["Normal"]))
    else:
        # PASO 7 - Si hay vulnerabilidades, agregar detalles de cada una
        estilo_codigo = ParagraphStyle(
            'CodigoPersonalizado',
            fontName='Courier',
            fontSize=8,
            backColor=colors.Color(0.95, 0.95, 0.95)
        )
        
        for numero, vuln in enumerate(vulnerabilidades, start=1):
            elementos.append(Paragraph(
                f"{numero}. {vuln.tipo_owasp} — Severidad: {vuln.severidad.value.upper()} (CVSS {vuln.score_cvss})",
                styles["Heading3"]
            ))
            elementos.append(Paragraph(
                f"Archivo: {vuln.nombre_archivo} · Línea: {vuln.linea_codigo}",
                styles["Normal"]
            ))
            elementos.append(Paragraph("Código vulnerable:", styles["Normal"]))
            elementos.append(Paragraph(
                vuln.fragmento_codigo.replace("\n", "<br/>"),
                estilo_codigo
            ))
            
            if vuln.recomendaciones:
                elementos.append(Paragraph(
                    f"💡 {vuln.recomendaciones[0].titulo}",
                    styles["Heading4"]
                ))
                elementos.append(Paragraph(
                    vuln.recomendaciones[0].explicacion_riesgo,
                    styles["Normal"]
                ))
                elementos.append(Paragraph("Código corregido sugerido:", styles["Normal"]))
                elementos.append(Paragraph(
                    vuln.recomendaciones[0].codigo_corregido_ejemplo.replace("\n", "<br/>"),
                    estilo_codigo
                ))
            
            elementos.append(Spacer(1, 0.7*cm))
    
    # PASO 8 - Generar el PDF
    doc.build(elementos)
    buffer.seek(0)
    return buffer
