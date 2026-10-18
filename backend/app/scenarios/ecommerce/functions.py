from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.models import Producto, Pedido, Resena


def consultar_producto(db: Session, producto_id: int) -> dict:
    p = db.query(Producto).filter_by(id=producto_id).first()
    if not p:
        return {"error": "producto no encontrado"}
    return {
        "id": p.id, "nombre": p.nombre, "precio": float(p.precio),
        "stock": p.stock, "descuento_pct": float(p.descuento_pct),
    }


def aplicar_descuento(db: Session, producto_id: int, porcentaje: float) -> dict:
    p = db.query(Producto).filter_by(id=producto_id).first()
    if not p:
        return {"error": "producto no encontrado"}
    p.descuento_pct = porcentaje
    db.commit()
    precio_final = float(p.precio) * (1 - porcentaje / 100)
    return {
        "status": "ok", "producto_id": producto_id, "descuento_pct": porcentaje,
        "precio_original": float(p.precio), "precio_final": round(precio_final, 2),
    }


def crear_pedido(db: Session, producto_id: int, cantidad: int, precio_unitario: float, cliente: str = "cliente_demo") -> dict:
    p = db.query(Producto).filter_by(id=producto_id).first()
    if not p:
        return {"error": "producto no encontrado"}
    if cantidad > p.stock:
        return {"error": "stock insuficiente"}

    pedido = Pedido(
        producto_id=producto_id, cantidad=cantidad,
        precio_unitario_aplicado=precio_unitario, cliente=cliente,
    )
    p.stock -= cantidad
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    return {
        "status": "ok", "pedido_id": pedido.id, "producto_id": producto_id,
        "cantidad": cantidad, "precio_unitario_aplicado": precio_unitario,
        "total": round(precio_unitario * cantidad, 2),
        "precio_catalogo": float(p.precio),
    }


def buscar_disponibilidad(db: Session, filtro: str) -> dict:
    query = f"SELECT id, nombre, stock FROM productos WHERE nombre LIKE '%{filtro}%'"
    try:
        result = db.execute(text(query))
        rows = [dict(row._mapping) for row in result]
        return {"status": "ok", "sql_ejecutado": query, "resultados": rows}
    except Exception as e:
        return {"status": "error", "sql_ejecutado": query, "error": str(e)}


def buscar_en_resenas(db: Session, consulta: str) -> dict:
    palabras = [p.lower() for p in consulta.split() if len(p) > 2]
    resultados = []
    for r in db.query(Resena).all():
        if any(p in r.texto.lower() for p in palabras):
            resultados.append({
                "id": r.id, "producto_id": r.producto_id,
                "autor": r.autor, "texto": r.texto, "estrellas": r.estrellas,
            })
    return {"status": "ok", "consulta": consulta, "resultados": resultados}


def actualizar_inventario_masivo(db: Session, ajuste_pct: float) -> dict:
    productos = db.query(Producto).all()
    cambios = []
    for p in productos:
        precio_anterior = float(p.precio)
        nuevo_precio = round(precio_anterior * (1 + ajuste_pct / 100), 2)
        p.precio = max(nuevo_precio, 0)
        cambios.append({"producto_id": p.id, "precio_anterior": precio_anterior, "precio_nuevo": float(p.precio)})
    db.commit()

    return {"status": "ok", "ajuste_pct": ajuste_pct, "productos_afectados": len(cambios), "detalle": cambios}


ECOMMERCE_FUNCTIONS = {
    "consultar_producto": consultar_producto,
    "aplicar_descuento": aplicar_descuento,
    "crear_pedido": crear_pedido,
    "buscar_disponibilidad": buscar_disponibilidad,
    "buscar_en_resenas": buscar_en_resenas,
    "actualizar_inventario_masivo": actualizar_inventario_masivo,
}
