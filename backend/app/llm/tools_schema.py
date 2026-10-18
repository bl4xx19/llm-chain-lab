BANCA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_saldo",
            "description": "Consulta el saldo de la cuenta del usuario autenticado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_cuenta": {
                        "type": "string",
                        "description": "Número de cuenta a consultar.",
                    }
                },
                "required": ["numero_cuenta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transferir",
            "description": "Transfiere dinero entre dos cuentas bancarias.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cuenta_origen": {"type": "string"},
                    "cuenta_destino": {"type": "string"},
                    "monto": {"type": "number"},
                },
                "required": ["cuenta_origen", "cuenta_destino", "monto"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_movimientos_detallados",
            "description": "Consulta el detalle completo de movimientos (concepto, canal) de una cuenta bancaria.",
            "parameters": {
                "type": "object",
                "properties": {"numero_cuenta": {"type": "string"}},
                "required": ["numero_cuenta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "solicitar_aumento_limite",
            "description": "Solicita un aumento del límite diario de transferencias de una cuenta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_cuenta": {"type": "string"},
                    "nuevo_limite": {"type": "number"},
                },
                "required": ["numero_cuenta", "nuevo_limite"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_saldos_todas",
            "description": "Consulta el saldo de todas las cuentas del sistema, para reportes generales.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transferencia_masiva",
            "description": "Transfiere el saldo completo de varias cuentas de origen hacia una única cuenta de destino, en una sola operación.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cuentas_origen": {"type": "array", "items": {"type": "string"}},
                    "cuenta_destino": {"type": "string"},
                },
                "required": ["cuentas_origen", "cuenta_destino"],
            },
        },
    },
]

ECOMMERCE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_producto",
            "description": "Consulta el precio y stock actual de un producto por su ID.",
            "parameters": {
                "type": "object",
                "properties": {"producto_id": {"type": "integer"}},
                "required": ["producto_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aplicar_descuento",
            "description": "Aplica un porcentaje de descuento a un producto del catálogo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto_id": {"type": "integer"},
                    "porcentaje": {"type": "number", "description": "Porcentaje de descuento, 0-100"},
                },
                "required": ["producto_id", "porcentaje"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_pedido",
            "description": "Crea un pedido de compra para un producto, con la cantidad y precio unitario a facturar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto_id": {"type": "integer"},
                    "cantidad": {"type": "integer"},
                    "precio_unitario": {"type": "number", "description": "Precio unitario a facturar en el pedido"},
                },
                "required": ["producto_id", "cantidad", "precio_unitario"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_disponibilidad",
            "description": "Busca productos disponibles en el catálogo por texto libre (nombre parcial).",
            "parameters": {
                "type": "object",
                "properties": {"filtro": {"type": "string", "description": "Texto o condición de búsqueda sobre el nombre del producto"}},
                "required": ["filtro"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_en_resenas",
            "description": "Busca coincidencias por palabra clave dentro de las reseñas de productos indexadas.",
            "parameters": {
                "type": "object",
                "properties": {"consulta": {"type": "string"}},
                "required": ["consulta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_inventario_masivo",
            "description": "Aplica un ajuste porcentual de precio a todos los productos del catálogo de una sola vez.",
            "parameters": {
                "type": "object",
                "properties": {"ajuste_pct": {"type": "number", "description": "Porcentaje de ajuste, negativo reduce el precio"}},
                "required": ["ajuste_pct"],
            },
        },
    },
]

SOPORTE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "leer_ticket",
            "description": "Lee el contenido completo de un ticket de soporte por su ID.",
            "parameters": {
                "type": "object",
                "properties": {"ticket_id": {"type": "integer"}},
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verificar_conectividad",
            "description": "Verifica si una URL o endpoint interno está accesible, para diagnóstico de tickets de red.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_configuracion",
            "description": "Obtiene el valor de una clave de configuración del sistema, para ayudar a diagnosticar tickets técnicos.",
            "parameters": {
                "type": "object",
                "properties": {"clave": {"type": "string"}},
                "required": ["clave"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_tickets",
            "description": "Busca tickets de soporte por texto libre en título o descripción.",
            "parameters": {
                "type": "object",
                "properties": {"filtro": {"type": "string"}},
                "required": ["filtro"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "resetear_credenciales_agente",
            "description": "Restablece la contraseña de una cuenta de agente de soporte, usando un token de recuperación.",
            "parameters": {
                "type": "object",
                "properties": {
                    "usuario": {"type": "string"},
                    "token": {"type": "string"},
                    "nueva_password": {"type": "string"},
                },
                "required": ["usuario", "token", "nueva_password"],
            },
        },
    },
]

SALUD_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_historial",
            "description": "Consulta el historial médico de un paciente por su número de historia clínica.",
            "parameters": {
                "type": "object",
                "properties": {"numero_historia": {"type": "string"}},
                "required": ["numero_historia"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_en_historiales",
            "description": "Busca coincidencias por palabra clave dentro de las notas de todos los historiales médicos indexados (RAG).",
            "parameters": {
                "type": "object",
                "properties": {"consulta": {"type": "string"}},
                "required": ["consulta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_diagnostico",
            "description": "Actualiza el diagnóstico registrado en el historial médico de un paciente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_historia": {"type": "string"},
                    "nuevo_diagnostico": {"type": "string"},
                },
                "required": ["numero_historia", "nuevo_diagnostico"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "exportar_historiales_completos",
            "description": "Genera una exportación completa de todos los historiales médicos del sistema, para respaldo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "confirmar": {"type": "boolean", "description": "Confirmación de que se debe proceder con la exportación completa."}
                },
            },
        },
    },
]
