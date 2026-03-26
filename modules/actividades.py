"""Módulo de actividades — Responsable: P3"""
# TODO Sprint 2 - P3
"""
Módulo de actividades — lógica de negocio (CRUD + participación).
Basado en las tablas:
    actividades
    actividad_residente

Funciones públicas:
    crear_actividad(datos: dict) -> int
    obtener_actividad(id_actividad: int)
    listar_actividades() -> list
    buscar_actividades(texto: str) -> list
    actualizar_actividad(id_actividad: int, datos: dict) -> bool
    eliminar_actividad(id_actividad: int) -> bool

    registrar_participacion(datos: dict) -> int
    listar_participaciones_por_actividad(id_actividad: int) -> list
    listar_participaciones_por_residente(id_residente: int) -> list
    actualizar_participacion(id_participacion: int, datos: dict) -> bool
    eliminar_participacion(id_participacion: int) -> bool
"""

from db.connection import get_connection


CAMPOS_ACTIVIDAD_VALIDOS = {
    "nombre",
    "es_fija",
    "fecha_programada",
    "hora_programada",
}

CAMPOS_PARTICIPACION_VALIDOS = {
    "id_residente",
    "id_actividad",
    "fecha",
    "hora",
    "participo",
}


def _filtrar_campos_actividad(datos: dict) -> dict:
    return {k: v for k, v in datos.items() if k in CAMPOS_ACTIVIDAD_VALIDOS}


def _filtrar_campos_participacion(datos: dict) -> dict:
    return {k: v for k, v in datos.items() if k in CAMPOS_PARTICIPACION_VALIDOS}


