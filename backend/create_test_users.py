#!/usr/bin/env python3
"""
Script para crear usuarios de prueba en la tabla usuarios existente
"""
import mysql.connector
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Configuración para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

def create_test_users():
    """Crea usuarios de prueba"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Usuario administrador
        admin_password = pwd_context.hash("admin123")
        cursor.execute("""
            INSERT INTO usuarios (username, password_hash, nombre, rol, activo, primer_login) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                password_hash = VALUES(password_hash),
                nombre = VALUES(nombre),
                rol = VALUES(rol),
                activo = VALUES(activo)
        """, ("admin", admin_password, "Administrador Sistema", "admin", True, True))
        
        # Usuario operador
        operador_password = pwd_context.hash("operador123")
        cursor.execute("""
            INSERT INTO usuarios (username, password_hash, nombre, rol, activo, primer_login) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                password_hash = VALUES(password_hash),
                nombre = VALUES(nombre),
                rol = VALUES(rol),
                activo = VALUES(activo)
        """, ("operador", operador_password, "Operador Sistema", "ope", True, True))
        
        # Usuario operador adicional
        operador2_password = pwd_context.hash("ope123")
        cursor.execute("""
            INSERT INTO usuarios (username, password_hash, nombre, rol, activo, primer_login) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                password_hash = VALUES(password_hash),
                nombre = VALUES(nombre),
                rol = VALUES(rol),
                activo = VALUES(activo)
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
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username, nombre, rol, activo FROM usuarios")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if users:
            print("📋 Usuarios existentes:")
            for user in users:
                status = "✅ Activo" if user["activo"] else "❌ Inactivo"
                print(f"   {user['username']} - {user['nombre']} ({user['rol']}) - {status}")
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

