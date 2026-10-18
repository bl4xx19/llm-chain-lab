from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Cuenta, Transaccion

router = APIRouter(prefix="/admin/banca", tags=["admin-banca"])


@router.get("/estado")
def estado_banca(db: Session = Depends(get_db)):
    cuentas = db.query(Cuenta).order_by(Cuenta.numero_cuenta).all()
    transacciones = db.query(Transaccion).order_by(Transaccion.timestamp.desc()).limit(20).all()
    return {
        "cuentas": [
            {"numero_cuenta": c.numero_cuenta, "titular": c.titular, "saldo": float(c.saldo)}
            for c in cuentas
        ],
        "transacciones": [
            {
                "id": t.id,
                "cuenta_origen": t.cuenta_origen,
                "cuenta_destino": t.cuenta_destino,
                "monto": float(t.monto),
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            }
            for t in transacciones
        ],
    }
