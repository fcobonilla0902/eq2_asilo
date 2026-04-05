@echo off
:: ============================================================
::  compilar.bat — Empaqueta el Sistema Asilo como .exe
::  Ejecuta este archivo desde la carpeta eq2_asilo/
:: ============================================================

title Compilando Sistema Asilo...
echo.
echo  =========================================
echo   Sistema de Gestion - Asilo
echo   Empaquetador automatico con PyInstaller
echo  =========================================
echo.

:: 1) Verificar que Python este instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python no encontrado.
    echo  Descargalo en https://www.python.org/downloads/
    echo  Asegurate de marcar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

:: 2) Instalar/actualizar dependencias
echo  [1/4] Instalando dependencias...
pip install customtkinter Pillow reportlab openpyxl pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo  [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)
echo        OK

:: 3) Limpiar compilaciones anteriores
echo  [2/4] Limpiando compilaciones anteriores...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
echo        OK

:: 4) Compilar
echo  [3/4] Compilando... (puede tardar 1-3 minutos)
pyinstaller asilo.spec
if errorlevel 1 (
    echo.
    echo  [ERROR] Fallo la compilacion. Revisa los mensajes de arriba.
    pause
    exit /b 1
)

:: 5) Copiar archivos de datos necesarios junto al .exe
echo  [4/4] Copiando base de datos y carpetas...

:: Base de datos inicial
if exist asilo.db (
    copy /y asilo.db dist\Asilo\asilo.db >nul
    echo        Copiado: asilo.db
)

:: Carpeta de uploads (fotos de residentes)
if exist uploads (
    xcopy /e /i /q uploads dist\Asilo\uploads >nul
    echo        Copiado: uploads\
)

:: Crear carpeta backups vacia si no existe
if not exist dist\Asilo\backups mkdir dist\Asilo\backups
echo        Creado: backups\

echo.
echo  =========================================
echo   LISTO! La aplicacion esta en:
echo.
echo   dist\Asilo\Asilo.exe
echo.
echo   Puedes copiar toda la carpeta dist\Asilo\
echo   a cualquier computadora con Windows.
echo  =========================================
echo.
pause
