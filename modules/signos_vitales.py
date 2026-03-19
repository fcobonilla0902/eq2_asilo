"""Módulo de signos vitales — Responsable: P3"""
"""
Módulo de signos vitales — lógica de negocio (CRUD completo).
Basado estrictamente en el diagrama de BD del equipo (tabla: signos_vitales).

Columnas de la tabla:
    id, id_residente, fecha, frecuencia_cardiaca, presion, oxigenacion,
    glucosa, temperatura, panales_usados, orino, evacuo, sueno,
    observaciones, id_enfermero

    id_enfermero referencia a usuarios.id (rol enfermero o doctor).

Funciones públicas:
    crear_registro(datos: dict) -> int
    obtener_registro(id: int)
    listar_registros() -> list
    listar_por_residente(id_residente: int) -> list
    listar_por_fecha(fecha: str) -> list
    buscar_registros(texto: str) -> list
    actualizar_registro(id: int, datos: dict) -> bool
    eliminar_registro(id: int) -> bool

    obtener_ultimo_registro(id_residente: int)
    obtener_historial_residente(id_residente: int) -> list
"""

from db.connection import get_connection


CAMPOS_VALIDOS = {
    "id_residente",
    "fecha",
    "frecuencia_cardiaca",
    "presion",
    "oxigenacion",
    "glucosa",
    "temperatura",
    "panales_usados",
    "orino",
    "evacuo",
    "sueno",
    "observaciones",
    "id_enfermero",
}


def _filtrar_campos(datos: dict) -> dict:
    return {k: v for k, v in datos.items() if k in CAMPOS_VALIDOS}


def _validar_requeridos(campos: dict):
    requeridos = {"id_residente", "fecha", "id_enfermero"}
    faltantes = requeridos - set(campos.keys())
    if faltantes:
        raise ValueError(f"Faltan campos requeridos: {', '.join(sorted(faltantes))}")


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────
def crear_registro(datos: dict) -> int:
    """
    Inserta un nuevo registro de signos vitales.
    Returns: id del registro creado.
    """
    campos = _filtrar_campos(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos.")

    _validar_requeridos(campos)

    columnas     = ", ".join(campos.keys())
    placeholders = ", ".join(["?"] * len(campos))
    valores      = list(campos.values())

    sql = f"INSERT INTO signos_vitales ({columnas}) VALUES ({placeholders})"

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
def obtener_registro(id: int):
    """
    Retorna un registro por ID con datos del residente y usuario (enfermero/doctor).
    Retorna None si no existe.
    """
    sql = """
        SELECT  sv.*,
                r.nombre   AS residente_nombre,
                r.curp     AS residente_curp,
                u.nombre   AS enfermero_nombre,
                u.rol      AS enfermero_rol
        FROM signos_vitales sv
        LEFT JOIN residentes r ON sv.id_residente = r.id_residente
        LEFT JOIN usuarios u   ON sv.id_enfermero = u.id
        WHERE sv.id = ?
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id,)).fetchone()
    finally:
        conn.close()


def listar_registros() -> list:
    """
    Lista todos los registros de signos vitales con nombres de residente y usuario.
    """
    sql = """
        SELECT  sv.id,
                sv.fecha,
                sv.id_residente,
                r.nombre   AS residente_nombre,
                sv.frecuencia_cardiaca,
                sv.presion,
                sv.oxigenacion,
                sv.glucosa,
                sv.temperatura,
                sv.panales_usados,
                sv.orino,
                sv.evacuo,
                sv.sueno,
                sv.observaciones,
                sv.id_enfermero,
                u.nombre   AS enfermero_nombre,
                u.rol      AS enfermero_rol
        FROM signos_vitales sv
        LEFT JOIN residentes r ON sv.id_residente = r.id_residente
        LEFT JOIN usuarios u   ON sv.id_enfermero = u.id
        ORDER BY sv.fecha DESC, r.nombre ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def listar_por_residente(id_residente: int) -> list:
    """
    Lista todos los registros de signos vitales de un residente, más recientes primero.
    """
    sql = """
        SELECT  sv.id,
                sv.fecha,
                sv.frecuencia_cardiaca,
                sv.presion,
                sv.oxigenacion,
                sv.glucosa,
                sv.temperatura,
                sv.panales_usados,
                sv.orino,
                sv.evacuo,
                sv.sueno,
                sv.observaciones,
                sv.id_enfermero,
                u.nombre AS enfermero_nombre,
                u.rol    AS enfermero_rol
        FROM signos_vitales sv
        LEFT JOIN usuarios u ON sv.id_enfermero = u.id
        WHERE sv.id_residente = ?
        ORDER BY sv.fecha DESC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_residente,)).fetchall()
    finally:
        conn.close()


def listar_por_fecha(fecha: str) -> list:
    """
    Lista todos los registros de una fecha específica (formato YYYY-MM-DD).
    """
    sql = """
        SELECT  sv.id,
                sv.fecha,
                sv.id_residente,
                r.nombre   AS residente_nombre,
                sv.frecuencia_cardiaca,
                sv.presion,
                sv.oxigenacion,
                sv.glucosa,
                sv.temperatura,
                sv.panales_usados,
                sv.orino,
                sv.evacuo,
                sv.sueno,
                sv.observaciones,
                u.nombre   AS enfermero_nombre,
                u.rol      AS enfermero_rol
        FROM signos_vitales sv
        LEFT JOIN residentes r ON sv.id_residente = r.id_residente
        LEFT JOIN usuarios u   ON sv.id_enfermero = u.id
        WHERE sv.fecha = ?
        ORDER BY r.nombre ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (fecha,)).fetchall()
    finally:
        conn.close()


