# auth_router.py
from typing import Any, Dict, Optional, List, Annotated
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from db import (
    authenticate_user,
    create_access_token,
    verify_token,
    get_user_by_username,
    create_user,
    get_all_users,
    update_last_login,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# --- Modelos ------------------------------
class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=4, max_length=128)

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    nombre: str = Field(min_length=1, max_length=120)
    rol: str = Field(default="ope", pattern="^(ope|admin)$")

class UserInfo(BaseModel):
    id: int
    username: str
    nombre: str
    rol: str
    primer_login: bool = True
    activo: Optional[bool] = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: UserInfo

class Message(BaseModel):
    message: str

class UsersResponse(BaseModel):
    users: List[Dict[str, Any]]

# --- Seguridad ----------------------------
security = HTTPBearer(auto_error=False)

def _raise_unauthorized(detail: str = "No autorizado"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

def _require_bearer(credentials: Optional[HTTPAuthorizationCredentials]) -> str:
    if credentials is None or not credentials.credentials:
        _raise_unauthorized("Falta el token")
    if credentials.scheme.lower() != "bearer":
        _raise_unauthorized("Esquema inválido, use Bearer")
    return credentials.credentials

# Usuario actual desde token
def get_current_user(credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]):
    token = _require_bearer(credentials)
    username = verify_token(token)
    if not username:
        _raise_unauthorized("Token inválido o expirado")

    user = get_user_by_username(username)
    if not user:
        _raise_unauthorized("Usuario no encontrado")
    if user.get("activo") is False:
        _raise_unauthorized("Usuario inactivo")

    return user

# Verificación de admin
def get_current_admin(current_user: Annotated[Dict[str, Any], Depends(get_current_user)]):
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador",
        )
    return current_user

# --- Endpoints ----------------------------
@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(data: LoginRequest):
    """Autentica y entrega un JWT firmado (HS256) con claim 'sub'."""
    user = authenticate_user(data.username, data.password)
    if not user:
        _raise_unauthorized("Credenciales incorrectas")

    if user.get("activo") is False:
        _raise_unauthorized("Usuario inactivo")

    try:
        update_last_login(user["username"])
    except Exception:
        pass

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

    user_info = UserInfo(
        id=user["id_usuario"],
        username=user["username"],
        nombre=user["nombre"],
        rol=user["rol"],
        primer_login=user.get("primer_login", True),
        activo=user.get("activo", True),
    )
    return Token(access_token=access_token, user_info=user_info)

@router.get("/me", response_model=UserInfo)
def get_current_user_info(current_user: Annotated[Dict[str, Any], Depends(get_current_user)]):
    """Información del usuario actual (derivada del token)."""
    return UserInfo(
        id=current_user["id_usuario"],
        username=current_user["username"],
        nombre=current_user["nombre"],
        rol=current_user["rol"],
        primer_login=current_user.get("primer_login", True),
        activo=current_user.get("activo", True),
    )

@router.post("/register", response_model=Message, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, current_admin: Annotated[Dict[str, Any], Depends(get_current_admin)]):
    """Crea usuarios (solo admin)."""
    result = create_user(
        username=data.username,
        password=data.password,
        nombre=data.nombre,
        rol=data.rol,
    )
    if result.get("success"):
        return Message(message=result.get("message", "Usuario creado"))
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message", "Error al crear usuario"))

@router.get("/users", response_model=UsersResponse)
def get_users(current_admin: Annotated[Dict[str, Any], Depends(get_current_admin)]):
    """Lista de usuarios (solo admin)."""
    users = get_all_users()
    return UsersResponse(users=users)

@router.get("/verify-token")
def verify_token_endpoint(current_user: Annotated[Dict[str, Any], Depends(get_current_user)]):
    """Devuelve válido si el token está correcto."""
    return {"valid": True, "user": {
        "id": current_user["id_usuario"],
        "username": current_user["username"],
        "rol": current_user["rol"]
    }}

# --- Diagnóstico (deshabilitar en producción) ----------------------------
@router.get("/test-user/{username}")
def test_user(username: str):
    """Endpoint de diagnóstico para revisar un usuario y el hash de password."""
    from db import get_connection, table_name, DB_SCHEMA
    from psycopg2.extras import RealDictCursor

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"SELECT * FROM {table_name('usuarios')} WHERE username = %s", (username,))
        user = cur.fetchone()

        if user:
            user_dict = dict(user)
            password_hash = user_dict.get("password_hash") or ""
            hash_valid = password_hash.startswith("$2b$") or password_hash.startswith("$2a$")
            if "password_hash" in user_dict:
                ph = user_dict["password_hash"]
                user_dict["password_hash"] = (ph[:30] + "...") if isinstance(ph, str) and len(ph) > 30 else ph

            info = {
                "encontrado": True,
                "usuario": user_dict,
                "schema_usado": DB_SCHEMA,
                "campos_disponibles": list(user_dict.keys()),
                "diagnostico": {
                    "activo": user_dict.get("activo", False),
                    "hash_valido": hash_valid,
                    "hash_longitud": len(password_hash),
                    "problemas": [],
                },
            }
            if user_dict.get("activo") is False:
                info["diagnostico"]["problemas"].append("Usuario INACTIVO (activo = FALSE)")
            if not hash_valid:
                info["diagnostico"]["problemas"].append("Password hash inválido (no es bcrypt)")
                info["diagnostico"]["solucion"] = "Ejecuta: python fix_user_password.py <username> <nueva_contraseña>"

            cur.close(); conn.close()
            return info

        cur.execute(f"SELECT username, nombre, rol, activo FROM {table_name('usuarios')} LIMIT 5")
        ejemplos = cur.fetchall()
        cur.close(); conn.close()
        return {
            "encontrado": False,
            "mensaje": f"Usuario '{username}' no encontrado en schema '{DB_SCHEMA}'",
            "ejemplos": [dict(e) for e in ejemplos] if ejemplos else [],
        }

    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc(), "schema_usado": DB_SCHEMA}

