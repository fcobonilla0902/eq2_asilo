"""Módulo de actividades — Responsable: P3"""
# TODO Sprint 2 - P3
"""
Módulo de actividades — lógica de negocio (CRUD).
Basada en la tabla:
    actividades

Funciones públicas:
    crear_actividad(datos: dict) -> int
    obtener_actividad(id_actividad: int)
    listar_actividades() -> list
    buscar_actividades(texto: str) -> list
    actualizar_actividad(id_actividad: int, datos: dict) -> bool
    eliminar_actividad(id_actividad: int) -> bool
"""

from db.connection import get_connection


CAMPOS_ACTIVIDAD_VALIDOS = {
    "nombre",
    "es_fija",
    "fecha_programada",
    "hora_programada",
    "hecho",
}


def _filtrar_campos_actividad(datos: dict) -> dict:
    return {k: v for k, v in datos.items() if k in CAMPOS_ACTIVIDAD_VALIDOS}


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
    sql = "SELECT * FROM actividades WHERE id_actividad = ?"
    conn = get_connection()
    try:
        return conn.execute(sql, (id_actividad,)).fetchone()
    finally:
        conn.close()


def listar_actividades():
    """
    Lista todas las actividades.
    """
    sql = """
        SELECT id_actividad, nombre, es_fija, fecha_programada, hora_programada,
               COALESCE(hecho, 0) AS hecho
        FROM actividades
        ORDER BY CASE WHEN es_fija IN ('Fija','sí','si','1','true') THEN 0 ELSE 1 END ASC,
                 fecha_programada DESC, hora_programada ASC, nombre ASC
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
        SELECT id_actividad, nombre, es_fija, fecha_programada, hora_programada
        FROM actividades
        WHERE nombre LIKE ?
           OR es_fija LIKE ?
           OR fecha_programada LIKE ?
           OR hora_programada LIKE ?
        ORDER BY fecha_programada DESC, hora_programada ASC, nombre ASC
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
    Elimina una actividad.
    Returns: True si se eliminó, False si no existía.
    """
    conn = get_connection()
    try:
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


def marcar_hecho(id_actividad: int, hecho: bool) -> bool:
    """
    Marca o desmarca una actividad como hecha (hecho = 1 ó 0).
    Returns: True si se actualizó, False si no existía.
    """
    conn = get_connection()
    try:
        # Migración lazy: agrega la columna si la BD es anterior al cambio
        try:
            conn.execute("ALTER TABLE actividades ADD COLUMN hecho INTEGER DEFAULT 0")
            conn.commit()
        except Exception:
            pass  # Columna ya existe

        cur = conn.execute(
            "UPDATE actividades SET hecho = ? WHERE id_actividad = ?",
            (1 if hecho else 0, id_actividad)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
