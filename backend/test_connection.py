#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos Neon PostgreSQL
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada en el archivo .env")
    print("\nAsegúrate de que tu archivo .env contenga:")
    print("DATABASE_URL=postgresql://...")
    exit(1)

print(f"✅ DATABASE_URL encontrada")
host = DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'N/A'
db_name = DATABASE_URL.split('/')[-1].split('?')[0] if '/' in DATABASE_URL else 'N/A'
print(f"📋 Host: {host}")
print(f"📋 Base de datos: {db_name}")

# Verificar si está usando la cadena correcta
if "ep-royal-cell" in DATABASE_URL:
    print(f"\n⚠️  ADVERTENCIA: Estás usando la cadena de conexión ANTIGUA")
    print(f"   La nueva cadena debería tener: ep-cool-lake-acun8p1l-pooler")
    print(f"   Actualiza tu archivo .env con la nueva cadena de conexión")

print("\n🔌 Intentando conectar...")

try:
    import psycopg2
    
    # Intentar conectar usando DATABASE_URL
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Ejecutar una consulta simple
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    
    print("✅ ¡Conexión exitosa!")
    print(f"\n📊 Versión de PostgreSQL:")
    print(f"   {version[0]}")
    
    # Verificar si las tablas existen en el schema public
    DB_SCHEMA = os.getenv("DB_SCHEMA", "public")
    print(f"\n🔍 Buscando tablas en el schema: '{DB_SCHEMA}'")
    
    # Intentar con pg_tables primero (más directo)
    try:
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = %s 
            ORDER BY tablename;
        """, (DB_SCHEMA,))
        tablas = cursor.fetchall()
    except Exception as e:
        print(f"   ⚠️  Error con pg_tables: {e}")
        # Fallback a information_schema
        try:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                ORDER BY table_name;
            """, (DB_SCHEMA,))
            tablas = cursor.fetchall()
        except Exception as e2:
            print(f"   ⚠️  Error con information_schema: {e2}")
            tablas = []
    
    if tablas:
        print(f"\n✅ Tablas encontradas en schema '{DB_SCHEMA}' ({len(tablas)}):")
        for tabla in tablas:
            print(f"   - {tabla[0]}")
        
        # Contar registros en tablas principales
        print(f"\n📊 Contando registros en tablas principales:")
        tablas_principales = ['usuarios', 'vehiculos', 'departamentos', 'propietarios', 'registro_accesos', 'pagos', 'tarifas', 'inquilinos']
        for tabla_nombre in tablas_principales:
            # Verificar si la tabla existe (comparar sin importar mayúsculas/minúsculas)
            tabla_existe = any(t[0].lower() == tabla_nombre.lower() for t in tablas)
            if tabla_existe:
                try:
                    # Usar el nombre exacto de la tabla como está en la BD
                    tabla_real = next((t[0] for t in tablas if t[0].lower() == tabla_nombre.lower()), tabla_nombre)
                    cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{tabla_real}"')
                    count = cursor.fetchone()[0]
                    print(f"   - {tabla_real}: {count} registro(s)")
                except Exception as e:
                    print(f"   - {tabla_nombre}: Error al contar - {e}")
        
        # También mostrar tablas en otros schemas comunes
        try:
            cursor.execute("""
                SELECT DISTINCT schemaname 
                FROM pg_tables 
                WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schemaname;
            """)
            schemas = cursor.fetchall()
        except Exception:
            try:
                cursor.execute("""
                    SELECT DISTINCT table_schema 
                    FROM information_schema.tables 
                    WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    ORDER BY table_schema;
                """)
                schemas = cursor.fetchall()
            except Exception:
                schemas = []
        
        if schemas:
            print(f"\n📂 Schemas disponibles en la base de datos:")
            for schema in schemas:
                schema_name = schema[0]
                try:
                    # Intentar con pg_tables
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM pg_tables 
                        WHERE schemaname = %s;
                    """, (schema_name,))
                    count = cursor.fetchone()[0]
                except Exception:
                    # Fallback
                    try:
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM information_schema.tables 
                            WHERE table_schema = %s;
                        """, (schema_name,))
                        count = cursor.fetchone()[0]
                    except Exception:
                        count = 0
                marker = " ✓ (usando)" if schema_name == DB_SCHEMA else ""
                print(f"   - {schema_name}: {count} tabla(s){marker}")
        
        print(f"\n✅ ¡Todo está configurado correctamente!")
    else:
        print(f"\n⚠️  No se encontraron tablas en el schema '{DB_SCHEMA}'")
        print("\n🔍 Buscando en otros schemas...")
        
        # Buscar en otros schemas usando pg_tables
        try:
            cursor.execute("""
                SELECT schemaname, tablename
                FROM pg_tables 
                WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schemaname, tablename;
            """)
            todas_tablas = cursor.fetchall()
        except Exception:
            # Fallback a information_schema
            try:
                cursor.execute("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables 
                    WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    ORDER BY table_schema, table_name;
                """)
                todas_tablas = cursor.fetchall()
            except Exception:
                todas_tablas = []
        
        if todas_tablas:
            print(f"\n📋 Tablas encontradas en otros schemas:")
            schema_actual = None
            for schema, tabla in todas_tablas:
                if schema != schema_actual:
                    schema_actual = schema
                    print(f"\n   Schema: {schema}")
                print(f"      - {tabla}")
            print(f"\n💡 Si tus tablas están en otro schema, configura DB_SCHEMA en tu .env")
        else:
            print("   No se encontraron tablas en ningún schema")
            print("\n   Debes ejecutar los scripts SQL en este orden:")
            print("   1. backend/sql/01_create_tables.sql")
            print("   2. backend/sql/02_insert_sample_data.sql")
            print("   3. backend/sql/03_create_default_users.sql")
    
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ Error de conexión: {e}")
    print("\nVerifica:")
    print("  1. Que la cadena de conexión DATABASE_URL sea correcta")
    print("  2. Que tu IP esté permitida en Neon (si aplica)")
    print("  3. Que la base de datos exista")
    
except ImportError:
    print("❌ Error: psycopg2 no está instalado")
    print("\nInstala las dependencias:")
    print("  pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")

