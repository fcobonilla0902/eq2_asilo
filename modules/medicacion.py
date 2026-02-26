"""Módulo de medicación — Responsable: P2"""
"""
Módulo de medicación — lógica de negocio (CRUD completo junto con los modulos de alertas calculadas y el historial programado).
Basado estrictamente en el diagrama de BD del equipo (tabla: medicaciones).

Funciones públicas:
    crear_medicacion(datos: dict) -> int
    obtener_medicacion(id_medicacion: int)
    listar_medicaciones() -> list
    listar_medicaciones_por_residente(id_residente: int) -> list
    buscar_medicaciones(texto: str) -> list
    actualizar_medicacion(id_medicacion: int, datos: dict) -> bool
    eliminar_medicacion(id_medicacion: int) -> bool
    marcar_administrada(id_medicacion: int) -> bool
    desmarcar_administrada(id_medicacion: int) -> bool

    obtener_historial_residente(id_residente: int) -> list
    obtener_alertas_medicacion(fecha_actual: str, hora_actual: str) -> list
    obtener_alertas_omisiones(fecha_actual: str) -> list

NOTA: requiere que la tabla medicaciones tenga la columna:
    administrada INTEGER DEFAULT 0
Si aún no existe, ejecutar:
    ALTER TABLE medicaciones ADD COLUMN administrada INTEGER DEFAULT 0;
"""

from db.connection import get_connection


CAMPOS_VALIDOS = {
    "id_residente",
    "dosis",
    "horario",
    "fecha",
    "id_enfermero",
    "administrada",
}


def _filtrar_campos(datos: dict) -> dict:
    return {k: v for k, v in datos.items() if k in CAMPOS_VALIDOS}


def _validar_requeridos(campos: dict):
    requeridos = {"id_residente", "dosis", "horario", "fecha", "id_enfermero"}
    faltantes = requeridos - set(campos.keys())
    if faltantes:
        raise ValueError(f"Faltan campos requeridos: {', '.join(sorted(faltantes))}")


def _ensure_column():
    """
    Agrega la columna 'administrada' si no existe todavía.
    Se llama automáticamente al importar el módulo.
    """
    conn = get_connection()
    try:
        cols = [row[1] for row in conn.execute("PRAGMA table_info(medicaciones)").fetchall()]
        if "administrada" not in cols:
            conn.execute("ALTER TABLE medicaciones ADD COLUMN administrada INTEGER DEFAULT 0")
            conn.commit()
    finally:
        conn.close()


# Migración automática al importar
try:
    _ensure_column()
