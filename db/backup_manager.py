"""
Motor de respaldo y restauración para asilo.db.
Usa sqlite3.backup() para copias seguras mientras la app está activa.
"""
import sqlite3
import shutil
import gzip
import os
import logging
import threading
import time
from datetime import datetime
from pathlib import Path

from db.connection import DB_PATH


# Carpeta de respaldos: mismo nivel que asilo.db → <raiz>/backups/
BASE_DIR = Path(DB_PATH).parent
BACKUP_DIR = BASE_DIR / "backups"
MAX_BACKUPS = 15          # máximo de archivos .db.gz conservados
INTERVAL_HORAS = 6.0      # respaldo automático cada 6 horas

# ── Logger dedicado ──────────────────────────────────────────────────────────
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
_log = logging.getLogger("BackupManager")
if not _log.handlers:
    fh = logging.FileHandler(BACKUP_DIR / "backup.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s  %(levelname)s  %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S"))
    _log.addHandler(fh)
    _log.setLevel(logging.INFO)


# ════════════════════════════════════════════════════════════════════════════
class BackupManager:
    """Crea, rota y restaura respaldos de asilo.db."""

    def __init__(self,
                 db_path: str = DB_PATH,
                 backup_dir: Path = BACKUP_DIR,
                 max_backups: int = MAX_BACKUPS):
        self.db_path   = Path(db_path)
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # ── Crear respaldo ───────────────────────────────────────────────────────
    def crear_respaldo(self, etiqueta: str = "") -> Path | None:
        """
        Copia la BD activa de forma segura con sqlite3.backup() y la
        comprime con gzip.  Devuelve la ruta del archivo creado, o None
        si ocurrió un error.
        """
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        sufx = f"_{etiqueta}" if etiqueta else ""
        nombre = f"respaldo_{ts}{sufx}.db.gz"
        ruta   = self.backup_dir / nombre
        tmp    = ruta.with_suffix("")           # archivo .db temporal

        try:
            src  = sqlite3.connect(self.db_path)
            dst  = sqlite3.connect(tmp)
            src.backup(dst, pages=200)          # copia consistente por páginas
            dst.close()
            src.close()

            # Comprimir el .db temporal → .db.gz
            with open(tmp, "rb") as fi, gzip.open(ruta, "wb") as fo:
                shutil.copyfileobj(fi, fo)
            tmp.unlink()

            _log.info(f"Respaldo creado: {nombre}")
            self._rotar()
            return ruta

        except Exception as exc:
            _log.error(f"Error al crear respaldo: {exc}")
            if tmp.exists():
                tmp.unlink(missing_ok=True)
            return None

    # ── Rotación ─────────────────────────────────────────────────────────────
    def _rotar(self):
        """Elimina los respaldos más viejos cuando se supera max_backups."""
        archivos = sorted(self.backup_dir.glob("respaldo_*.db.gz"))
        while len(archivos) > self.max_backups:
            viejo = archivos.pop(0)
            viejo.unlink()
            _log.info(f"Rotado (eliminado): {viejo.name}")

    # ── Listar respaldos ─────────────────────────────────────────────────────
    def listar_respaldos(self) -> list[dict]:
        """Devuelve los respaldos disponibles, del más reciente al más antiguo."""
        resultado = []
        for f in sorted(self.backup_dir.glob("respaldo_*.db.gz"), reverse=True):
            st = f.stat()
            resultado.append({
                "path":     f,
                "nombre":   f.name,
                "tamano_kb": round(st.st_size / 1024, 1),
                "fecha":    datetime.fromtimestamp(st.st_mtime).strftime("%d/%m/%Y  %H:%M"),
            })
        return resultado

    # ── Restaurar ────────────────────────────────────────────────────────────
    def restaurar(self, ruta_respaldo: Path) -> bool:
        """
        Restaura un respaldo sobre asilo.db.
        Crea automáticamente un respaldo de seguridad antes de sobrescribir.
        """
        try:
            # 1. Guardar respaldo de seguridad
            self.crear_respaldo(etiqueta="pre_restauracion")

            tmp = self.backup_dir / "_tmp_restaurar.db"

            # 2. Descomprimir
            with gzip.open(ruta_respaldo, "rb") as fi, open(tmp, "wb") as fo:
                shutil.copyfileobj(fi, fo)

            # 3. Reemplazar BD activa
            shutil.copy2(tmp, self.db_path)
            tmp.unlink()

            _log.info(f"Restauración exitosa desde: {ruta_respaldo.name}")
            return True

        except Exception as exc:
            _log.error(f"Error al restaurar: {exc}")
            return False


# ════════════════════════════════════════════════════════════════════════════
class BackupScheduler:
    """
    Hilo daemon que dispara respaldos automáticos en segundo plano.
    No bloquea la UI.
    """

    def __init__(self,
                 manager: BackupManager,
                 intervalo_horas: float = INTERVAL_HORAS):
        self._mgr      = manager
        self._intervalo = intervalo_horas * 3600
        self._stop     = threading.Event()
        self._hilo: threading.Thread | None = None

    def iniciar(self):
        """Arranca el scheduler (llamar en main.py después de init_db)."""
        self._hilo = threading.Thread(target=self._ciclo, daemon=True,
                                      name="BackupScheduler")
        self._hilo.start()
        _log.info(f"Scheduler iniciado — intervalo: {INTERVAL_HORAS}h")

    def detener(self):
        self._stop.set()

    def respaldar_al_salir(self):
        """Llama esto antes de cerrar la app para guardar el estado final."""
        self.detener()
        self._mgr.crear_respaldo(etiqueta="cierre")

    def _ciclo(self):
        while not self._stop.wait(self._intervalo):
            self._mgr.crear_respaldo(etiqueta="auto")


# ── Instancia global (importable desde cualquier módulo) ─────────────────────
backup_manager   = BackupManager()
backup_scheduler = BackupScheduler(backup_manager)
