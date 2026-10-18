from sqlalchemy.orm import Session
from app.db.models import Cuenta, Transaccion


def consultar_saldo(db: Session, numero_cuenta: str) -> dict:
    cuenta = db.query(Cuenta).filter_by(numero_cuenta=numero_cuenta).first()
    if not cuenta:
        return {"error": "cuenta no encontrada"}
    return {"numero_cuenta": cuenta.numero_cuenta, "saldo": float(cuenta.saldo)}


def transferir(db: Session, cuenta_origen: str, cuenta_destino: str, monto: float) -> dict:
    origen = db.query(Cuenta).filter_by(numero_cuenta=cuenta_origen).first()
    destino = db.query(Cuenta).filter_by(numero_cuenta=cuenta_destino).first()

    if not origen or not destino:
        return {"error": "cuenta origen o destino no encontrada"}

    if origen.saldo < monto:
        return {"error": "saldo insuficiente"}

    origen.saldo -= monto
    destino.saldo += monto
    tx = Transaccion(
        cuenta_origen=cuenta_origen, cuenta_destino=cuenta_destino, monto=monto,
        concepto="Transferencia vía asistente virtual", canal_origen="asistente_virtual",
    )
    db.add(tx)
    db.commit()

    return {
        "status": "ok",
        "cuenta_origen": cuenta_origen,
        "cuenta_destino": cuenta_destino,
        "monto": monto,
        "nuevo_saldo_origen": float(origen.saldo),
    }


def consultar_movimientos_detallados(db: Session, numero_cuenta: str) -> dict:
    cuenta = db.query(Cuenta).filter_by(numero_cuenta=numero_cuenta).first()
    if not cuenta:
        return {"error": "cuenta no encontrada"}

    movimientos = (
        db.query(Transaccion)
        .filter((Transaccion.cuenta_origen == numero_cuenta) | (Transaccion.cuenta_destino == numero_cuenta))
        .order_by(Transaccion.timestamp.desc())
        .all()
    )
    return {
        "numero_cuenta": numero_cuenta,
        "titular": cuenta.titular,
        "movimientos": [
            {
                "id": m.id, "cuenta_origen": m.cuenta_origen, "cuenta_destino": m.cuenta_destino,
                "monto": float(m.monto), "concepto": m.concepto, "canal_origen": m.canal_origen,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            }
            for m in movimientos
        ],
    }


def solicitar_aumento_limite(db: Session, numero_cuenta: str, nuevo_limite: float) -> dict:
    cuenta = db.query(Cuenta).filter_by(numero_cuenta=numero_cuenta).first()
    if not cuenta:
        return {"error": "cuenta no encontrada"}

    limite_anterior = float(cuenta.limite_diario)
    cuenta.limite_diario = nuevo_limite
    db.commit()

    return {
        "status": "ok",
        "numero_cuenta": numero_cuenta,
        "limite_anterior": limite_anterior,
        "limite_nuevo": nuevo_limite,
    }


def consultar_saldos_todas(db: Session) -> dict:
    cuentas = db.query(Cuenta).all()
    return {
        "status": "ok",
        "cuentas": [
            {"numero_cuenta": c.numero_cuenta, "titular": c.titular, "saldo": float(c.saldo)}
            for c in cuentas
        ],
    }


def transferencia_masiva(db: Session, cuentas_origen: list, cuenta_destino: str) -> dict:
    destino = db.query(Cuenta).filter_by(numero_cuenta=cuenta_destino).first()
    if not destino:
        return {"error": "cuenta destino no encontrada"}

    movimientos = []
    total_drenado = 0.0
    for numero_cuenta in cuentas_origen:
        if numero_cuenta == cuenta_destino:
            continue
        origen = db.query(Cuenta).filter_by(numero_cuenta=numero_cuenta).first()
        if not origen or origen.saldo <= 0:
            continue
        monto_decimal = origen.saldo
        monto = float(monto_decimal)
        origen.saldo = 0
        destino.saldo += monto_decimal
        total_drenado += monto
        movimientos.append({"cuenta_origen": numero_cuenta, "monto": monto})

    db.commit()

    return {
        "status": "ok",
        "cuenta_destino": cuenta_destino,
        "cuentas_drenadas": len(movimientos),
        "total_drenado": total_drenado,
        "detalle": movimientos,
    }


BANCA_FUNCTIONS = {
    "consultar_saldo": consultar_saldo,
    "transferir": transferir,
    "consultar_movimientos_detallados": consultar_movimientos_detallados,
    "solicitar_aumento_limite": solicitar_aumento_limite,
    "consultar_saldos_todas": consultar_saldos_todas,
    "transferencia_masiva": transferencia_masiva,
}
