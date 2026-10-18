from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Producto, Pedido

router = APIRouter(prefix="/admin/ecommerce", tags=["admin-ecommerce"])


@router.get("/estado")
def estado_ecommerce(db: Session = Depends(get_db)):
    productos = db.query(Producto).order_by(Producto.id).all()
    pedidos = db.query(Pedido).order_by(Pedido.timestamp.desc()).limit(20).all()
    return {
        "productos": [
            {
                "id": p.id, "nombre": p.nombre, "categoria": p.categoria,
                "precio": float(p.precio), "stock": p.stock,
                "descuento_pct": float(p.descuento_pct),
            }
            for p in productos
        ],
        "pedidos": [
            {
                "id": ped.id, "producto_id": ped.producto_id, "cantidad": ped.cantidad,
                "precio_unitario_aplicado": float(ped.precio_unitario_aplicado),
                "cliente": ped.cliente,
                "timestamp": ped.timestamp.isoformat() if ped.timestamp else None,
            }
            for ped in pedidos
        ],
    }
