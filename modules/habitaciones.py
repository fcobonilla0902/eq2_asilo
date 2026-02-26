"""
Módulo de habitaciones — lógica de negocio (CRUD completo).
Basado estrictamente en el diagrama de BD del equipo.

Funciones públicas:
    crear_habitacion(datos: dict) -> int
    obtener_habitacion(id_habitacion: int) -> sqlite3.Row | None
    listar_habitaciones() -> list[sqlite3.Row]
    listar_habitaciones_por_tipo(tipo: str) -> list[sqlite3.Row]
    actualizar_habitacion(id_habitacion: int, datos: dict) -> bool
    eliminar_habitacion(id_habitacion: int) -> bool
"""

from db.connection import get_connection


CAMPOS_VALIDOS = {"numero", "tipo"}


def _filtrar_campos(datos: dict) -> dict:
    return {k: v for k, v in datos.items() if k in CAMPOS_VALIDOS}


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────
def crear_habitacion(datos: dict) -> int:
    """
    Inserta una nueva habitación.
    Returns: id_habitacion del registro creado.
    """
    campos = _filtrar_campos(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos.")

    requeridos = {"numero", "tipo"}
    faltantes = requeridos - set(campos.keys())
    if faltantes:
        raise ValueError(f"Faltan campos requeridos: {', '.join(sorted(faltantes))}")

    columnas     = ", ".join(campos.keys())
    placeholders = ", ".join(["?"] * len(campos))
    valores      = list(campos.values())

    sql = f"INSERT INTO habitaciones ({columnas}) VALUES ({placeholders})"

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
def obtener_habitacion(id_habitacion: int):
    """
    Retorna una habitación por su ID, incluyendo cuántos residentes tiene asignados.
    Retorna None si no existe.
    """
    sql = """
        SELECT  h.id_habitacion,
                h.numero,
                h.tipo,
                COUNT(r.id_residente) AS residentes_count
        FROM    habitaciones h
        LEFT JOIN residentes r ON r.habitacion_id = h.id_habitacion
        WHERE   h.id_habitacion = ?
        GROUP BY h.id_habitacion
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_habitacion,)).fetchone()
    finally:
        conn.close()


def listar_habitaciones():
    """
    Retorna todas las habitaciones con el conteo de residentes asignados.
    Ordenadas por tipo y luego por número.
    """
    sql = """
        SELECT  h.id_habitacion,
                h.numero,
                h.tipo,
                COUNT(r.id_residente) AS residentes_count
        FROM    habitaciones h
        LEFT JOIN residentes r ON r.habitacion_id = h.id_habitacion
        GROUP BY h.id_habitacion
        ORDER BY h.tipo ASC, h.numero ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def listar_habitaciones_por_tipo(tipo: str):
    """
    Retorna habitaciones filtradas por tipo: '2' Doble, '3' Triple, '4' Cuádruple.
    """
    sql = """
        SELECT  h.id_habitacion,
                h.numero,
                h.tipo,
                COUNT(r.id_residente) AS residentes_count
        FROM    habitaciones h
        LEFT JOIN residentes r ON r.habitacion_id = h.id_habitacion
        WHERE   h.tipo = ?
        GROUP BY h.id_habitacion
        ORDER BY h.numero ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (tipo,)).fetchall()
    finally:
        conn.close()


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────
def actualizar_habitacion(id_habitacion: int, datos: dict) -> bool:
    """
    Actualiza los campos indicados de una habitación.
    Returns: True si se actualizó, False si no existe.
    """
    campos = _filtrar_campos(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")

    set_clause = ", ".join([f"{k} = ?" for k in campos.keys()])
    valores    = list(campos.values()) + [id_habitacion]

    sql = f"UPDATE habitaciones SET {set_clause} WHERE id_habitacion = ?"

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


# ─────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────
def eliminar_habitacion(id_habitacion: int) -> bool:
    """
    Elimina una habitación por su ID.
    Los residentes asignados quedarán con habitacion_id = NULL.
    Returns: True si se eliminó, False si no existía.
    """
    conn = get_connection()
    try:
        # Desasignar residentes antes de eliminar
        conn.execute(
            "UPDATE residentes SET habitacion_id = NULL WHERE habitacion_id = ?",
            (id_habitacion,)
        )
        cur = conn.execute(
            "DELETE FROM habitaciones WHERE id_habitacion = ?",
            (id_habitacion,)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()