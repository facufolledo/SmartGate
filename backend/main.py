from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.general import router as general_router
from routers.cocheras import router as cocheras_router
from routers.auth import router as auth_router
from routers.auto_access import router as auto_access_router

app = FastAPI()

app.include_router(general_router)
app.include_router(cocheras_router)
app.include_router(auth_router)
app.include_router(auto_access_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)