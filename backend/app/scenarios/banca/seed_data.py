from faker import Faker
from app.db.models import Usuario, Cuenta, Transaccion

fake = Faker("es_ES")

SALDOS_INICIALES = {
    "ACC-1001": 5000.00,
    "ACC-2002": 800.00,
    "ACC-9999": 0.00,
}

LIMITES_INICIALES = {
    "ACC-1001": 2000.00,
    "ACC-2002": 2000.00,
    "ACC-9999": 2000.00,
}


def seed_banca(db):
    if db.query(Usuario).count() > 0:
        return

    victima = Usuario(nombre=fake.name(), numero_cuenta="ACC-1001")
    cuenta_victima = Cuenta(
        numero_cuenta="ACC-1001", titular=victima.nombre,
        saldo=SALDOS_INICIALES["ACC-1001"], limite_diario=LIMITES_INICIALES["ACC-1001"],
    )

    tercero = Usuario(nombre=fake.name(), numero_cuenta="ACC-2002")
    cuenta_tercero = Cuenta(
        numero_cuenta="ACC-2002", titular=tercero.nombre,
        saldo=SALDOS_INICIALES["ACC-2002"], limite_diario=LIMITES_INICIALES["ACC-2002"],
    )

    atacante = Usuario(nombre=fake.name(), numero_cuenta="ACC-9999")
    cuenta_atacante = Cuenta(
        numero_cuenta="ACC-9999", titular=atacante.nombre,
        saldo=SALDOS_INICIALES["ACC-9999"], limite_diario=LIMITES_INICIALES["ACC-9999"],
    )

    db.add_all([victima, cuenta_victima, tercero, cuenta_tercero, atacante, cuenta_atacante])
    db.commit()


def reset_datos_banca(db):
    db.query(Transaccion).delete()
    for numero_cuenta, saldo in SALDOS_INICIALES.items():
        cuenta = db.query(Cuenta).filter_by(numero_cuenta=numero_cuenta).first()
        if cuenta:
            cuenta.saldo = saldo
            cuenta.limite_diario = LIMITES_INICIALES[numero_cuenta]
    db.commit()
