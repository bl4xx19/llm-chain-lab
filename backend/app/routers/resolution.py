from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import InteractionLog
from app.resolution.build import build_resolution, build_catalogo_escenario

router = APIRouter(prefix="/resolucion", tags=["resolucion"])


@router.get("/catalogo")
def obtener_catalogo(escenario: str):
    return build_catalogo_escenario(escenario)


@router.get("")
def obtener_resolucion(log_id: int, db: Session = Depends(get_db)):
    log_entry = db.query(InteractionLog).filter_by(id=log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="log no encontrado")

    resolucion = build_resolution(log_entry)
    if not resolucion:
        raise HTTPException(
            status_code=404,
            detail="este log no corresponde a ninguna cadena reconocida",
        )
    return resolucion
