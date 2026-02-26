"""
Módulo de residentes — lógica de negocio (CRUD completo).
Basado estrictamente en el diagrama de BD del equipo.

Funciones públicas:
    crear_residente(datos: dict) -> int
    obtener_residente(id_residente: int) -> sqlite3.Row | None
    listar_residentes() -> list[sqlite3.Row]
    buscar_residentes(texto: str) -> list[sqlite3.Row]
    actualizar_residente(id_residente: int, datos: dict) -> bool
    eliminar_residente(id_residente: int) -> bool
"""

from db.connection import get_connection


CAMPOS_VALIDOS = {
    "nombre", "curp", "edad", "complexion", "color_ojos",
    "tipo_nariz", "tez_piel", "tipo_ceja", "tipo_sangre",
    "cartilla_salud", "comprobante_servicio_medico",
    "habitacion_id", "id_familiar",
    "foto_ine", "foto_comprobante_domicilio", "foto_acta_nacimiento",
    "fecha_registro",
}


def _filtrar_campos(datos: dict) -> dict:
    return {k: v for k, v in datos.items() if k in CAMPOS_VALIDOS}


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────
def crear_residente(datos: dict) -> int:
    """
    Inserta un nuevo residente.
    Returns: id_residente del registro creado.
    """
    campos = _filtrar_campos(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos.")

    columnas = ", ".join(campos.keys())
    placeholders = ", ".join(["?"] * len(campos))
    valores = list(campos.values())

    sql = f"INSERT INTO residentes ({columnas}) VALUES ({placeholders})"

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
def obtener_residente(id_residente: int):
    """
    Retorna un residente por su ID con datos de familiar y habitación.
    Retorna None si no existe.
    """
    sql = """
        SELECT  r.*,
                f.nombre    AS familiar_nombre,
                f.telefono  AS familiar_telefono,
                f.foto_ine  AS familiar_foto_ine,
                h.numero    AS habitacion_numero,
                h.tipo      AS habitacion_tipo
        FROM    residentes r
        LEFT JOIN familiares   f ON r.id_familiar   = f.id_familiar
        LEFT JOIN habitaciones h ON r.habitacion_id = h.id_habitacion
        WHERE   r.id_residente = ?
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_residente,)).fetchone()
    finally:
        conn.close()


def listar_residentes():
    """Retorna todos los residentes con su habitación asignada."""
    sql = """
        SELECT  r.id_residente,
                r.nombre,
                r.curp,
                r.edad,
                r.tipo_sangre,
                r.fecha_registro,
                h.numero AS habitacion_numero
        FROM    residentes r
        LEFT JOIN habitaciones h ON r.habitacion_id = h.id_habitacion
        ORDER BY r.nombre ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def buscar_residentes(texto: str):
    """Busca residentes por nombre o CURP (parcial, case-insensitive)."""
    patron = f"%{texto.strip()}%"
    sql = """
        SELECT  r.id_residente, r.nombre, r.curp, r.edad,
                r.tipo_sangre, h.numero AS habitacion_numero
        FROM    residentes r
        LEFT JOIN habitaciones h ON r.habitacion_id = h.id_habitacion
        WHERE   r.nombre LIKE ? OR r.curp LIKE ?
        ORDER BY r.nombre ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (patron, patron)).fetchall()
    finally:
        conn.close()


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────
def actualizar_residente(id_residente: int, datos: dict) -> bool:
    """
    Actualiza los campos indicados de un residente.
    Returns: True si se actualizó, False si no existe.
    """
    campos = _filtrar_campos(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")

    set_clause = ", ".join([f"{k} = ?" for k in campos.keys()])
    valores = list(campos.values()) + [id_residente]

    sql = f"UPDATE residentes SET {set_clause} WHERE id_residente = ?"

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
def eliminar_residente(id_residente: int) -> bool:
    """
    Elimina un residente por su ID.
    Returns: True si se eliminó, False si no existía.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM residentes WHERE id_residente = ?",
            (id_residente,)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()