# asilo.spec  — versión corregida
# Coloca este archivo en eq2_asilo/ (junto a main.py) y ejecuta:
#   pyinstaller asilo.spec

import sys, os
from pathlib import Path

block_cipher = None

# ── Detectar la ruta real de customtkinter instalado ────────────────────────
import customtkinter
CTK_PATH = str(Path(customtkinter.__file__).parent)

added_files = [
    (CTK_PATH, "customtkinter"),   # incluye temas, widgets, imágenes
]

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        "customtkinter",
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.filedialog",
        "PIL",
        "PIL.Image",
        "PIL.ImageTk",
        "PIL.ImageDraw",
        "reportlab",
        "reportlab.pdfgen",
        "reportlab.pdfgen.canvas",
        "reportlab.lib",
        "reportlab.lib.pagesizes",
        "reportlab.lib.styles",
        "reportlab.lib.units",
        "reportlab.platypus",
        "openpyxl",
        "db",
        "db.connection",
        "db.schema",
        "db.backup_manager",
        "modules",
        "modules.auth",
        "modules.habitaciones",
        "modules.residentes",
        "modules.medicacion",
        "modules.actividades",
        "modules.signos_vitales",
        "reports",
        "reports.generador",
        "utils",
        "utils.helpers",
        "ui",
        "ui.screens",
        "ui.screens.login",
        "ui.screens.dashboard",
        "ui.screens.habitaciones_screen",
        "ui.screens.residentes_screen",
        "ui.screens.medicacion_screen",
        "ui.screens.actividades_screen",
        "ui.screens.signos_vitales_screen",
        "ui.screens.usuarios_screen",
        "ui.screens.respaldo_screen",
        "sqlite3",
        "hashlib",
        "gzip",
        "shutil",
        "threading",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "unittest", "test"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Asilo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Asilo",
)
