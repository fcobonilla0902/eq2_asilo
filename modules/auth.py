"""
Módulo de autenticación — Sistema de roles y permisos.
Roles: admin, enfermero, doctor
"""
import hashlib
from db.connection import get_connection

# ── Permisos por rol ──────────────────────────────────────────────────────────
PERMISOS = {
    "admin": {
        "residentes":     True,
        "medicaciones":   True,
        "habitaciones":   True,
        "enfermeros":     True,
        "signos_vitales": True,
        "actividades":    True,
        "usuarios":       True,
        "respaldo":       True,
    },
    "enfermero": {
        "residentes":     True,
        "medicaciones":   True,
        "habitaciones":   False,
        "enfermeros":     False,
        "signos_vitales": True,
        "actividades":    True,
        "usuarios":       False,
        "respaldo":       False,
    },
    "doctor": {
        "residentes":     True,
        "medicaciones":   True,
        "habitaciones":   False,
        "enfermeros":     False,
        "signos_vitales": True,
        "actividades":    False,
        "usuarios":       False,
        "respaldo":       False,
    },
}

_sesion_activa: dict | None = None


def inicializar_modulo_auth():
    """Crea la tabla unificada de usuarios y siembra datos de prueba."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario        TEXT UNIQUE NOT NULL,
            password_hash  TEXT NOT NULL,
            rol            TEXT NOT NULL CHECK(rol IN ('admin','enfermero','doctor')),
            nombre         TEXT NOT NULL DEFAULT '',
            telefono       TEXT DEFAULT '',
            activo         INTEGER DEFAULT 1,
            fecha_creacion TEXT DEFAULT (date('now'))
        )
    """)

    # Solo sembrar si no hay ningún usuario aún
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        semilla = [
            ("admin",      pw, "admin",     "Administrador",    "8110000001"),
            ("enfermero1", pw, "enfermero", "María García",     "8110000002"),
            ("doctor1",    pw, "doctor",    "Dr. Carlos López", "8110000003"),
        ]
        for usuario, ph, rol, nombre, telefono in semilla:
            try:
                cursor.execute(
                    "INSERT INTO usuarios (usuario, password_hash, rol, nombre, telefono) VALUES (?,?,?,?,?)",
                    (usuario, ph, rol, nombre, telefono),
                )
            except Exception:
                pass

    conn.commit()
    conn.close()


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def validar_usuario(usuario: str, password: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, usuario, rol, nombre, telefono FROM usuarios "
        "WHERE usuario = ? AND password_hash = ? AND activo = 1",
        (usuario, _hash(password)),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "usuario": row["usuario"],
                "rol": row["rol"], "nombre": row["nombre"], "telefono": row["telefono"]}
    return None


def iniciar_sesion(datos_usuario: dict):
    global _sesion_activa
    _sesion_activa = datos_usuario


def cerrar_sesion():
    global _sesion_activa
    _sesion_activa = None


def get_sesion() -> dict | None:
    return _sesion_activa


def get_rol() -> str | None:
    return _sesion_activa["rol"] if _sesion_activa else None


def tiene_permiso(modulo: str) -> bool:
    rol = get_rol()
    if rol is None:
        return False
    return PERMISOS.get(rol, {}).get(modulo, False)


def listar_usuarios() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, rol, nombre, telefono, activo FROM usuarios ORDER BY id")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def crear_usuario(usuario: str, password: str, rol: str, nombre: str, telefono: str = "") -> bool:
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO usuarios (usuario, password_hash, rol, nombre, telefono) VALUES (?,?,?,?,?)",
            (usuario, _hash(password), rol, nombre, telefono),
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def cambiar_password(id_usuario: int, nueva_password: str) -> bool:
    try:
        conn = get_connection()
        conn.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?",
                     (_hash(nueva_password), id_usuario))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def toggle_activo(id_usuario: int) -> bool:
    try:
        conn = get_connection()
        conn.execute(
            "UPDATE usuarios SET activo = CASE WHEN activo=1 THEN 0 ELSE 1 END WHERE id = ?",
            (id_usuario,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False