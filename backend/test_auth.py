#!/usr/bin/env python3
"""
Script para probar la autenticación directamente
"""
import os
from dotenv import load_dotenv
from db import authenticate_user, get_connection, table_name, DB_SCHEMA
from psycopg2.extras import RealDictCursor

load_dotenv()

def test_auth(username: str, password: str):
    """Prueba la autenticación directamente"""
    print(f"=" * 60)
    print(f"🔍 Probando autenticación para: {username}")
    print(f"=" * 60)
    
    # Primero verificar qué hay en la BD
    print("\n1️⃣ Verificando usuario en la base de datos...")
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SELECT * FROM {table_name('usuarios')} WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            user_dict = dict(user)
            print(f"✅ Usuario encontrado:")
            print(f"   - ID: {user_dict.get('id_usuario')}")
            print(f"   - Username: {user_dict.get('username')}")
            print(f"   - Nombre: {user_dict.get('nombre')}")
            print(f"   - Rol: {user_dict.get('rol')}")
            print(f"   - Activo: {user_dict.get('activo')}")
            print(f"   - Primer login: {user_dict.get('primer_login')}")
            
            password_hash = user_dict.get('password_hash', '')
            print(f"   - Password hash: {password_hash[:50]}...")
            print(f"   - Hash válido: {password_hash.startswith('$2b$') or password_hash.startswith('$2a$')}")
            print(f"   - Longitud hash: {len(password_hash)}")
        else:
            print(f"❌ Usuario '{username}' NO encontrado")
            return False
    except Exception as e:
        print(f"❌ Error consultando usuario: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Ahora probar la autenticación
    print(f"\n2️⃣ Probando autenticación con password: '{password}'...")
    result = authenticate_user(username, password)
    
    if result:
        print(f"\n✅ ¡AUTENTICACIÓN EXITOSA!")
        print(f"   Usuario retornado: {result.get('username')}")
        return True
    else:
        print(f"\n❌ AUTENTICACIÓN FALLIDA")
        return False

if __name__ == "__main__":
    import sys
    
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    
    print(f"📋 Schema usado: {DB_SCHEMA}")
    print()
    
    test_auth(username, password)

