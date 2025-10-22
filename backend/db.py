import mysql.connector
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

load_dotenv()

# Configuración para JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_aqui_cambiala_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

def tiene_permiso(matricula: str) -> bool:
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT estado FROM vehiculos WHERE matricula = %s"
        cursor.execute(query, (matricula,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is not None:
            return resultado[0] == 0
        else:
            return False
    except Exception as e:
        print("Error DB:", e)
        return False

def test_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        conn.close()
        return {"db_status": "Conexión exitosa"}
    except Exception as e:
        return {"db_status": "Error de conexión", "detail": str(e)}

# Funciones de autenticación adaptadas a tu estructura de tabla
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    """Autentica un usuario verificando sus credenciales"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Buscar usuario por username usando tu estructura de tabla
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return False
        
        # Verificar contraseña usando password_hash
        if not verify_password(password, user["password_hash"]):
            return False
        
        return user
    except Exception as e:
        print("Error en autenticación:", e)
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def get_user_by_username(username: str):
    """Obtiene información de un usuario por su username"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, username, nombre, rol, activo FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        print("Error obteniendo usuario:", e)
        return None

def create_user(username: str, password: str, nombre: str, rol: str = "ope"):
    """Crea un nuevo usuario en la base de datos"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id_usuario FROM usuarios WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "message": "El usuario ya existe"}
        
        # Crear nuevo usuario usando tu estructura de tabla
        hashed_password = get_password_hash(password)
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, nombre, rol, activo, primer_login) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, hashed_password, nombre, rol, True, True)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Usuario creado exitosamente"}
    except Exception as e:
        print("Error creando usuario:", e)
        return {"success": False, "message": f"Error: {str(e)}"}

def get_all_users():
    """Obtiene todos los usuarios (sin contraseñas)"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, username, nombre, rol, activo, primer_login, fecha_creacion, ultimo_login FROM usuarios")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    except Exception as e:
        print("Error obteniendo usuarios:", e)
        return []

def update_last_login(username: str):
    """Actualiza el último login del usuario"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP, primer_login = 0 WHERE username = %s", (username,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error actualizando último login:", e)
