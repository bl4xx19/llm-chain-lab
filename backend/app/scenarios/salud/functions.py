from sqlalchemy.orm import Session
from app.db.models import HistorialMedico


def consultar_historial(db: Session, numero_historia: str) -> dict:
    h = db.query(HistorialMedico).filter_by(numero_historia=numero_historia).first()
    if not h:
        return {"error": "historial no encontrado"}
    return {
        "numero_historia": h.numero_historia,
        "diagnostico": h.diagnostico,
        "notas": h.notas,
    }


def buscar_en_historiales(db: Session, consulta: str) -> dict:
    palabras = [p.lower() for p in consulta.split() if len(p) > 2]
    resultados = []
    for h in db.query(HistorialMedico).all():
        texto = f"{h.diagnostico} {h.notas}".lower()
        if any(p in texto for p in palabras):
            resultados.append({
                "numero_historia": h.numero_historia,
                "diagnostico": h.diagnostico,
                "notas": h.notas,
            })
    return {"status": "ok", "consulta": consulta, "resultados": resultados}


def actualizar_diagnostico(db: Session, numero_historia: str, nuevo_diagnostico: str) -> dict:
    h = db.query(HistorialMedico).filter_by(numero_historia=numero_historia).first()
    if not h:
        return {"error": "historial no encontrado"}

    diagnostico_anterior = h.diagnostico
    h.diagnostico = nuevo_diagnostico
    db.commit()

    return {
        "status": "ok",
        "numero_historia": numero_historia,
        "diagnostico_anterior": diagnostico_anterior,
        "diagnostico_nuevo": nuevo_diagnostico,
    }


def exportar_historiales_completos(db: Session, confirmar: bool = True) -> dict:
    historiales = db.query(HistorialMedico).all()
    return {
        "status": "ok",
        "total_historiales": len(historiales),
        "historiales": [
            {
                "numero_historia": h.numero_historia,
                "diagnostico": h.diagnostico,
                "notas": h.notas,
            }
            for h in historiales
        ],
    }


SALUD_FUNCTIONS = {
    "consultar_historial": consultar_historial,
    "buscar_en_historiales": buscar_en_historiales,
    "actualizar_diagnostico": actualizar_diagnostico,
    "exportar_historiales_completos": exportar_historiales_completos,
}