except Exception:
    pass  # Si la tabla aún no existe, no pasa nada


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────
def crear_medicacion(datos: dict) -> int:
    """
    Inserta una nueva medicación programada.
    Returns: id_medicacion del registro creado.
    """
    campos = _filtrar_campos(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos.")

    _validar_requeridos(campos)

    # administrada siempre inicia en 0
    campos["administrada"] = 0

    columnas = ", ".join(campos.keys())
    placeholders = ", ".join(["?"] * len(campos))
    valores = list(campos.values())

    sql = f"INSERT INTO medicaciones ({columnas}) VALUES ({placeholders})"

    conn = get_connection()
    try:
        cur = conn.execute(sql, valores)
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ─────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────
def obtener_medicacion(id_medicacion: int):
    """
    Retorna una medicación por ID con datos del residente y enfermero.
    Retorna None si no existe.
    """
    sql = """
        SELECT  m.*,
                r.nombre AS residente_nombre,
                r.curp   AS residente_curp,
                e.nombre AS enfermero_nombre,
                e.telefono AS enfermero_telefono
        FROM medicaciones m
        LEFT JOIN residentes r ON m.id_residente = r.id_residente
        LEFT JOIN enfermeros e ON m.id_enfermero = e.id_enfermero
        WHERE m.id_medicacion = ?
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_medicacion,)).fetchone()
    finally:
        conn.close()


def listar_medicaciones():
    """
    Lista todas las medicaciones programadas con nombres de residente y enfermero.
    """
    sql = """
        SELECT  m.id_medicacion,
                m.fecha,
                m.horario,
                m.dosis,
                m.id_residente,
                r.nombre AS residente_nombre,
                m.id_enfermero,
                e.nombre AS enfermero_nombre,
                m.administrada
        FROM medicaciones m
        LEFT JOIN residentes r ON m.id_residente = r.id_residente
        LEFT JOIN enfermeros e ON m.id_enfermero = e.id_enfermero
        ORDER BY m.fecha DESC, m.horario ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def listar_medicaciones_por_residente(id_residente: int):
    """
    Lista medicaciones programadas de un residente.
    """
    sql = """
        SELECT  m.id_medicacion,
                m.fecha,
                m.horario,
                m.dosis,
                m.id_enfermero,
                e.nombre AS enfermero_nombre,
                m.administrada
        FROM medicaciones m
        LEFT JOIN enfermeros e ON m.id_enfermero = e.id_enfermero
        WHERE m.id_residente = ?
        ORDER BY m.fecha DESC, m.horario DESC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_residente,)).fetchall()
    finally:
        conn.close()


def buscar_medicaciones(texto: str):
    """
    Busca medicaciones por nombre de residente, dosis, fecha o horario.
    """
    patron = f"%{texto.strip()}%"
    sql = """
        SELECT  m.id_medicacion,
                m.fecha,
                m.horario,
                m.dosis,
                r.nombre AS residente_nombre,
                e.nombre AS enfermero_nombre,
                m.administrada
        FROM medicaciones m
        LEFT JOIN residentes r ON m.id_residente = r.id_residente
        LEFT JOIN enfermeros e ON m.id_enfermero = e.id_enfermero
        WHERE r.nombre LIKE ?
           OR m.dosis LIKE ?
           OR m.fecha LIKE ?
           OR m.horario LIKE ?
        ORDER BY m.fecha DESC, m.horario ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (patron, patron, patron, patron)).fetchall()
    finally:
        conn.close()


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────
def actualizar_medicacion(id_medicacion: int, datos: dict) -> bool:
    """
    Actualiza campos de una medicación programada.
    Returns: True si se actualizó, False si no existe.
    """
    campos = _filtrar_campos(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")

    set_clause = ", ".join([f"{k} = ?" for k in campos.keys()])
    valores = list(campos.values()) + [id_medicacion]

    sql = f"UPDATE medicaciones SET {set_clause} WHERE id_medicacion = ?"

    conn = get_connection()
    try:
        cur = conn.execute(sql, valores)
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def marcar_administrada(id_medicacion: int) -> bool:
    """
    Marca una medicación como administrada (aplicada al residente).
    Returns: True si se actualizó, False si no existe.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE medicaciones SET administrada = 1 WHERE id_medicacion = ?",
            (id_medicacion,)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def desmarcar_administrada(id_medicacion: int) -> bool:
    """
    Revierte el estado administrada de una medicación (por error de registro).
    Returns: True si se actualizó, False si no existe.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE medicaciones SET administrada = 0 WHERE id_medicacion = ?",
            (id_medicacion,)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ─────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────
def eliminar_medicacion(id_medicacion: int) -> bool:
    """
    Elimina una medicación por su ID.
    Returns: True si se eliminó, False si no existía.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM medicaciones WHERE id_medicacion = ?",
            (id_medicacion,)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ─────────────────────────────────────────────
# HISTORIAL (programado)
# ─────────────────────────────────────────────
def obtener_historial_residente(id_residente: int):
    """
    Historial de medicaciones programadas del residente.
    """
    sql = """
        SELECT  m.id_medicacion,
                m.fecha,
                m.horario,
                m.dosis,
                e.nombre AS enfermero_nombre,
                m.administrada
        FROM medicaciones m
        LEFT JOIN enfermeros e ON m.id_enfermero = e.id_enfermero
        WHERE m.id_residente = ?
        ORDER BY m.fecha DESC, m.horario DESC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_residente,)).fetchall()
    finally:
        conn.close()


# ─────────────────────────────────────────────
# ALERTAS (calculadas)
# ─────────────────────────────────────────────
def obtener_alertas_medicacion(fecha_actual: str, hora_actual: str):
    """
    Alertas de medicaciones vencidas hasta el momento, excluyendo las ya administradas.

    fecha_actual: 'YYYY-MM-DD'
    hora_actual:  'HH:MM'
    """
    sql = """
        SELECT  m.id_medicacion,
                m.fecha,
                m.horario,
                m.dosis,
                r.id_residente,
                r.nombre AS residente_nombre,
                e.nombre AS enfermero_nombre
        FROM medicaciones m
        LEFT JOIN residentes r ON m.id_residente = r.id_residente
        LEFT JOIN enfermeros e ON m.id_enfermero = e.id_enfermero
        WHERE (
            (m.fecha < ?)
            OR (m.fecha = ? AND m.horario <= ?)
        )
        AND m.administrada = 0
        ORDER BY m.fecha ASC, m.horario ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (fecha_actual, fecha_actual, hora_actual)).fetchall()
    finally:
        conn.close()


def obtener_alertas_omisiones(fecha_actual: str):
    """
    Alertas de medicaciones de días anteriores no administradas (omisiones reales).
    """
    sql = """
        SELECT  m.id_medicacion,
                m.fecha,
                m.horario,
                m.dosis,
                r.id_residente,
                r.nombre AS residente_nombre,
                e.nombre AS enfermero_nombre
        FROM medicaciones m
        LEFT JOIN residentes r ON m.id_residente = r.id_residente
        LEFT JOIN enfermeros e ON m.id_enfermero = e.id_enfermero
        WHERE m.fecha < ?
          AND m.administrada = 0
        ORDER BY m.fecha ASC, m.horario ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (fecha_actual,)).fetchall()
    finally:
        conn.close()