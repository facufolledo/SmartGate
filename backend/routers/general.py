from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import tiene_permiso

router = APIRouter(prefix="/general", tags=["General"])

class MatriculaRequest(BaseModel):
    matricula: str

@router.get("/test-db")
def test_db():
    from db import db_config, test_db_connection
    return test_db_connection()

@router.post("/verificar-acceso")
def verificar_acceso(data: MatriculaRequest):
    try:
        if tiene_permiso(data.matricula):
            return {"acceso": True, "mensaje": "Acceso autorizado"}
        else:
            raise HTTPException(status_code=403, detail="Acceso denegado")
    except HTTPException:
        # Re-lanzar HTTPException (como 403) sin modificar
        raise
    except Exception as e:
        # Solo capturar otras excepciones, no HTTPException
        raise HTTPException(status_code=500, detail=f"Error al verificar acceso: {str(e)}")

@router.get("/test-vehiculo/{matricula}")
def test_vehiculo(matricula: str):
    """Endpoint de prueba para verificar si un vehículo existe en la BD"""
    from db import db_config, DB_SCHEMA
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    try:
        # Usar la función de conexión de db.py que configura el search_path
        from db import get_connection
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar el vehículo
        from db import table_name
        cursor.execute(f"SELECT * FROM {table_name('vehiculos')} WHERE matricula = %s", (matricula,))
        vehiculo = cursor.fetchone()
        
        if vehiculo:
            vehiculo_dict = dict(vehiculo)
            cursor.close()
            conn.close()
            return {
                "encontrado": True,
                "vehiculo": vehiculo_dict,
                "schema_usado": DB_SCHEMA
            }
        else:
            # Listar algunas matrículas disponibles para prueba
            from db import table_name
            cursor.execute(f"SELECT matricula, estado FROM {table_name('vehiculos')} LIMIT 5")
            ejemplos = cursor.fetchall()
            cursor.close()
            conn.close()
            return {
                "encontrado": False,
                "mensaje": f"Vehículo '{matricula}' no encontrado en schema '{DB_SCHEMA}'",
                "ejemplos": [dict(e) for e in ejemplos] if ejemplos else []
            }
    except Exception as e:
        return {
            "error": str(e),
            "schema_usado": DB_SCHEMA
        }
