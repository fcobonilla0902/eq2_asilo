"""
╔══════════════════════════════════════════════════════════════╗
║          PRUEBAS MANUALES — eq2_asilo                       ║
║  Ejecutar desde la raíz del proyecto:                       ║
║      python pruebas_consola.py                              ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.schema import init_db
from db.connection import get_connection
from modules.residentes import (
    crear_residente, obtener_residente, listar_residentes,
    buscar_residentes, actualizar_residente, eliminar_residente,
)
from modules.medicacion import (
    crear_medicacion, obtener_medicacion, listar_medicaciones,
    listar_medicaciones_por_residente, buscar_medicaciones,
    actualizar_medicacion, eliminar_medicacion,
    obtener_historial_residente,
    obtener_alertas_medicacion, obtener_alertas_omisiones,
)

# ── Colores en terminal ──────────────────────────────────────
OK    = "\033[92m✅ PASS\033[0m"
FAIL  = "\033[91m❌ FAIL\033[0m"
WARN  = "\033[93m⚠️  OBS\033[0m"
SEP   = "\033[90m" + "─" * 60 + "\033[0m"
HEAD  = "\033[1;34m"
RESET = "\033[0m"

resultados = []

def titulo(texto):
    print(f"\n{HEAD}{'═'*60}")
    print(f"  {texto}")
    print(f"{'═'*60}{RESET}")

def caso(id_caso, descripcion, resultado, esperado, aprobado):
    estado = OK if aprobado else FAIL
    resultados.append((id_caso, descripcion, aprobado))
    print(f"\n[{id_caso}] {descripcion}")
    print(f"  Esperado : {esperado}")
    print(f"  Obtenido : {resultado}")
    print(f"  {estado}")

def observacion(texto):
    print(f"\n  {WARN} {texto}")

# ── Preparar BD limpia ───────────────────────────────────────
def limpiar_bd():
    conn = get_connection()
    conn.execute("DELETE FROM medicaciones")
    conn.execute("DELETE FROM residentes")
    conn.execute("DELETE FROM enfermeros")
    conn.execute("DELETE FROM familiares")
    conn.execute("DELETE FROM habitaciones")
    conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('medicaciones','residentes','enfermeros','familiares','habitaciones')")
    conn.commit()
    conn.close()

def insertar_datos_base():
    conn = get_connection()
    conn.execute("INSERT INTO familiares (nombre, telefono) VALUES ('Ana Pérez', '5512345678')")
    conn.execute("INSERT INTO habitaciones (numero, tipo) VALUES ('101', 'Individual')")
    conn.execute("INSERT INTO enfermeros (nombre, telefono, curp) VALUES ('Enf. García', '5598765432', 'GARM800101HDFXXX01')")
    conn.commit()
    conn.close()

# ════════════════════════════════════════════════════════════
#  SECCIÓN 1 — CRUD RESIDENTES
# ════════════════════════════════════════════════════════════

def pruebas_residentes():
    titulo("SECCIÓN 1 — CRUD RESIDENTES")
    limpiar_bd()
    insertar_datos_base()

    # ── R-01: Alta con datos completos ───────────────────────
    try:
        rid = crear_residente({
            "nombre": "María López",
            "curp": "LOPM900101MDFXXX01",
            "edad": 75,
            "tipo_sangre": "O+",
            "habitacion_id": 1,
            "id_familiar": 1,
            "fecha_registro": "2025-06-01",
        })
        caso("R-01", "Alta con datos completos",
             f"id_residente={rid}", "id > 0", rid > 0)
    except Exception as e:
        caso("R-01", "Alta con datos completos", str(e), "id > 0", False)

    # ── R-02: Alta con dict vacío ────────────────────────────
    try:
        crear_residente({})
        caso("R-02", "Alta con dict vacío", "No lanzó excepción", "ValueError", False)
    except ValueError as e:
        caso("R-02", "Alta con dict vacío", f"ValueError: {e}", "ValueError", True)
    except Exception as e:
        caso("R-02", "Alta con dict vacío", f"Otro error: {e}", "ValueError", False)

    # ── R-03: Alta con campo inválido (debe ignorarlo) ────────
    try:
        rid2 = crear_residente({"nombre": "Juan Ruiz", "peso": 70, "edad": 80})
        res = obtener_residente(rid2)
        caso("R-03", "Alta ignorando campo inválido 'peso'",
             f"id={rid2}, nombre={res['nombre']}", "Inserta sin error, ignora 'peso'", rid2 > 0)
    except Exception as e:
        caso("R-03", "Alta ignorando campo inválido 'peso'", str(e), "Inserta sin error", False)

    print(SEP)

    # ── R-04: Consulta por ID existente ──────────────────────
    try:
        res = obtener_residente(1)
        caso("R-04", "Consulta por ID existente (id=1)",
             f"nombre={res['nombre']}, familiar={res['familiar_nombre']}",
             "Row con datos + familiar_nombre", res is not None)
    except Exception as e:
        caso("R-04", "Consulta por ID existente", str(e), "Row con datos", False)

    # ── R-05: Consulta por ID inexistente ────────────────────
    try:
        res = obtener_residente(9999)
        caso("R-05", "Consulta por ID inexistente (id=9999)",
             str(res), "None", res is None)
    except Exception as e:
        caso("R-05", "Consulta por ID inexistente", str(e), "None", False)

    # ── R-06: Listar todos ───────────────────────────────────
    try:
        lista = listar_residentes()
        caso("R-06", "Listar todos los residentes",
             f"{len(lista)} residente(s): {[r['nombre'] for r in lista]}",
             "Lista con ≥1 elemento", len(lista) >= 1)
    except Exception as e:
        caso("R-06", "Listar todos", str(e), "Lista ≥1", False)

    # ── R-07: Buscar por nombre parcial ──────────────────────
    try:
        resultados_busq = buscar_residentes("María")
        caso("R-07", "Buscar por nombre 'María'",
             f"{len(resultados_busq)} resultado(s)", "≥1 resultado", len(resultados_busq) >= 1)
    except Exception as e:
        caso("R-07", "Buscar por nombre", str(e), "≥1 resultado", False)

    # ── R-08: Buscar por CURP parcial ────────────────────────
    try:
        resultados_busq = buscar_residentes("LOPM")
        caso("R-08", "Buscar por CURP parcial 'LOPM'",
             f"{len(resultados_busq)} resultado(s)", "≥1 resultado", len(resultados_busq) >= 1)
    except Exception as e:
        caso("R-08", "Buscar por CURP", str(e), "≥1 resultado", False)

    # ── R-09: Buscar sin coincidencias ───────────────────────
    try:
        resultados_busq = buscar_residentes("XYZZZZ999")
        caso("R-09", "Buscar texto sin coincidencias 'XYZZZZ999'",
             f"{len(resultados_busq)} resultado(s)", "Lista vacía []", len(resultados_busq) == 0)
    except Exception as e:
        caso("R-09", "Buscar sin coincidencias", str(e), "Lista vacía", False)

    print(SEP)

    # ── R-10: Edición de campo simple ────────────────────────
    try:
        ok = actualizar_residente(1, {"edad": 76})
        res = obtener_residente(1)
        caso("R-10", "Editar edad del residente id=1",
             f"retorna={ok}, edad_nueva={res['edad']}", "True y edad=76", ok and res["edad"] == 76)
    except Exception as e:
        caso("R-10", "Editar campo simple", str(e), "True y edad=76", False)

    # ── R-11: Edición de ID inexistente ─────────────────────
    try:
        ok = actualizar_residente(9999, {"edad": 99})
        caso("R-11", "Editar residente inexistente (id=9999)",
             str(ok), "False", ok == False)
    except Exception as e:
        caso("R-11", "Editar ID inexistente", str(e), "False", False)

    # ── R-12: Edición con campo inválido ─────────────────────
    try:
        actualizar_residente(1, {"peso": 70})
        caso("R-12", "Editar con campo inválido 'peso'", "No lanzó excepción", "ValueError", False)
    except ValueError as e:
        caso("R-12", "Editar con campo inválido 'peso'", f"ValueError: {e}", "ValueError", True)
    except Exception as e:
        caso("R-12", "Editar con campo inválido", str(e), "ValueError", False)

    print(SEP)

    # ── R-13: Eliminar existente ─────────────────────────────
    try:
        # Crear uno extra para eliminar sin afectar las siguientes pruebas
        rid_tmp = crear_residente({"nombre": "Temporal Borrar", "edad": 60})
        ok = eliminar_residente(rid_tmp)
        res = obtener_residente(rid_tmp)
        caso("R-13", f"Eliminar residente id={rid_tmp}",
             f"retorna={ok}, consulta_post={res}", "True y None", ok and res is None)
    except Exception as e:
        caso("R-13", "Eliminar existente", str(e), "True y None", False)

    # ── R-14: Eliminar inexistente ───────────────────────────
    try:
        ok = eliminar_residente(9999)
        caso("R-14", "Eliminar residente inexistente (id=9999)",
             str(ok), "False", ok == False)
    except Exception as e:
        caso("R-14", "Eliminar inexistente", str(e), "False", False)

    # ── Observación: baja lógica ─────────────────────────────
    observacion("R-OBS: eliminar_residente() hace DELETE físico. "
                "No existe campo 'activo' para baja lógica.")


# ════════════════════════════════════════════════════════════
#  SECCIÓN 2 — CRUD MEDICACIONES
# ════════════════════════════════════════════════════════════

def pruebas_medicaciones():
    titulo("SECCIÓN 2 — CRUD MEDICACIONES")

    # ── M-01: Crear medicación completa ──────────────────────
    try:
        mid = crear_medicacion({
            "id_residente": 1,
            "dosis": "Paracetamol 500mg",
            "horario": "08:00",
            "fecha": "2025-06-01",
            "id_enfermero": 1,
        })
        caso("M-01", "Crear medicación con todos los campos",
             f"id_medicacion={mid}", "id > 0", mid > 0)
    except Exception as e:
        caso("M-01", "Crear medicación completa", str(e), "id > 0", False)

    # ── M-02: Crear sin campo requerido ──────────────────────
    try:
        crear_medicacion({
            "id_residente": 1,
            "horario": "08:00",
            "fecha": "2025-06-01",
            "id_enfermero": 1,
            # falta 'dosis'
        })
        caso("M-02", "Crear sin campo 'dosis'", "No lanzó excepción", "ValueError", False)
    except ValueError as e:
        caso("M-02", "Crear sin campo 'dosis'", f"ValueError: {e}", "ValueError", True)
    except Exception as e:
        caso("M-02", "Crear sin campo 'dosis'", str(e), "ValueError", False)

    # ── M-03: Crear segunda medicación ───────────────────────
    try:
        mid2 = crear_medicacion({
            "id_residente": 1,
            "dosis": "Ibuprofeno 400mg",
            "horario": "14:00",
            "fecha": "2025-06-01",
            "id_enfermero": 1,
        })
        caso("M-03", "Crear segunda medicación (mismo residente)",
             f"id_medicacion={mid2}", "id > 0", mid2 > 0)
    except Exception as e:
        caso("M-03", "Crear segunda medicación", str(e), "id > 0", False)

    print(SEP)

    # ── M-04: Obtener por ID existente ───────────────────────
    try:
        med = obtener_medicacion(1)
        caso("M-04", "Obtener medicación id=1",
             f"dosis={med['dosis']}, residente={med['residente_nombre']}, enfermero={med['enfermero_nombre']}",
             "Row con dosis + nombres", med is not None)
    except Exception as e:
        caso("M-04", "Obtener por ID existente", str(e), "Row con datos", False)

    # ── M-05: Obtener por ID inexistente ─────────────────────
    try:
        med = obtener_medicacion(9999)
        caso("M-05", "Obtener medicación inexistente (id=9999)",
             str(med), "None", med is None)
    except Exception as e:
        caso("M-05", "Obtener ID inexistente", str(e), "None", False)

    # ── M-06: Listar todas ───────────────────────────────────
    try:
        lista = listar_medicaciones()
        caso("M-06", "Listar todas las medicaciones",
             f"{len(lista)} registro(s): {[(r['dosis'], r['horario']) for r in lista]}",
             "≥2 registros ordenados", len(lista) >= 2)
    except Exception as e:
        caso("M-06", "Listar todas", str(e), "≥2 registros", False)

    # ── M-07: Listar por residente ───────────────────────────
    try:
        lista = listar_medicaciones_por_residente(1)
        caso("M-07", "Listar medicaciones del residente id=1",
             f"{len(lista)} registro(s)", "≥2 registros", len(lista) >= 2)
    except Exception as e:
        caso("M-07", "Listar por residente", str(e), "≥2 registros", False)

    # ── M-08: Listar por residente sin medicaciones ──────────
    try:
        lista = listar_medicaciones_por_residente(9999)
        caso("M-08", "Listar medicaciones de residente inexistente (id=9999)",
             f"{len(lista)} registro(s)", "Lista vacía []", len(lista) == 0)
    except Exception as e:
        caso("M-08", "Listar por residente inexistente", str(e), "Lista vacía", False)

    # ── M-09: Buscar por dosis ───────────────────────────────
    try:
        lista = buscar_medicaciones("Paracetamol")
        caso("M-09", "Buscar medicaciones por dosis 'Paracetamol'",
             f"{len(lista)} resultado(s)", "≥1 resultado", len(lista) >= 1)
    except Exception as e:
        caso("M-09", "Buscar por dosis", str(e), "≥1 resultado", False)

    # ── M-10: Buscar por nombre de residente ─────────────────
    try:
        lista = buscar_medicaciones("María")
        caso("M-10", "Buscar medicaciones por nombre residente 'María'",
             f"{len(lista)} resultado(s)", "≥1 resultado", len(lista) >= 1)
    except Exception as e:
        caso("M-10", "Buscar por nombre residente", str(e), "≥1 resultado", False)

    print(SEP)

    # ── M-11: Actualizar dosis ───────────────────────────────
    try:
        ok = actualizar_medicacion(1, {"dosis": "Paracetamol 1000mg"})
        med = obtener_medicacion(1)
        caso("M-11", "Actualizar dosis de medicación id=1",
             f"retorna={ok}, dosis_nueva={med['dosis']}",
             "True y dosis=Paracetamol 1000mg", ok and med["dosis"] == "Paracetamol 1000mg")
    except Exception as e:
        caso("M-11", "Actualizar dosis", str(e), "True y nueva dosis", False)

    # ── M-12: Actualizar horario ─────────────────────────────
    try:
        ok = actualizar_medicacion(1, {"horario": "10:00", "fecha": "2025-06-15"})
        med = obtener_medicacion(1)
        caso("M-12", "Actualizar horario y fecha de medicación id=1",
             f"retorna={ok}, horario={med['horario']}, fecha={med['fecha']}",
             "True y horario=10:00", ok and med["horario"] == "10:00")
    except Exception as e:
        caso("M-12", "Actualizar horario/fecha", str(e), "True", False)

    # ── M-13: Actualizar inexistente ─────────────────────────
    try:
        ok = actualizar_medicacion(9999, {"dosis": "Aspirina"})
        caso("M-13", "Actualizar medicación inexistente (id=9999)",
             str(ok), "False", ok == False)
    except Exception as e:
        caso("M-13", "Actualizar inexistente", str(e), "False", False)

    # ── M-14: Eliminar existente ─────────────────────────────
    try:
        mid_tmp = crear_medicacion({
            "id_residente": 1, "dosis": "Temporal", "horario": "23:00",
            "fecha": "2025-06-30", "id_enfermero": 1,
        })
        ok = eliminar_medicacion(mid_tmp)
        med = obtener_medicacion(mid_tmp)
        caso("M-14", f"Eliminar medicación id={mid_tmp}",
             f"retorna={ok}, consulta_post={med}", "True y None", ok and med is None)
    except Exception as e:
        caso("M-14", "Eliminar existente", str(e), "True y None", False)

    # ── M-15: Eliminar inexistente ───────────────────────────
    try:
        ok = eliminar_medicacion(9999)
        caso("M-15", "Eliminar medicación inexistente (id=9999)",
             str(ok), "False", ok == False)
    except Exception as e:
        caso("M-15", "Eliminar inexistente", str(e), "False", False)


# ════════════════════════════════════════════════════════════
#  SECCIÓN 3 — ALERTAS Y OMISIONES
# ════════════════════════════════════════════════════════════

def pruebas_alertas():
    titulo("SECCIÓN 3 — ALERTAS Y DETECCIÓN DE OMISIONES")

    # Insertar medicaciones con fechas variadas para las alertas
    conn = get_connection()
    conn.execute("DELETE FROM medicaciones")
    conn.commit()
    conn.close()

    crear_medicacion({"id_residente": 1, "dosis": "Metformina 850mg", "horario": "08:00", "fecha": "2025-05-29", "id_enfermero": 1})  # omisión (pasado)
    crear_medicacion({"id_residente": 1, "dosis": "Losartán 50mg",    "horario": "08:00", "fecha": "2025-05-31", "id_enfermero": 1})  # omisión (pasado)
    crear_medicacion({"id_residente": 1, "dosis": "Paracetamol 500mg","horario": "08:00", "fecha": "2025-06-01", "id_enfermero": 1})  # vencida hoy (pasó las 08:00)
    crear_medicacion({"id_residente": 1, "dosis": "Ibuprofeno 400mg", "horario": "20:00", "fecha": "2025-06-01", "id_enfermero": 1})  # futura hoy (aún no son las 20:00)

    FECHA_HOY   = "2025-06-01"
    HORA_ACTUAL = "09:00"

    # ── A-01: Alerta vencida mismo día ───────────────────────
    try:
        alertas = obtener_alertas_medicacion(FECHA_HOY, HORA_ACTUAL)
        nombres = [a["dosis"] for a in alertas]
        tiene_paracetamol = any("Paracetamol" in d for d in nombres)
        caso("A-01", f"Alerta: medicación 08:00 vencida a las {HORA_ACTUAL}",
             f"{len(alertas)} alerta(s): {nombres}",
             "Paracetamol 08:00 aparece en alertas", tiene_paracetamol)
    except Exception as e:
        caso("A-01", "Alerta vencida mismo día", str(e), "Lista con medicación", False)

    # ── A-02: Medicación futura NO genera alerta ─────────────
    try:
        alertas = obtener_alertas_medicacion(FECHA_HOY, HORA_ACTUAL)
        nombres = [a["dosis"] for a in alertas]
        ibuprofeno_no_esta = not any("Ibuprofeno" in d for d in nombres)
        caso("A-02", f"Medicación 20:00 NO aparece en alertas a las {HORA_ACTUAL}",
             f"Ibuprofeno en alertas: {not ibuprofeno_no_esta}",
             "Ibuprofeno NO en alertas", ibuprofeno_no_esta)
    except Exception as e:
        caso("A-02", "Medicación futura no alerta", str(e), "Ibuprofeno ausente", False)

    # ── A-03: Omisiones de días anteriores ───────────────────
    try:
        omisiones = obtener_alertas_omisiones(FECHA_HOY)
        fechas = [o["fecha"] for o in omisiones]
        tiene_pasado = all(f < FECHA_HOY for f in fechas)
        caso("A-03", f"Omisiones: medicaciones con fecha < {FECHA_HOY}",
             f"{len(omisiones)} omisión(es): fechas={fechas}",
             "Solo fechas anteriores a hoy", len(omisiones) >= 2 and tiene_pasado)
    except Exception as e:
        caso("A-03", "Detección de omisiones", str(e), "Lista con fechas pasadas", False)

    # ── A-04: Sin alertas cuando todo es futuro ───────────────
    try:
        alertas = obtener_alertas_medicacion("2020-01-01", "00:00")
        caso("A-04", "Sin alertas cuando fecha_actual es muy antigua (2020-01-01 00:00)",
             f"{len(alertas)} alerta(s)", "Lista vacía []", len(alertas) == 0)
    except Exception as e:
        caso("A-04", "Sin alertas futuras", str(e), "Lista vacía", False)

    # ── A-05: Sin omisiones cuando todo es hoy o futuro ──────
    try:
        omisiones = obtener_alertas_omisiones("2020-01-01")
        caso("A-05", "Sin omisiones cuando fecha_actual es muy antigua (2020-01-01)",
             f"{len(omisiones)} omisión(es)", "Lista vacía []", len(omisiones) == 0)
    except Exception as e:
        caso("A-05", "Sin omisiones", str(e), "Lista vacía", False)

    # ── A-06: Historial de residente ─────────────────────────
    try:
        historial = obtener_historial_residente(1)
        caso("A-06", "Historial medicaciones del residente id=1",
             f"{len(historial)} registro(s): {[(h['dosis'], h['fecha']) for h in historial]}",
             "≥4 registros ordenados", len(historial) >= 4)
    except Exception as e:
        caso("A-06", "Historial residente", str(e), "≥4 registros", False)

    # ── A-07: Historial de residente sin medicaciones ─────────
    try:
        historial = obtener_historial_residente(9999)
        caso("A-07", "Historial de residente inexistente (id=9999)",
             f"{len(historial)} registro(s)", "Lista vacía []", len(historial) == 0)
    except Exception as e:
        caso("A-07", "Historial inexistente", str(e), "Lista vacía", False)


# ════════════════════════════════════════════════════════════
#  RESUMEN FINAL
# ════════════════════════════════════════════════════════════

def resumen():
    titulo("RESUMEN DE RESULTADOS")
    aprobados = sum(1 for _, _, ok in resultados if ok)
    fallidos   = len(resultados) - aprobados
    print(f"\n  Total de casos : {len(resultados)}")
    print(f"  \033[92mAprobados      : {aprobados}\033[0m")
    print(f"  \033[91mFallidos       : {fallidos}\033[0m")

    if fallidos:
        print(f"\n  Casos fallidos:")
        for cid, desc, ok in resultados:
            if not ok:
                print(f"    ❌ [{cid}] {desc}")
    print()


# ════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n\033[1mInicializando base de datos...\033[0m")
    init_db()

    pruebas_residentes()
    pruebas_medicaciones()
    pruebas_alertas()
    resumen()