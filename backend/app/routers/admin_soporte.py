from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Ticket, ConfiguracionInterna

router = APIRouter(prefix="/admin/soporte", tags=["admin-soporte"])


@router.get("/estado")
def estado_soporte(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).order_by(Ticket.id).all()
    config = db.query(ConfiguracionInterna).order_by(ConfiguracionInterna.id).all()
    return {
        "tickets": [
            {
                "id": t.id, "cliente": t.cliente, "titulo": t.titulo,
                "descripcion": t.descripcion, "estado": t.estado,
            }
            for t in tickets
        ],
        "configuracion": [
            {"clave": c.clave, "valor": c.valor} for c in config
        ],
    }
