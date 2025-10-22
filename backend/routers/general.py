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
    if tiene_permiso(data.matricula):
        return {"acceso": True, "mensaje": "Acceso autorizado"}
    else:
        raise HTTPException(status_code=403, detail="Acceso denegado")
