from app.main import app


def test_no_hay_endpoint_directo_para_transferir():
    paths = [route.path for route in app.routes]
    prohibidos = [p for p in paths if "transferir" in p.lower()]
    assert prohibidos == [], (
        f"Existe(n) endpoint(s) que exponen transferir() directamente: {prohibidos}. "
        "Esto rompe la regla de aislamiento (IND-3)."
    )


def test_no_hay_endpoint_directo_para_consultar_saldo():
    paths = [route.path for route in app.routes]
    prohibidos = [p for p in paths if "saldo" in p.lower() and "chat" not in p.lower()]
    assert prohibidos == [], (
        f"Existe(n) endpoint(s) que exponen consultar_saldo() directamente: {prohibidos}. "
        "Esto rompe la regla de aislamiento (IND-3)."
    )


def test_unicos_endpoints_del_escenario_banca():
    paths = sorted(
        route.path for route in app.routes if "banca" in route.path.lower()
    )
    assert paths == ["/chat/banca", "/chat/banca/reset"], (
        f"Endpoints inesperados para el escenario banca: {paths}"
    )


ESCENARIOS = ["banca", "ecommerce", "soporte", "salud"]

FUNCIONES_ESLABON2 = [
    "transferir", "aplicar_descuento", "crear_pedido", "buscar_disponibilidad",
    "verificar_conectividad", "obtener_configuracion", "buscar_tickets",
    "consultar_historial", "buscar_en_historiales",
    "consultar_movimientos_detallados", "solicitar_aumento_limite",
    "actualizar_diagnostico", "exportar_historiales_completos",
    "buscar_en_resenas", "actualizar_inventario_masivo",
    "resetear_credenciales_agente",
    "consultar_saldos_todas", "transferencia_masiva",
]


def test_ninguna_funcion_eslabon2_tiene_endpoint_propio():
    paths = [route.path.lower() for route in app.routes]
    for fn_name in FUNCIONES_ESLABON2:
        prohibidos = [p for p in paths if fn_name.lower() in p]
        assert prohibidos == [], (
            f"'{fn_name}' aparece expuesto en un endpoint fuera de /chat/<escenario>: "
            f"{prohibidos}. Rompe la regla de aislamiento (IND-3)."
        )


def test_cada_escenario_tiene_solo_chat_y_reset():
    for escenario in ESCENARIOS:
        paths = sorted(
            route.path for route in app.routes if f"/chat/{escenario}" in route.path
        )
        esperado = [f"/chat/{escenario}", f"/chat/{escenario}/reset"]
        assert paths == esperado, (
            f"Endpoints inesperados para '{escenario}': {paths} (esperado: {esperado})"
        )
