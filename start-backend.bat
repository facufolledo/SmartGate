@echo off
echo ==========================================
echo        SMARTGATE - INICIAR BACKEND
echo ==========================================
echo.

cd backend

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Iniciando servidor FastAPI...
echo.
echo 🌐 API disponible en: http://localhost:8000
echo 📚 Documentación en: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
