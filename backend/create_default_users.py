#!/usr/bin/env python3
"""
Script para crear usuarios por defecto en la base de datos
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


def create_default_users():
    """Crea usuarios por defecto"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Usuario administrador
        admin_password = pwd_context.hash("admin123")
        cursor.execute("""
            INSERT INTO usuarios (username, password, nombre, apellido, rol) 
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                password = VALUES(password),
                nombre = VALUES(nombre),
                apellido = VALUES(apellido),
                rol = VALUES(rol)
        """, ("admin", admin_password, "Administrador", "Sistema", "administrador"))
        
        # Usuario operador
        operador_password = pwd_context.hash("operador123")
        cursor.execute("""
            INSERT INTO usuarios (username, password, nombre, apellido, rol) 
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                password = VALUES(password),
                nombre = VALUES(nombre),
                apellido = VALUES(apellido),
                rol = VALUES(rol)
        """, ("operador", operador_password, "Operador", "Sistema", "operador"))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Usuarios por defecto creados/actualizados exitosamente")
        print("\n📋 Credenciales por defecto:")
        print("👨‍💼 Administrador:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n👷 Operador:")
        print("   Username: operador")
        print("   Password: operador123")
        print("\n⚠️  IMPORTANTE: Cambia estas contraseñas en producción!")
        
    except Exception as e:
        print(f"❌ Error creando usuarios por defecto: {e}")

if __name__ == "__main__":
    print("🚀 Creando sistema de usuarios para SmartGate...")
    create_default_users()
    print("\n✅ Configuración completada!")
