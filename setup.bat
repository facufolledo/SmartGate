@echo off
echo ==========================================
echo    SMARTGATE - CONFIGURACION AUTOMATICA
echo ==========================================
echo.

echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)
echo ✅ Python encontrado

echo.
echo [2/6] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js no encontrado. Por favor instala Node.js 16+ desde https://nodejs.org
    pause
    exit /b 1
)
echo ✅ Node.js encontrado

echo.
echo [3/6] Configurando Backend...
cd backend

echo    Creando entorno virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Error creando entorno virtual
    pause
    exit /b 1
)

echo    Activando entorno virtual...
call venv\Scripts\activate.bat

echo    Instalando dependencias de Python...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias de Python
    pause
    exit /b 1
)

echo    Configurando variables de entorno...
if not exist .env (
    copy ..\env.example .env
    echo ✅ Archivo .env creado desde env.example
    echo ⚠️  IMPORTANTE: Edita el archivo backend\.env con tus configuraciones de base de datos
) else (
    echo ✅ Archivo .env ya existe
)

echo    Creando directorio de modelos...
if not exist models mkdir models
echo ✅ Directorio models creado

echo.
echo [4/6] Configurando Frontend...
cd ..\frontend

echo    Instalando dependencias de Node.js...
npm install
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias de Node.js
    pause
    exit /b 1
)

echo.
echo [5/6] Verificando estructura...
cd ..
if not exist backend\main.py (
    echo ❌ Archivo backend\main.py no encontrado
    pause
    exit /b 1
)
if not exist frontend\src\App.js (
    echo ❌ Archivo frontend\src\App.js no encontrado
    pause
    exit /b 1
)
echo ✅ Estructura del proyecto verificada

echo.
echo [6/6] Descargando modelos YOLO...
cd backend
call venv\Scripts\activate.bat

echo    Descargando yolov8n.pt...
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Advertencia: No se pudo descargar yolov8n.pt automáticamente
    echo    Puedes descargarlo manualmente desde: https://github.com/ultralytics/assets/releases
)

echo.
echo ==========================================
echo           CONFIGURACION COMPLETADA
echo ==========================================
echo.
echo ✅ Backend configurado en: backend\
echo ✅ Frontend configurado en: frontend\
echo ✅ Entorno virtual creado en: backend\venv\
echo.
echo 📋 SIGUIENTES PASOS:
echo.
echo 1. Configurar base de datos MySQL:
echo    - Crear base de datos 'smartgate'
echo    - Editar backend\.env con tus credenciales
echo    - Ejecutar scripts SQL en backend\sql\
echo.
echo 2. Configurar cámara:
echo    - Para cámara USB: editar CAMERA_INDEX en .env
echo    - Para DroidCam: configurar CAMERA_URL en .env
echo.
echo 3. Ejecutar el sistema:
echo    - Backend: cd backend ^&^& venv\Scripts\activate ^&^& python -m uvicorn main:app --reload
echo    - Frontend: cd frontend ^&^& npm start
echo.
echo 4. Acceder a:
echo    - Frontend: http://localhost:3000
echo    - API: http://localhost:8000
echo.
echo 📖 Para más información, consulta el README.md
echo.
pause
