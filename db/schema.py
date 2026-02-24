"""
Inicializa todas las tablas de la BD si no existen.
Basado estrictamente en el diagrama del equipo.
Llamar a init_db() una sola vez al arrancar la app (en main.py).
"""
from db.connection import get_connection


SCHEMA = """
-- Tabla: familiares
CREATE TABLE IF NOT EXISTS familiares (
    id_familiar     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT,
    telefono        TEXT,
    foto_ine        TEXT
);

-- Tabla: habitaciones
CREATE TABLE IF NOT EXISTS habitaciones (
    id_habitacion   INTEGER PRIMARY KEY AUTOINCREMENT,
    numero          TEXT,
    tipo            TEXT
);

-- Tabla: residentes
CREATE TABLE IF NOT EXISTS residentes (
    id_residente                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre                      TEXT,
    curp                        TEXT,
    edad                        INTEGER,
    complexion                  TEXT,
    color_ojos                  TEXT,
    tipo_nariz                  TEXT,
    tez_piel                    TEXT,
    tipo_ceja                   TEXT,
    tipo_sangre                 TEXT,
    cartilla_salud              TEXT,
    comprobante_servicio_medico TEXT,
    habitacion_id               INTEGER REFERENCES habitaciones(id_habitacion),
    id_familiar                 INTEGER REFERENCES familiares(id_familiar),
    foto_ine                    TEXT,
    foto_comprobante_domicilio  TEXT,
    foto_acta_nacimiento        TEXT,
    fecha_registro              TEXT
);

-- Tabla: enfermeros
CREATE TABLE IF NOT EXISTS enfermeros (
    id_enfermero    INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT,
    telefono        TEXT,
    curp            TEXT
);

-- Tabla: usuarios_admin
CREATE TABLE IF NOT EXISTS usuarios_admin (
    id_admin        INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario         TEXT,
    password_hash   TEXT
);

-- Tabla: medicaciones
CREATE TABLE IF NOT EXISTS medicaciones (
    id_medicacion   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_residente    INTEGER REFERENCES residentes(id_residente),
    dosis           TEXT,
    horario         TEXT,
    fecha           TEXT,
    id_enfermero    INTEGER REFERENCES enfermeros(id_enfermero)
);

-- Tabla: actividades
CREATE TABLE IF NOT EXISTS actividades (
    id_actividad        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre              TEXT,
    es_fija             TEXT,
    fecha_programada    TEXT,
    hora_programada     TEXT
);

-- Tabla: actividad_residente
CREATE TABLE IF NOT EXISTS actividad_residente (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    id_residente    INTEGER REFERENCES residentes(id_residente),
    id_actividad    INTEGER REFERENCES actividades(id_actividad),
    fecha           TEXT,
    hora            TEXT,
    participo       INTEGER
);

-- Tabla: signos_vitales
CREATE TABLE IF NOT EXISTS signos_vitales (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_residente        INTEGER REFERENCES residentes(id_residente),
    fecha               TEXT,
    frecuencia_cardiaca INTEGER,
    presion             TEXT,
    oxigenacion         INTEGER,
    glucosa             INTEGER,
    temperatura         REAL,
    panales_usados      INTEGER,
    orino               INTEGER,
    evacuo              INTEGER,
    sueno               TEXT,
    observaciones       TEXT,
    id_enfermero        INTEGER REFERENCES enfermeros(id_enfermero)
);
"""


def init_db():
    """Crea todas las tablas si no existen. Seguro llamarlo múltiples veces."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        print("[DB] Schema inicializado correctamente.")
    except Exception as e:
        print(f"[DB] Error al inicializar schema: {e}")
    finally:
        conn.close()