
from fastapi import APIRouter
from pydantic import BaseModel
from db import db_config
import mysql.connector

router = APIRouter(prefix="/cocheras", tags=["Cocheras"])

class MatriculaRequest(BaseModel):
    matricula: str

@router.post("/verificar-acceso")
def verificar_acceso_cochera(data: MatriculaRequest):
    import mysql.connector
    from db import db_config
    from datetime import datetime, timedelta, date
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        # Buscar id_departamento del vehículo
        cursor.execute("SELECT id_departamento FROM vehiculos WHERE matricula = %s", (data.matricula,))
        vehiculo = cursor.fetchone()
        if not vehiculo or not vehiculo["id_departamento"]:
            cursor.close()
            conn.close()
            return {"acceso": False, "mensaje": "Acceso denegado", "motivo": "Vehículo sin cochera/departamento asociado"}
        id_departamento = vehiculo["id_departamento"]
        # Buscar el último pago realizado
        cursor.execute("SELECT * FROM pagos WHERE id_departamento = %s ORDER BY fecha_pago DESC LIMIT 1", (id_departamento,))
        pago = cursor.fetchone()
        if not pago:
            cursor.close()
            conn.close()
            return {"acceso": False, "mensaje": "Acceso denegado", "motivo": "No se encontraron pagos para este departamento"}
        # Buscar id_tarifa en la tabla inquilinos
        cursor.execute("SELECT id_tarifa FROM inquilinos WHERE id_departamento = %s", (id_departamento,))
        inquilino = cursor.fetchone()
        if not inquilino or not inquilino["id_tarifa"]:
            return {"acceso": False, "mensaje": "Acceso denegado", "motivo": "No se encontró tarifa para el departamento"}
        id_tarifa = inquilino["id_tarifa"]
        cursor.execute("SELECT * FROM tarifas WHERE id_tarifa = %s", (id_tarifa,))
        tarifa = cursor.fetchone()
        cursor.close()
        conn.close()
        # Calcular fecha de vencimiento usando solo date
        fecha_pago = pago["fecha_pago"]
        if isinstance(fecha_pago, str):
            fecha_pago = datetime.strptime(fecha_pago, "%Y-%m-%d").date()
        elif isinstance(fecha_pago, datetime):
            fecha_pago = fecha_pago.date()
        # Sumar días según la tarifa
        if tarifa["descripcion"].lower() == "mensual":
            vencimiento = fecha_pago + timedelta(days=30)
        elif tarifa["descripcion"].lower() == "anual":
            vencimiento = fecha_pago + timedelta(days=365)
        else:
            vencimiento = fecha_pago
        hoy = date.today()
        dias_restantes = (vencimiento - hoy).days
        acceso = dias_restantes > 0
        # Si la mensualidad está vencida, actualizar estado del vehículo a 1 (denegado)
        if not acceso:
            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute("UPDATE vehiculos SET estado = 1 WHERE matricula = %s", (data.matricula,))
                conn.commit()
                cursor.close()
                conn.close()
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
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tarifas")
        tarifas = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"tarifas": tarifas}
    except Exception as e:
        return {"error": str(e)}

@router.post("/pago")
def registrar_pago():
    # Aquí irá la lógica para registrar pagos
    return {"mensaje": "Pago registrado (demo)"}

@router.get("/pagos/{matricula}")
def historial_pagos(matricula: str):
    # Aquí irá la lógica para consultar historial de pagos
        import mysql.connector
        from db import db_config
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            # Buscar id_departamento del vehículo
            cursor.execute("SELECT id_departamento FROM vehiculos WHERE matricula = %s", (matricula,))
            vehiculo = cursor.fetchone()
            if not vehiculo or not vehiculo["id_departamento"]:
                cursor.close()
                conn.close()
                return {"pagos": [], "mensaje": "Vehículo sin cochera/departamento asociado"}
            id_departamento = vehiculo["id_departamento"]
            
            cursor.execute("SELECT * FROM pagos WHERE id_departamento = %s", (id_departamento,))
            pagos = cursor.fetchall()
            cursor.close()
            conn.close()
            return {"pagos": pagos}
        except Exception as e:
            return {"error": str(e)}
