from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import timedelta
from db import (
    authenticate_user, 
    create_access_token, 
    verify_token, 
    get_user_by_username,
    create_user,
    get_all_users,
    update_last_login,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    nombre: str
    rol: str = "ope"

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: dict

# Función para obtener el usuario actual
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Función para verificar si es administrador
def get_current_admin(current_user = Depends(get_current_user)):
    if current_user["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador"
        )
    return current_user

@router.post("/login", response_model=Token)
def login(data: LoginRequest):
    """Endpoint para autenticar usuarios y obtener token JWT"""
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si el usuario está activo
    if not user.get("activo", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    # Actualizar último login
    update_last_login(user["username"])
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # Información del usuario (sin contraseña)
    user_info = {
        "id": user["id_usuario"],
        "username": user["username"],
        "nombre": user["nombre"],
        "rol": user["rol"],
        "primer_login": user.get("primer_login", True)
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": user_info
    }

@router.get("/me")
def get_current_user_info(current_user = Depends(get_current_user)):
    """Obtiene información del usuario actual"""
    return {
        "id": current_user["id_usuario"],
        "username": current_user["username"],
        "nombre": current_user["nombre"],
        "rol": current_user["rol"],
        "activo": current_user["activo"]
    }

@router.post("/register")
def register_user(data: UserCreate, current_admin = Depends(get_current_admin)):
    """Registra un nuevo usuario (solo administradores)"""
    result = create_user(
        username=data.username,
        password=data.password,
        nombre=data.nombre,
        rol=data.rol
    )
    
    if result["success"]:
        return {"message": result["message"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.get("/users")
def get_users(current_admin = Depends(get_current_admin)):
    """Obtiene lista de todos los usuarios (solo administradores)"""
    users = get_all_users()
    return {"users": users}

@router.get("/verify-token")
def verify_token_endpoint(current_user = Depends(get_current_user)):
    """Verifica si el token es válido"""
    return {"valid": True, "user": current_user}
