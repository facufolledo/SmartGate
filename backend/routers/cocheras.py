
from fastapi import APIRouter
from pydantic import BaseModel
from db import db_config, DB_SCHEMA, get_connection, table_name
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/cocheras", tags=["Cocheras"])

class MatriculaRequest(BaseModel):
    matricula: str

@router.post("/verificar-acceso")
def verificar_acceso_cochera(data: MatriculaRequest):
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from db import db_config
    from datetime import datetime, timedelta, date
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Buscar id_departamento del vehículo
        cursor.execute(f"SELECT id_departamento FROM {table_name('vehiculos')} WHERE matricula = %s", (data.matricula,))
        vehiculo = cursor.fetchone()
        if not vehiculo or not dict(vehiculo).get("id_departamento"):
            cursor.close()
            conn.close()
            return {"acceso": False, "mensaje": "Acceso denegado", "motivo": "Vehículo sin cochera/departamento asociado"}
        vehiculo_dict = dict(vehiculo)
        id_departamento = vehiculo_dict["id_departamento"]
        # Buscar el último pago realizado
        cursor.execute(f"SELECT * FROM {table_name('pagos')} WHERE id_departamento = %s ORDER BY fecha_pago DESC LIMIT 1", (id_departamento,))
        pago = cursor.fetchone()
        if not pago:
            cursor.close()
            conn.close()
            return {"acceso": False, "mensaje": "Acceso denegado", "motivo": "No se encontraron pagos para este departamento"}
        pago_dict = dict(pago)
        # Buscar id_tarifa en la tabla inquilinos
        cursor.execute(f"SELECT id_tarifa FROM {table_name('inquilinos')} WHERE id_departamento = %s", (id_departamento,))
        inquilino = cursor.fetchone()
        if not inquilino or not dict(inquilino).get("id_tarifa"):
            cursor.close()
            conn.close()
            return {"acceso": False, "mensaje": "Acceso denegado", "motivo": "No se encontró tarifa para el departamento"}
        inquilino_dict = dict(inquilino)
        id_tarifa = inquilino_dict["id_tarifa"]
        cursor.execute(f"SELECT * FROM {table_name('tarifas')} WHERE id_tarifa = %s", (id_tarifa,))
        tarifa = cursor.fetchone()
        tarifa_dict = dict(tarifa)
        cursor.close()
        conn.close()
        # Calcular fecha de vencimiento usando solo date
        fecha_pago = pago_dict["fecha_pago"]
        if isinstance(fecha_pago, str):
            fecha_pago = datetime.strptime(fecha_pago, "%Y-%m-%d").date()
        elif isinstance(fecha_pago, datetime):
            fecha_pago = fecha_pago.date()
        # Sumar días según la tarifa
        if tarifa_dict["descripcion"].lower() == "mensual":
            vencimiento = fecha_pago + timedelta(days=30)
        elif tarifa_dict["descripcion"].lower() == "anual":
            vencimiento = fecha_pago + timedelta(days=365)
        else:
            vencimiento = fecha_pago
        hoy = date.today()
        dias_restantes = (vencimiento - hoy).days
        acceso = dias_restantes > 0
        # Si la mensualidad está vencida, actualizar estado del vehículo a 1 (denegado)
        if not acceso:
            try:
                conn2 = get_connection()
                cursor2 = conn2.cursor()
                cursor2.execute(f"UPDATE {table_name('vehiculos')} SET estado = 1 WHERE matricula = %s", (data.matricula,))
                conn2.commit()
                cursor2.close()
                conn2.close()
            except Exception as e:
                return {"error": f"No se pudo actualizar el estado del vehículo: {str(e)}"}
            return {
                "acceso": False,
                "mensaje": "Acceso denegado",
                "motivo": "Mensualidad vencida",
                "dias_restantes": dias_restantes,
                "vencimiento": vencimiento.strftime("%Y-%m-%d")
            }
        return {
            "acceso": True,
            "mensaje": "Acceso autorizado",
            "dias_restantes": dias_restantes,
            "vencimiento": vencimiento.strftime("%Y-%m-%d")
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/tarifas")
def get_tarifas():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SELECT * FROM {table_name('tarifas')}")
        tarifas = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"tarifas": [dict(t) for t in tarifas]}
    except Exception as e:
        return {"error": str(e)}

@router.post("/pago")
def registrar_pago():
    # Aquí irá la lógica para registrar pagos
    return {"mensaje": "Pago registrado (demo)"}

@router.get("/pagos/{matricula}")
def historial_pagos(matricula: str):
    # Aquí irá la lógica para consultar historial de pagos
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from db import db_config
        try:
            conn = get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            # Buscar id_departamento del vehículo
            cursor.execute(f"SELECT id_departamento FROM {table_name('vehiculos')} WHERE matricula = %s", (matricula,))
            vehiculo = cursor.fetchone()
            if not vehiculo or not dict(vehiculo).get("id_departamento"):
                cursor.close()
                conn.close()
                return {"pagos": [], "mensaje": "Vehículo sin cochera/departamento asociado"}
            vehiculo_dict = dict(vehiculo)
            id_departamento = vehiculo_dict["id_departamento"]
            
            cursor.execute(f"SELECT * FROM {table_name('pagos')} WHERE id_departamento = %s", (id_departamento,))
            pagos = cursor.fetchall()
            cursor.close()
            conn.close()
            return {"pagos": [dict(p) for p in pagos]}
        except Exception as e:
            return {"error": str(e)}
