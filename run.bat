@echo off
REM =============================================================================
REM SigmaOps - Script de instalación y ejecución (Windows)
REM =============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================
echo   SigmaOps - Sistema de Tickets
echo ========================================
echo.

if "%1"=="" goto run
if "%1"=="setup" goto setup
if "%1"=="run" goto run
if "%1"=="run-prod" goto run_prod
if "%1"=="help" goto help
if "%1"=="-h" goto help

echo Comando desconocido: %1
goto help

:setup
echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    exit /b 1
)

echo.
echo [2/4] Creando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el ambiente virtual
    exit /b 1
)

echo.
echo [3/4] Activando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo [4/4] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================
echo   Instalacion completada!
echo ========================================
echo.
echo Recuerda configurar el archivo .env con tus credenciales de BD
echo Luego ejecuta: run.bat
echo.
goto end

:run
echo Iniciando servidor de desarrollo...
echo.

if not exist "venv" (
    echo ERROR: Ambiente virtual no encontrado.
    echo Ejecuta primero: run.bat setup
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist ".env" (
    echo Advertencia: Archivo .env no encontrado, copiando desde .env.example
    copy .env.example .env
)

echo.
echo Servidor disponible en: http://127.0.0.1:8000
echo Presiona Ctrl+C para detener
echo.
python manage.py runserver 127.0.0.1:8000
goto end

:run_prod
echo Iniciando servidor de produccion...
echo.

if not exist "venv" (
    echo ERROR: Ambiente virtual no encontrado.
    echo Ejecuta primero: run.bat setup
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist ".env" (
    echo ERROR: Archivo .env no encontrado
    exit /b 1
)

echo Recolectando archivos estaticos...
python manage.py collectstatic --noinput

echo.
echo Servidor disponible en: http://0.0.0.0:8000
echo.
venv\Scripts\gunicorn.exe --bind 0.0.0.0:8000 --workers 3 sigmaops.wsgi:application
goto end

:help
echo.
echo Uso: run.bat [comando]
echo.
echo Comandos:
echo   setup          Instala ambiente virtual y dependencias
echo   run            Ejecuta en modo desarrollo (default)
echo   run-prod       Ejecuta en modo produccion con Gunicorn
echo   help           Muestra esta ayuda
echo.
goto end

:end
endlocal
