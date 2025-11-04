import psycopg2
from psycopg2.extras import RealDictCursor
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

# Schema de la base de datos (public es el default en PostgreSQL)
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")

# Configuración de base de datos PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Si hay DATABASE_URL, usarla directamente (formato de Neon)
    db_config = {"dsn": DATABASE_URL}
else:
    # Si no, usar parámetros individuales
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": os.getenv("DB_PORT", "5432")
    }

def get_connection():
    """Obtiene una conexión a la base de datos con el schema correcto configurado"""
    if "dsn" in db_config:
        conn = psycopg2.connect(db_config["dsn"])
    else:
        conn = psycopg2.connect(**db_config)
    # Configurar el search_path para usar el schema correcto
    # Con esto, no necesitamos especificar el schema en las consultas
    with conn.cursor() as cursor:
        cursor.execute(f"SET search_path TO {DB_SCHEMA}, public")
    conn.commit()
    return conn

def table_name(table: str) -> str:
    """
    Retorna el nombre de tabla con schema si es necesario.
    Para schema 'public', no es necesario especificarlo si search_path está configurado.
    Pero lo mantenemos explícito por claridad y seguridad.
    """
    if DB_SCHEMA == "public":
        # Para public, podemos omitirlo o incluirlo sin comillas
        return f"public.{table}"
    else:
        return f"{DB_SCHEMA}.{table}"

def tiene_permiso(matricula: str) -> bool:
    """
    Verifica si un vehículo tiene permiso de acceso.
    Retorna True si estado = 1 (permitido) y activo = True
    Retorna False si estado = 0 (denegado) o no existe o no está activo
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Con search_path configurado, podemos usar solo el nombre de tabla
        # Pero usamos el schema explícito para mayor claridad
        query = f"SELECT estado, activo FROM {table_name('vehiculos')} WHERE matricula = %s"
        cursor.execute(query, (matricula,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is not None:
            estado = resultado[0]
            activo = resultado[1] if len(resultado) > 1 else True
            # estado = 1 significa acceso permitido, estado = 0 significa denegado
            # Además debe estar activo
            return estado == 1 and activo == True
        else:
            return False
    except Exception as e:
        print("Error DB:", e)
        return False

def test_db_connection():
    try:
        conn = get_connection()
        conn.close()
        return {"db_status": "Conexión exitosa", "schema": DB_SCHEMA}
    except Exception as e:
        return {"db_status": "Error de conexión", "detail": str(e), "schema": DB_SCHEMA}

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
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar usuario por username usando tu estructura de tabla
        cursor.execute(f"SELECT * FROM {table_name('usuarios')} WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            print(f"❌ Usuario '{username}' no encontrado en la base de datos")
            return False
        
        # Convertir a diccionario si es necesario
        user_dict = dict(user) if not isinstance(user, dict) else user
        
        print(f"🔍 Usuario encontrado: {user_dict.get('username')}")
        print(f"   Activo: {user_dict.get('activo')}")
        print(f"   Hash preview: {str(user_dict.get('password_hash', ''))[:30]}...")
        
        # Verificar si el usuario está activo
        if not user_dict.get("activo", True):
            print(f"❌ Usuario '{username}' está inactivo")
            return False
        
        # Verificar contraseña usando password_hash
        password_hash = user_dict.get("password_hash")
        if not password_hash:
            print(f"❌ Usuario '{username}' no tiene password_hash")
            return False
        
        # Verificar si el password_hash es un hash bcrypt válido (debe empezar con $2b$)
        if not password_hash.startswith("$2b$") and not password_hash.startswith("$2a$"):
            print(f"⚠️  Usuario '{username}' tiene un password_hash inválido (no es bcrypt)")
            print(f"   El hash actual es: '{password_hash[:30]}...'")
            print(f"   Debes regenerar el hash usando bcrypt para este usuario")
            return False
        
        print(f"🔐 Verificando contraseña...")
        password_valid = verify_password(password, password_hash)
        print(f"   Resultado verificación: {password_valid}")
        
        if not password_valid:
            print(f"❌ Contraseña incorrecta para usuario '{username}'")
            # Para debug: mostrar qué hash estamos comparando
            print(f"   Hash en BD: {password_hash[:30]}...")
            return False
        
        print(f"✅ Autenticación exitosa para '{username}'")
        return user_dict
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        import traceback
        traceback.print_exc()
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
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SELECT id_usuario, username, nombre, rol, activo FROM {table_name('usuarios')} WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        print("Error obteniendo usuario:", e)
        return None

def create_user(username: str, password: str, nombre: str, rol: str = "ope"):
    """Crea un nuevo usuario en la base de datos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute(f"SELECT id_usuario FROM {table_name('usuarios')} WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "message": "El usuario ya existe"}
        
        # Crear nuevo usuario usando tu estructura de tabla
        hashed_password = get_password_hash(password)
        cursor.execute(
            f"INSERT INTO {table_name('usuarios')} (username, password_hash, nombre, rol, activo, primer_login) VALUES (%s, %s, %s, %s, %s, %s)",
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
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SELECT id_usuario, username, nombre, rol, activo, primer_login, fecha_creacion, ultimo_login FROM {table_name('usuarios')}")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(user) for user in users]
    except Exception as e:
        print("Error obteniendo usuarios:", e)
        return []

def update_last_login(username: str):
    """Actualiza el último login del usuario"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table_name('usuarios')} SET ultimo_login = CURRENT_TIMESTAMP, primer_login = FALSE WHERE username = %s", (username,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error actualizando último login:", e)
