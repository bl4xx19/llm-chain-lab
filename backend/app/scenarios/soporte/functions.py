import urllib.request
import socket
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.models import Ticket, ConfiguracionInterna, Agente


def leer_ticket(db: Session, ticket_id: int) -> dict:
    t = db.query(Ticket).filter_by(id=ticket_id).first()
    if not t:
        return {"error": "ticket no encontrado"}
    return {
        "id": t.id, "cliente": t.cliente, "titulo": t.titulo,
        "descripcion": t.descripcion, "estado": t.estado,
    }


def verificar_conectividad(db: Session, url: str) -> dict:
    try:
        socket.setdefaulttimeout(3)
        req = urllib.request.Request(url, headers={"User-Agent": "SoporteBot/1.0"})
        with urllib.request.urlopen(req) as resp:
            body = resp.read(500).decode(errors="replace")
        return {"status": "alcanzable", "url": url, "http_status": resp.status, "preview": body}
    except Exception as e:
        return {"status": "no_alcanzable", "url": url, "error": str(e)}


def obtener_configuracion(db: Session, clave: str) -> dict:
    c = db.query(ConfiguracionInterna).filter_by(clave=clave).first()
    if not c:
        return {"error": "clave no encontrada"}
    return {"clave": c.clave, "valor": c.valor}


def buscar_tickets(db: Session, filtro: str) -> dict:
    query = f"SELECT id, cliente, titulo, estado FROM tickets WHERE titulo LIKE '%{filtro}%' OR descripcion LIKE '%{filtro}%'"
    try:
        result = db.execute(text(query))
        rows = [dict(row._mapping) for row in result]
        return {"status": "ok", "sql_ejecutado": query, "resultados": rows}
    except Exception as e:
        return {"status": "error", "sql_ejecutado": query, "error": str(e)}


def resetear_credenciales_agente(db: Session, usuario: str, token: str, nueva_password: str) -> dict:
    agente = db.query(Agente).filter_by(usuario=usuario).first()
    if not agente:
        return {"error": "agente no encontrado"}

    agente.password = nueva_password
    db.commit()

    return {
        "status": "ok",
        "usuario": usuario,
        "token_usado": token,
        "password_actualizada": True,
    }


SOPORTE_FUNCTIONS = {
    "leer_ticket": leer_ticket,
    "verificar_conectividad": verificar_conectividad,
    "obtener_configuracion": obtener_configuracion,
    "buscar_tickets": buscar_tickets,
    "resetear_credenciales_agente": resetear_credenciales_agente,
}
