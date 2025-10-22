#!/usr/bin/env python3
"""
Script para generar hashes de contraseña para usuarios por defecto
Ejecutar: python generate_password_hashes.py
"""

from passlib.context import CryptContext

# Configurar contexto de hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_hash(password: str) -> str:
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)

def main():
    print("=" * 50)
    print("GENERADOR DE HASHES DE CONTRASEÑA")
    print("=" * 50)
    print()
    
    # Contraseñas por defecto
    passwords = {
        "admin123": "admin",
        "ope123": "ope"
    }
    
    print("Hashes generados:")
    print("-" * 30)
    
    for password, username in passwords.items():
        hash_value = generate_hash(password)
        print(f"Usuario: {username}")
        print(f"Password: {password}")
        print(f"Hash: {hash_value}")
        print()
    
    print("=" * 50)
    print("INSTRUCCIONES:")
    print("1. Copia los hashes generados")
    print("2. Actualiza el archivo backend/sql/03_create_default_users.sql")
    print("3. Reemplaza los hashes existentes con los nuevos")
    print("=" * 50)

if __name__ == "__main__":
    main()
