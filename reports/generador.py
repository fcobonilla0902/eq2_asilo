import os
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from modules.residentes import obtener_residente
from modules.actividades import listar_participaciones_por_residente


def _texto_participo(valor):
    return "Sí" if int(valor or 0) == 1 else "No"

def generar_reporte_actividades_por_residente(id_residente: int, carpeta_salida: str = None) -> str:
    """
    Genera un PDF con el historial de actividades y participación por residente.
    Retorna la ruta absoluta del archivo generado.
    """
    residente = obtener_residente(id_residente)
    if not residente:
        raise ValueError("No se encontró el residente.")

    residente = dict(residente)

    registros = listar_participaciones_por_residente(id_residente)
    registros = [dict(r) for r in registros]
    registros.sort(key=lambda x: (str(x.get("fecha", "")), str(x.get("hora", ""))))

    if carpeta_salida is None:
        carpeta_salida = str(Path.home() / "Downloads")

    os.makedirs(carpeta_salida, exist_ok=True)

    nombre_seguro = str(residente.get("nombre", "residente")).replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"reporte_actividades_{nombre_seguro}_{timestamp}.pdf"
    ruta_archivo = os.path.abspath(os.path.join(carpeta_salida, nombre_archivo))

    doc = SimpleDocTemplate(
        ruta_archivo,
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TituloCustom",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubtituloCustom",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
        )
    )

    elementos = []

    elementos.append(Paragraph("Reporte de actividades y participación por residente", styles["TituloCustom"]))
    elementos.append(
        Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            styles["SubtituloCustom"]
        )
    )
    elementos.append(Spacer(1, 0.4 * cm))

    datos_residente = [
        ["Residente", residente.get("nombre", "—")],
        ["CURP", residente.get("curp", "—")],
        ["Edad", str(residente.get("edad", "—"))],
        ["Habitación", str(residente.get("habitacion_numero", "—"))],
    ]

    tabla_residente = Table(datos_residente, colWidths=[4 * cm, 11.5 * cm])
    tabla_residente.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e0f2fe")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )
    elementos.append(tabla_residente)
    elementos.append(Spacer(1, 0.5 * cm))

    total_registros = len(registros)
    total_si = sum(1 for r in registros if int(r.get("participo") or 0) == 1)
    total_no = total_registros - total_si
    porcentaje = (total_si / total_registros * 100) if total_registros else 0

    actividades_distintas = len({
        str(r.get("actividad_nombre", "")).strip()
        for r in registros
        if str(r.get("actividad_nombre", "")).strip()
    })

    resumen = [
        ["Total de registros", str(total_registros)],
        ["Actividades distintas", str(actividades_distintas)],
        ["Participó", str(total_si)],
        ["No participó", str(total_no)],
        ["Porcentaje de participación", f"{porcentaje:.1f}%"],
    ]

    tabla_resumen = Table(resumen, colWidths=[6 * cm, 4 * cm])
    tabla_resumen.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )
    elementos.append(Paragraph("Resumen", styles["Heading3"]))
    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph("Detalle de actividades", styles["Heading3"]))

    if registros:
        data = [["Actividad", "Tipo", "Fecha", "Hora", "Participó"]]

        for r in registros:
            data.append([
                str(r.get("actividad_nombre", "—")),
                "Fija" if str(r.get("es_fija", "")).strip().lower() in ("sí", "si", "1", "true", "fija") else "Programada",
                str(r.get("fecha", "—")),
                str(r.get("hora", "—")),
                _texto_participo(r.get("participo")),
            ])

        tabla_detalle = Table(
            data,
            colWidths=[6.0 * cm, 2.8 * cm, 2.6 * cm, 2.0 * cm, 2.4 * cm],
            repeatRows=1
        )

        estilo_detalle = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0ea5e9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]

        for i, fila in enumerate(data[1:], start=1):
            valor = str(fila[4]).strip().lower()
            if valor in ("sí", "si"):
                estilo_detalle.extend([
                    ("TEXTCOLOR", (4, i), (4, i), colors.HexColor("#15803d")),
                    ("FONTNAME", (4, i), (4, i), "Helvetica-Bold"),
                ])
            else:
                estilo_detalle.extend([
                    ("TEXTCOLOR", (4, i), (4, i), colors.HexColor("#dc2626")),
                    ("FONTNAME", (4, i), (4, i), "Helvetica-Bold"),
                ])

        tabla_detalle.setStyle(TableStyle(estilo_detalle))
        elementos.append(tabla_detalle)
    else:
        elementos.append(Paragraph(
            "No hay registros de participación para este residente en el sistema.",
            styles["Normal"]
        ))

    doc.build(elementos)

    try:
        os.startfile(ruta_archivo)
    except Exception:
        pass

    return ruta_archivo