# ─────────────────────────────────────────────
# CRUD DE ACTIVIDADES
# ─────────────────────────────────────────────
def crear_actividad(datos: dict) -> int:
    """
    Inserta una nueva actividad.
    Returns: id_actividad del registro creado.
    """
    campos = _filtrar_campos_actividad(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos.")

    if "nombre" not in campos or not str(campos["nombre"]).strip():
        raise ValueError("El campo 'nombre' es obligatorio.")

    if "es_fija" not in campos:
        raise ValueError("El campo 'es_fija' es obligatorio.")

    columnas = ", ".join(campos.keys())
    placeholders = ", ".join(["?"] * len(campos))
    valores = list(campos.values())

    sql = f"INSERT INTO actividades ({columnas}) VALUES ({placeholders})"

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


def obtener_actividad(id_actividad: int):
    """
    Retorna una actividad por su ID.
    Retorna None si no existe.
    """
    sql = """
        SELECT  a.*,
                COUNT(ar.id) AS total_registros,
                SUM(CASE WHEN ar.participo = 1 THEN 1 ELSE 0 END) AS total_participaron
        FROM actividades a
        LEFT JOIN actividad_residente ar ON a.id_actividad = ar.id_actividad
        WHERE a.id_actividad = ?
        GROUP BY a.id_actividad
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_actividad,)).fetchone()
    finally:
        conn.close()


def listar_actividades():
    """
    Lista todas las actividades con total de registros de participación.
    """
    sql = """
        SELECT  a.id_actividad,
                a.nombre,
                a.es_fija,
                a.fecha_programada,
                a.hora_programada,
                COUNT(ar.id) AS total_registros,
                SUM(CASE WHEN ar.participo = 1 THEN 1 ELSE 0 END) AS total_participaron
        FROM actividades a
        LEFT JOIN actividad_residente ar ON a.id_actividad = ar.id_actividad
        GROUP BY a.id_actividad
        ORDER BY a.fecha_programada DESC, a.hora_programada ASC, a.nombre ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def buscar_actividades(texto: str):
    """
    Busca actividades por nombre, tipo, fecha u hora.
    """
    patron = f"%{texto.strip()}%"
    sql = """
        SELECT  a.id_actividad,
                a.nombre,
                a.es_fija,
                a.fecha_programada,
                a.hora_programada,
                COUNT(ar.id) AS total_registros,
                SUM(CASE WHEN ar.participo = 1 THEN 1 ELSE 0 END) AS total_participaron
        FROM actividades a
        LEFT JOIN actividad_residente ar ON a.id_actividad = ar.id_actividad
        WHERE a.nombre LIKE ?
           OR a.es_fija LIKE ?
           OR a.fecha_programada LIKE ?
           OR a.hora_programada LIKE ?
        GROUP BY a.id_actividad
        ORDER BY a.fecha_programada DESC, a.hora_programada ASC, a.nombre ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (patron, patron, patron, patron)).fetchall()
    finally:
        conn.close()


def actualizar_actividad(id_actividad: int, datos: dict) -> bool:
    """
    Actualiza los campos indicados de una actividad.
    Returns: True si se actualizó, False si no existe.
    """
    campos = _filtrar_campos_actividad(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")

    set_clause = ", ".join([f"{k} = ?" for k in campos.keys()])
    valores = list(campos.values()) + [id_actividad]

    sql = f"UPDATE actividades SET {set_clause} WHERE id_actividad = ?"

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


def eliminar_actividad(id_actividad: int) -> bool:
    """
    Elimina una actividad y sus registros de participación relacionados.
    Returns: True si se eliminó, False si no existía.
    """
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM actividad_residente WHERE id_actividad = ?",
            (id_actividad,)
        )
        cur = conn.execute(
            "DELETE FROM actividades WHERE id_actividad = ?",
            (id_actividad,)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ─────────────────────────────────────────────
# PARTICIPACIÓN EN ACTIVIDADES
# ─────────────────────────────────────────────
def registrar_participacion(datos: dict) -> int:
    """
    Inserta un nuevo registro de participación.
    Returns: id del registro creado.
    """
    campos = _filtrar_campos_participacion(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos.")

    requeridos = {"id_residente", "id_actividad", "fecha", "hora", "participo"}
    faltantes = requeridos - set(campos.keys())
    if faltantes:
        raise ValueError(f"Faltan campos requeridos: {', '.join(sorted(faltantes))}")

    columnas = ", ".join(campos.keys())
    placeholders = ", ".join(["?"] * len(campos))
    valores = list(campos.values())

    sql = f"INSERT INTO actividad_residente ({columnas}) VALUES ({placeholders})"

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


def listar_participaciones_por_actividad(id_actividad: int):
    """
    Lista participaciones de una actividad con datos del residente.
    """
    sql = """
        SELECT  ar.id,
                ar.id_residente,
                r.nombre AS residente_nombre,
                r.curp AS residente_curp,
                ar.id_actividad,
                a.nombre AS actividad_nombre,
                ar.fecha,
                ar.hora,
                ar.participo
        FROM actividad_residente ar
        LEFT JOIN residentes r ON ar.id_residente = r.id_residente
        LEFT JOIN actividades a ON ar.id_actividad = a.id_actividad
        WHERE ar.id_actividad = ?
        ORDER BY ar.fecha DESC, ar.hora DESC, r.nombre ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_actividad,)).fetchall()
    finally:
        conn.close()


def listar_participaciones_por_residente(id_residente: int):
    """
    Lista participaciones de un residente.
    """
    sql = """
        SELECT  ar.id,
                ar.id_residente,
                r.nombre AS residente_nombre,
                ar.id_actividad,
                a.nombre AS actividad_nombre,
                a.es_fija,
                ar.fecha,
                ar.hora,
                ar.participo
        FROM actividad_residente ar
        LEFT JOIN residentes r ON ar.id_residente = r.id_residente
        LEFT JOIN actividades a ON ar.id_actividad = a.id_actividad
        WHERE ar.id_residente = ?
        ORDER BY ar.fecha DESC, ar.hora DESC, a.nombre ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_residente,)).fetchall()
    finally:
        conn.close()


def actualizar_participacion(id_participacion: int, datos: dict) -> bool:
    """
    Actualiza campos de un registro de participación.
    Returns: True si se actualizó, False si no existe.
    """
    campos = _filtrar_campos_participacion(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")

    set_clause = ", ".join([f"{k} = ?" for k in campos.keys()])
    valores = list(campos.values()) + [id_participacion]

    sql = f"UPDATE actividad_residente SET {set_clause} WHERE id = ?"

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


def eliminar_participacion(id_participacion: int) -> bool:
    """
    Elimina un registro de participación.
    Returns: True si se eliminó, False si no existía.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM actividad_residente WHERE id = ?",
            (id_participacion,)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
