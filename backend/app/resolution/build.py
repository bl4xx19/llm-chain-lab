from app.resolution.catalog import RESOLUTION_CATALOG

FUNCTION_TO_CADENA = {
    "consultar_historial": "1.1",
    "actualizar_diagnostico": "1.3",
    "exportar_historiales_completos": "1.4",
    "aplicar_descuento": "2.1",
    "crear_pedido": "2.2",
    "buscar_disponibilidad": "2.3",
    "actualizar_inventario_masivo": "2.4",
    "verificar_conectividad": "3.2",
    "obtener_configuracion": "3.1",
    "buscar_tickets": "3.3",
    "resetear_credenciales_agente": "3.4",
    "transferir": "4.1",
    "consultar_movimientos_detallados": "4.2",
    "solicitar_aumento_limite": "4.3",
    "transferencia_masiva": "4.4",
}

CADENAS_POR_ESCENARIO = {
    "salud": ["1.1", "1.2", "1.3", "1.4"],
    "ecommerce": ["2.1", "2.2", "2.3", "2.4"],
    "soporte": ["3.1", "3.2", "3.3", "3.4"],
    "banca": ["4.1", "4.2", "4.3", "4.4"],
}

PLACEHOLDERS_GENERICOS = {
    "numero_historia": "el número de historia de otro paciente",
    "consulta": "un tema de búsqueda cualquiera",
    "producto_id": "un producto del catálogo",
    "porcentaje": "un porcentaje elegido por quien pregunta",
    "precio_unitario": "un precio distinto al del catálogo",
    "precio_catalogo": "el precio real del catálogo",
    "filtro": "un texto de búsqueda con sintaxis SQL",
    "sql_ejecutado": "la consulta SQL resultante, ya alterada",
    "url": "una dirección de red interna",
    "clave": "una clave de configuración sensible",
    "cuenta_origen": "una cuenta que no es la del usuario autenticado",
    "cuenta_destino": "la cuenta de destino elegida por el atacante",
    "monto": "el monto elegido por quien pregunta",
    "numero_cuenta": "una cuenta que no es la del usuario autenticado",
    "limite_anterior": "el límite original de la cuenta",
    "limite_nuevo": "un límite más alto, elegido por quien pregunta",
    "diagnostico_anterior": "el diagnóstico original del paciente",
    "diagnostico_nuevo": "un diagnóstico distinto, elegido por quien pregunta",
    "total_historiales": "todos",
    "ajuste_pct": "un porcentaje elegido por quien pregunta",
    "productos_afectados": "todos",
    "usuario": "una cuenta de agente con privilegios",
    "cuentas_origen": "varias cuentas del sistema",
    "cuentas_drenadas": "varias",
}


class _SafeDict(dict):
    def __missing__(self, key):
        return f"[{key}]"


def _resolver_cadena_id(log_entry) -> str | None:
    if log_entry.cadena_id:
        return log_entry.cadena_id

    if log_entry.function_called == "buscar_en_historiales":
        return "1.2"

    return FUNCTION_TO_CADENA.get(log_entry.function_called)


def _interpolar(texto: str, contexto: dict) -> str:
    return texto.format_map(_SafeDict(contexto))


def build_resolution(log_entry) -> dict | None:
    cadena_id = _resolver_cadena_id(log_entry)
    if not cadena_id or cadena_id not in RESOLUTION_CATALOG:
        return None

    entry = RESOLUTION_CATALOG[cadena_id]

    contexto = {}
    contexto.update(log_entry.function_args or {})
    resultado = log_entry.function_result or {}
    for k, v in resultado.items():
        if k != "resultados":
            contexto[k] = v

    def interpolar_bloque(bloque: dict) -> dict:
        return {
            "tecnico": _interpolar(bloque["tecnico"], contexto),
            "no_tecnico": _interpolar(bloque["no_tecnico"], contexto),
        }

    return {
        "cadena_id": cadena_id,
        "nivel": entry.get("nivel"),
        "titulo": entry["titulo"],
        "eslabon_1": entry["eslabon_1"],
        "eslabon_2": entry["eslabon_2"],
        "que_paso": interpolar_bloque(entry["que_paso"]),
        "que_esta_en_riesgo": interpolar_bloque(entry["que_esta_en_riesgo"]),
        "como_se_resuelve": interpolar_bloque(entry["como_se_resuelve"]),
        "cvss": entry["cvss"],
        "owasp_risk_rating": entry["owasp_risk_rating"],
        "log_id": log_entry.id,
    }


def build_resolution_generic(cadena_id: str) -> dict | None:
    if cadena_id not in RESOLUTION_CATALOG:
        return None

    entry = RESOLUTION_CATALOG[cadena_id]

    def interpolar_generico(bloque: dict) -> dict:
        return {
            "tecnico": _interpolar(bloque["tecnico"], PLACEHOLDERS_GENERICOS),
            "no_tecnico": _interpolar(bloque["no_tecnico"], PLACEHOLDERS_GENERICOS),
        }

    return {
        "cadena_id": cadena_id,
        "nivel": entry.get("nivel"),
        "titulo": entry["titulo"],
        "eslabon_1": entry["eslabon_1"],
        "eslabon_2": entry["eslabon_2"],
        "que_paso": interpolar_generico(entry["que_paso"]),
        "que_esta_en_riesgo": interpolar_generico(entry["que_esta_en_riesgo"]),
        "como_se_resuelve": interpolar_generico(entry["como_se_resuelve"]),
        "cvss": entry["cvss"],
        "owasp_risk_rating": entry["owasp_risk_rating"],
        "log_id": None,
    }


def build_catalogo_escenario(escenario: str) -> list[dict]:
    cadenas = CADENAS_POR_ESCENARIO.get(escenario, [])
    resultado = []
    for cadena_id in cadenas:
        r = build_resolution_generic(cadena_id)
        if r:
            resultado.append(r)
    return resultado
