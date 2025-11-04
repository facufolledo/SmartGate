"""
Funciones auxiliares para construir consultas SQL con manejo de schemas
"""
import os
from dotenv import load_dotenv

load_dotenv()
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")

def table_name(table: str) -> str:
    """
    Retorna el nombre de tabla con schema si es necesario.
    Para schema 'public', omite el schema (PostgreSQL lo busca por defecto).
    """
    if DB_SCHEMA == "public":
        return table
    else:
        return f"{DB_SCHEMA}.{table}"


