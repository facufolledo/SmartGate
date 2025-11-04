#!/usr/bin/env python3
"""
Script para actualizar el password_hash de un usuario en la base de datos
"""
import os
from dotenv import load_dotenv
from db import get_connection, table_name, get_password_hash, DB_SCHEMA

load_dotenv()

def fix_user_password(username: str, new_password: str):
    """Actualiza el password_hash de un usuario"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar si el usuario existe
        cursor.execute(f"SELECT id_usuario, username FROM {table_name('usuarios')} WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Usuario '{username}' no encontrado")
            return False
        
        # Generar nuevo hash
        new_hash = get_password_hash(new_password)
        
        # Actualizar el password_hash y activar el usuario
        cursor.execute(
            f"UPDATE {table_name('usuarios')} SET password_hash = %s, activo = TRUE WHERE username = %s",
            (new_hash, username)
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Password actualizado para usuario '{username}'")
        print(f"   Nuevo hash: {new_hash[:30]}...")
        print(f"   Usuario activado")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python fix_user_password.py <username> <nueva_contraseña>")
        print("\nEjemplo:")
        print("  python fix_user_password.py facufolledo nueva_password123")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"🔧 Actualizando password para usuario: {username}")
    print(f"📋 Schema: {DB_SCHEMA}")
    print()
    
    fix_user_password(username, password)

