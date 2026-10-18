from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Paciente, HistorialMedico

router = APIRouter(prefix="/admin/salud", tags=["admin-salud"])


@router.get("/estado")
def estado_salud(db: Session = Depends(get_db)):
    pacientes = db.query(Paciente).order_by(Paciente.id).all()
    historiales = db.query(HistorialMedico).order_by(HistorialMedico.id).all()
    return {
        "pacientes": [
            {"numero_historia": p.numero_historia, "nombre": p.nombre} for p in pacientes
        ],
        "historiales": [
            {
                "numero_historia": h.numero_historia,
                "diagnostico": h.diagnostico,
                "notas": h.notas,
            }
            for h in historiales
        ],
    }
