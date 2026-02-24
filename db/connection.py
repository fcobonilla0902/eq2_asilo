import sqlite3
import os

# La BD se guarda en la raíz del proyecto como asilo.db
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "asilo.db")


def get_connection() -> sqlite3.Connection:
    """Retorna una conexión a la BD con row_factory para acceder por nombre de columna."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_cursor():
    """Retorna (conn, cursor). Recuerda llamar conn.commit() y conn.close()."""
    conn = get_connection()
    return conn, conn.cursor()
