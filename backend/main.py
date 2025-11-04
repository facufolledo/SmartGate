from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routers.general import router as general_router
from routers.cocheras import router as cocheras_router
from routers.auth import router as auth_router
from routers.auto_access import router as auto_access_router

app = FastAPI()

app.include_router(general_router)
app.include_router(cocheras_router)
app.include_router(auth_router)
app.include_router(auto_access_router)

# Configurar CORS para producción
# En desarrollo permite localhost, en producción permite el dominio de Netlify
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# Agregar origen de Netlify si está configurado
netlify_url = os.getenv("NETLIFY_URL")
if netlify_url:
    allowed_origins.append(netlify_url)

# Para producción, permitir todos los orígenes
# En producción real, deberías especificar tu dominio exacto de Netlify
# Por ejemplo: ["https://tu-app.netlify.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambia esto a los dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)