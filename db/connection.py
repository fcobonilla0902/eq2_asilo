import sqlite3
import os
import sys


def _get_app_dir() -> str:
    """
    Devuelve la carpeta donde vive la aplicación.

    - Cuando se ejecuta como .exe empaquetado con PyInstaller,
      sys.executable apunta al .exe y su carpeta ES la raíz del programa.
    - Cuando se ejecuta como script normal (python main.py),
      usamos la ruta de este archivo para localizar la raíz del proyecto.
    """
    if getattr(sys, "frozen", False):
        # Ejecutando dentro de un .exe de PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Ejecutando como script: subimos dos niveles desde db/connection.py
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


APP_DIR = _get_app_dir()
DB_PATH = os.path.join(APP_DIR, "asilo.db")


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