def buscar_registros(texto: str) -> list:
    """
    Busca registros por nombre de residente, fecha u observaciones.
    """
    patron = f"%{texto.strip()}%"
    sql = """
        SELECT  sv.id,
                sv.fecha,
                r.nombre   AS residente_nombre,
                sv.frecuencia_cardiaca,
                sv.presion,
                sv.oxigenacion,
                sv.glucosa,
                sv.temperatura,
                sv.observaciones,
                u.nombre   AS enfermero_nombre
        FROM signos_vitales sv
        LEFT JOIN residentes r ON sv.id_residente = r.id_residente
        LEFT JOIN usuarios u   ON sv.id_enfermero = u.id
        WHERE r.nombre        LIKE ?
           OR sv.fecha         LIKE ?
           OR sv.observaciones LIKE ?
        ORDER BY sv.fecha DESC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (patron, patron, patron)).fetchall()
    finally:
        conn.close()


def obtener_ultimo_registro(id_residente: int):
    """
    Retorna el registro más reciente de un residente.
    Útil para mostrar el estado actual en la ficha del residente.
    Retorna None si no tiene registros.
    """
    sql = """
        SELECT  sv.*,
                u.nombre AS enfermero_nombre,
                u.rol    AS enfermero_rol
        FROM signos_vitales sv
        LEFT JOIN usuarios u ON sv.id_enfermero = u.id
        WHERE sv.id_residente = ?
        ORDER BY sv.fecha DESC
        LIMIT 1
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (id_residente,)).fetchone()
    finally:
        conn.close()


def obtener_historial_residente(id_residente: int) -> list:
    """
    Historial completo de signos vitales de un residente.
    Alias semántico de listar_por_residente para uso en pantalla de historial.
    """
    return listar_por_residente(id_residente)


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────
def actualizar_registro(id: int, datos: dict) -> bool:
    """
    Actualiza campos de un registro de signos vitales.
    Returns: True si se actualizó, False si no existe.
    """
    campos = _filtrar_campos(datos)
    if not campos:
        raise ValueError("No se proporcionaron campos válidos para actualizar.")

    set_clause = ", ".join([f"{k} = ?" for k in campos.keys()])
    valores    = list(campos.values()) + [id]

    sql = f"UPDATE signos_vitales SET {set_clause} WHERE id = ?"

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
def eliminar_registro(id: int) -> bool:
    """
    Elimina un registro de signos vitales por su ID.
    Returns: True si se eliminó, False si no existía.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM signos_vitales WHERE id = ?",
            (id,)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()