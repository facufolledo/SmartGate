#!/usr/bin/env python3
"""
Script para crear usuarios de prueba en la tabla usuarios existente
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Configuración para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schema de la base de datos (public es el default en PostgreSQL)
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")

# Configuración de base de datos PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    db_config = {"dsn": DATABASE_URL}
else:
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": os.getenv("DB_PORT", "5432")
    }

def create_test_users():
    """Crea usuarios de prueba"""
    try:
        if "dsn" in db_config:
            conn = psycopg2.connect(db_config["dsn"])
        else:
            conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Usuario administrador
        admin_password = pwd_context.hash("admin123")
        cursor.execute(f"""
            INSERT INTO {DB_SCHEMA}.usuarios (username, password_hash, nombre, rol, activo, primer_login) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE 
                SET password_hash = EXCLUDED.password_hash,
                    nombre = EXCLUDED.nombre,
                    rol = EXCLUDED.rol,
                    activo = EXCLUDED.activo
        """, ("admin", admin_password, "Administrador Sistema", "admin", True, True))
        
        # Usuario operador
        operador_password = pwd_context.hash("operador123")
        cursor.execute(f"""
            INSERT INTO {DB_SCHEMA}.usuarios (username, password_hash, nombre, rol, activo, primer_login) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE 
                SET password_hash = EXCLUDED.password_hash,
                    nombre = EXCLUDED.nombre,
                    rol = EXCLUDED.rol,
                    activo = EXCLUDED.activo
        """, ("operador", operador_password, "Operador Sistema", "ope", True, True))
        
        # Usuario operador adicional
        operador2_password = pwd_context.hash("ope123")
        cursor.execute(f"""
            INSERT INTO {DB_SCHEMA}.usuarios (username, password_hash, nombre, rol, activo, primer_login) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE 
                SET password_hash = EXCLUDED.password_hash,
                    nombre = EXCLUDED.nombre,
                    rol = EXCLUDED.rol,
                    activo = EXCLUDED.activo
        """, ("ope1", operador2_password, "Operador 1", "ope", True, True))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Usuarios de prueba creados/actualizados exitosamente")
        print("\n📋 Credenciales de prueba:")
        print("👨‍💼 Administrador:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Rol: admin")
        print("\n👷 Operador 1:")
        print("   Username: operador")
        print("   Password: operador123")
        print("   Rol: ope")
        print("\n👷 Operador 2:")
        print("   Username: ope1")
        print("   Password: ope123")
        print("   Rol: ope")
        print("\n⚠️  IMPORTANTE: Cambia estas contraseñas en producción!")
        
    except Exception as e:
        print(f"❌ Error creando usuarios de prueba: {e}")

def check_existing_users():
    """Verifica usuarios existentes"""
    try:
        if "dsn" in db_config:
            conn = psycopg2.connect(db_config["dsn"])
        else:
            conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SELECT username, nombre, rol, activo FROM {DB_SCHEMA}.usuarios")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if users:
            print("📋 Usuarios existentes:")
            for user in users:
                user_dict = dict(user)
                status = "✅ Activo" if user_dict["activo"] else "❌ Inactivo"
                print(f"   {user_dict['username']} - {user_dict['nombre']} ({user_dict['rol']}) - {status}")
        else:
            print("📋 No hay usuarios en la tabla")
            
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")

if __name__ == "__main__":
    print("🚀 Configurando usuarios de prueba para SmartGate...")
    check_existing_users()
    print("\n" + "="*50)
    create_test_users()
    print("\n" + "="*50)
    check_existing_users()
    print("\n✅ Configuración completada!")

