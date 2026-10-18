RESOLUTION_CATALOG = {

    "1.1": {
        "nivel": 1,
        "titulo": "Acceso a historial médico ajeno vía prompt injection indirecta",
        "eslabon_1": "LLM01: Prompt Injection Directa",
        "eslabon_2": "A01: Broken Access Control",
        "que_paso": {
            "tecnico": "El LLM invocó consultar_historial() con numero_historia="
                       "'{numero_historia}', un valor distinto al paciente autenticado "
                       "de la sesión, sin que el backend validara la pertenencia del "
                       "registro antes de devolverlo.",
            "no_tecnico": "El asistente le mostró a un paciente el historial médico "
                          "de otra persona distinta, solo porque se lo pidió.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Confidencialidad de datos clínicos de terceros: cualquier "
                       "número de historia válido es alcanzable sin autorización "
                       "adicional (A01 Broken Access Control).",
            "no_tecnico": "Los diagnósticos y notas médicas de cualquier paciente del "
                          "sistema, incluyendo información sensible como tratamientos "
                          "psiquiátricos o de salud reproductiva.",
        },
        "como_se_resuelve": {
            "tecnico": "Validar en consultar_historial() que numero_historia "
                       "corresponda al paciente autenticado de la sesión (server-side, "
                       "nunca solo en el prompt). Aplicar control de acceso por fila "
                       "(row-level security) a nivel de base de datos si es posible.",
            "no_tecnico": "El sistema necesita comprobar de verdad que cada persona "
                          "solo pueda ver su propio historial, con una regla que no "
                          "dependa de que el asistente 'decida' bien.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N", "score": 5.3},
        "owasp_risk_rating": "High",
    },

    "1.2": {
        "nivel": 2,
        "titulo": "Fuga de información de otros pacientes vía búsqueda sin alcance",
        "eslabon_1": "LLM06: Sensitive Information Disclosure",
        "eslabon_2": "A01: Broken Access Control",
        "que_paso": {
            "tecnico": "buscar_en_historiales() ejecutó la búsqueda '{consulta}' sobre "
                       "TODOS los historiales indexados, sin filtrar por el paciente "
                       "autenticado de la sesión, y devolvió los resultados completos "
                       "al LLM como contexto de recuperación.",
            "no_tecnico": "Al buscar un tema de salud, el asistente mostró información "
                          "de otros pacientes que coincidían con esa búsqueda, no solo "
                          "la del usuario que preguntó.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Confidencialidad de datos clínicos vía el componente de "
                       "recuperación (RAG): la ausencia de scope por paciente convierte "
                       "cualquier búsqueda en un vector de disclosure masivo.",
            "no_tecnico": "La privacidad de todos los pacientes cuyos historiales "
                          "coincidan por palabra clave con lo que alguien más pregunte.",
        },
        "como_se_resuelve": {
            "tecnico": "Filtrar la recuperación por paciente_id == sesión autenticada "
                       "antes de pasar los resultados al LLM, no después. El RAG debe "
                       "respetar el mismo control de acceso que el resto del sistema.",
            "no_tecnico": "La búsqueda del asistente necesita estar limitada solo a la "
                          "información de la persona que está preguntando, nunca a la "
                          "de todos los pacientes del sistema.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", "score": 7.5},
        "owasp_risk_rating": "High",
    },

    "1.3": {
        "nivel": 3,
        "titulo": "Modificación de diagnóstico sin segunda validación clínica",
        "eslabon_1": "LLM08: Excessive Agency",
        "eslabon_2": "A04: Insecure Design",
        "que_paso": {
            "tecnico": "El LLM invocó actualizar_diagnostico() y cambió el campo "
                       "diagnostico de '{diagnostico_anterior}' a "
                       "'{diagnostico_nuevo}' en una sola interacción, sin que exista "
                       "ningún flujo de segunda validación por un profesional humano.",
            "no_tecnico": "El asistente cambió el diagnóstico registrado de un "
                          "paciente solo porque alguien se lo pidió en la conversación, "
                          "sin que ningún médico lo revisara.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Integridad de datos clínicos (A08): a diferencia de las "
                       "cadenas 1.1/1.2 (solo lectura), aquí se escribe sobre un "
                       "registro médico real sin control de integridad ni auditoría "
                       "de cambios.",
            "no_tecnico": "La exactitud del historial médico de un paciente, que "
                          "podría terminar con un diagnóstico incorrecto sin que nadie "
                          "lo note a tiempo.",
        },
        "como_se_resuelve": {
            "tecnico": "Cualquier escritura sobre un dato clínico debería requerir "
                       "confirmación de un profesional humano (human-in-the-loop) "
                       "antes de aplicarse, más un registro de auditoría de quién y "
                       "cuándo lo cambió.",
            "no_tecnico": "Cambiar un diagnóstico médico nunca debería depender solo "
                          "de una conversación con un asistente, siempre necesita que "
                          "un médico lo confirme.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N", "score": 7.5},
        "owasp_risk_rating": "High",
    },

    "1.4": {
        "nivel": 4,
        "titulo": "Exportación masiva de historiales vía documento indexado malicioso",
        "eslabon_1": "LLM01: Prompt Injection Indirecta",
        "eslabon_2": "A01: Broken Access Control (alcance masivo)",
        "que_paso": {
            "tecnico": "Un historial plantado (HC-9999) contenía una instrucción "
                       "indexada que indujo al LLM a invocar "
                       "exportar_historiales_completos(), la cual devolvió "
                       "{total_historiales} historiales completos del sistema, sin "
                       "ningún filtro ni control de acceso.",
            "no_tecnico": "Una nota falsa escondida en el sistema logró que el "
                          "asistente entregara de golpe los datos médicos de todos "
                          "los pacientes, no solo de uno.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Esto es una brecha de datos a escala completa (A01, alcance "
                       "masivo): el mismo mecanismo de confianza ciega en contenido "
                       "indexado que en 1.2, pero conectado a una función de impacto "
                       "mucho mayor.",
            "no_tecnico": "La privacidad médica de TODOS los pacientes del sistema al "
                          "mismo tiempo, no la de una sola persona: el tipo de "
                          "incidente que se reportaría como brecha de datos grave.",
        },
        "como_se_resuelve": {
            "tecnico": "Ninguna función de exportación masiva debería ser alcanzable "
                       "por function calling de un LLM sin un flujo de aprobación "
                       "administrativa separado, y el contenido indexado (RAG) nunca "
                       "debe poder disparar acciones de alto impacto.",
            "no_tecnico": "Una función tan poderosa como 'exportar todos los "
                          "historiales' nunca debería poder activarse solo por una "
                          "nota escondida en el sistema.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", "score": 7.5},
        "owasp_risk_rating": "High",
    },

    "2.1": {
        "nivel": 1,
        "titulo": "Descuento aplicado sin autorización de rol",
        "eslabon_1": "LLM08: Excessive Agency",
        "eslabon_2": "A01: Broken Access Control",
        "que_paso": {
            "tecnico": "El LLM invocó aplicar_descuento() con producto_id={producto_id} "
                       "y porcentaje={porcentaje}, sin que el backend validara que "
                       "quien lo solicita tenga rol de administrador.",
            "no_tecnico": "Cualquier persona que hable con el asistente pudo pedirle "
                          "que le pusiera descuento a un producto, y lo hizo sin pedir "
                          "ninguna autorización real.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Integridad de precios del catálogo: la función de negocio "
                       "crítica no tiene control de rol, solo la buena voluntad del LLM "
                       "de negarse (A01 Broken Access Control por agencia excesiva).",
            "no_tecnico": "Las ganancias de la tienda, ya que cualquier cliente podría "
                          "convencer al asistente de bajar precios sin permiso real.",
        },
        "como_se_resuelve": {
            "tecnico": "Verificar rol/permiso del usuario autenticado antes de "
                       "ejecutar aplicar_descuento(), en el backend, independientemente "
                       "de lo que el LLM decida.",
            "no_tecnico": "La tienda necesita comprobar quién es realmente la persona "
                          "antes de dejar que se cambien los precios, no solo confiar "
                          "en lo que dice el chat.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N", "score": 5.3},
        "owasp_risk_rating": "Medium",
    },

    "2.2": {
        "nivel": 2,
        "titulo": "Precio de pedido alterado sin regla de negocio",
        "eslabon_1": "LLM01: Prompt Injection Directa",
        "eslabon_2": "A04: Insecure Design",
        "que_paso": {
            "tecnico": "crear_pedido() aceptó precio_unitario={precio_unitario} "
                       "provisto por el LLM en vez de recalcularlo siempre desde "
                       "Producto.precio ({precio_catalogo}). No existe una regla de "
                       "negocio que fuerce esa igualdad.",
            "no_tecnico": "Un cliente le dijo al asistente un precio distinto al real, "
                          "y el pedido se generó con ese precio inventado.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Integridad financiera de las órdenes: ausencia de validación "
                       "de reglas de negocio críticas (A04 Insecure Design), no solo "
                       "un control de acceso faltante.",
            "no_tecnico": "El dinero real que la tienda debería cobrar por cada "
                          "producto vendido.",
        },
        "como_se_resuelve": {
            "tecnico": "Nunca aceptar precio_unitario como parámetro de entrada; "
                       "recalcularlo siempre server-side desde el catálogo al momento "
                       "de crear el pedido.",
            "no_tecnico": "El sistema debe usar siempre el precio real que tiene "
                          "guardado, sin importar lo que diga la conversación.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N", "score": 5.3},
        "owasp_risk_rating": "High",
    },

    "2.3": {
        "nivel": 3,
        "titulo": "Restricción insuficiente de alcance en consultas de búsqueda",
        "eslabon_1": "LLM02: Insecure Output Handling",
        "eslabon_2": "A01: Broken Access Control",
        "que_paso": {
            "tecnico": "buscar_disponibilidad() usó el filtro '{filtro}' generado por el "
                       "LLM sin validar su alcance: un filtro vacío o comodín ('%') no "
                       "requiere romper la consulta, y aun así devuelve el catálogo "
                       "completo sin ninguna condición real de búsqueda. Se probó "
                       "explícitamente si el modelo podía escalar a una inyección SQL "
                       "real (con ruptura de comillas) y consistentemente se rehusó a "
                       "hacerlo; el mecanismo real y reproducible es este, no la "
                       "inyección de sintaxis.",
            "no_tecnico": "El asistente, al pedirle 'muéstrame todo sin excepción', dejó "
                          "el campo de búsqueda vacío o con un comodín, y el sistema no "
                          "revisó que eso significaba 'ignora cualquier restricción' "
                          "antes de mostrar todo el catálogo.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Confidencialidad del catálogo completo, no de otras tablas de la "
                       "base de datos: a diferencia de una inyección SQL con ruptura de "
                       "consulta, este mecanismo no demuestra capacidad de leer datos "
                       "fuera del recurso ya consultado por la función.",
            "no_tecnico": "Que cualquiera pueda ver el catálogo completo de la tienda de "
                          "una sola vez, sin que el sistema distinga entre una búsqueda "
                          "puntual y una petición de 'mostrar todo'.",
        },
        "como_se_resuelve": {
            "tecnico": "Validar que el filtro de búsqueda tenga contenido real antes de "
                       "ejecutar la consulta (rechazar vacío o comodines puros), además "
                       "de usar siempre consultas parametrizadas como buena práctica "
                       "general independiente de este hallazgo específico.",
            "no_tecnico": "El sistema debería exigir que una búsqueda tenga un criterio "
                          "real antes de mostrar resultados, en vez de interpretar 'sin "
                          "texto' como 'muéstralo todo'.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", "score": 7.5},
        "owasp_risk_rating": "High",
    },

    "2.4": {
        "nivel": 4,
        "titulo": "Actualización masiva de inventario vía reseña maliciosa",
        "eslabon_1": "LLM01: Prompt Injection Indirecta",
        "eslabon_2": "A01: Broken Access Control (alcance masivo)",
        "que_paso": {
            "tecnico": "Una reseña de producto plantada indujo al LLM a invocar "
                       "actualizar_inventario_masivo() con ajuste_pct={ajuste_pct}, "
                       "afectando a {productos_afectados} productos del catálogo de "
                       "una sola vez, sin ninguna aprobación administrativa.",
            "no_tecnico": "Un comentario falso disfrazado de reseña de producto logró "
                          "que el asistente cambiara los precios de toda la tienda de "
                          "golpe, no solo de un producto.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Integridad del catálogo completo (A08, alcance masivo): el "
                       "mismo patrón de confianza ciega en contenido indexado que en "
                       "2.1/2.2, pero conectado a una función que afecta todo el "
                       "inventario en una sola llamada.",
            "no_tecnico": "Las finanzas de la tienda completa, ya que todos los "
                          "precios podrían quedar mal de una sola vez, no solo uno.",
        },
        "como_se_resuelve": {
            "tecnico": "Ninguna función de actualización masiva debería ser "
                       "alcanzable por function calling sin un flujo de aprobación "
                       "administrativa separado; el contenido de reseñas indexado "
                       "nunca debe poder disparar acciones de escritura.",
            "no_tecnico": "Cambiar el precio de todo el catálogo de una sola vez "
                          "nunca debería poder activarse solo por un comentario de un "
                          "cliente.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N", "score": 7.5},
        "owasp_risk_rating": "High",
    },

    "3.2": {
        "nivel": 2,
        "titulo": "SSRF vía instrucción oculta en un ticket",
        "eslabon_1": "LLM01: Prompt Injection Indirecta",
        "eslabon_2": "A10: Server-Side Request Forgery",
        "que_paso": {
            "tecnico": "Un ticket contenía una nota de 'diagnóstico estándar' que "
                       "indujo al LLM a invocar verificar_conectividad() contra "
                       "'{url}', sin ninguna restricción de destino en la función.",
            "no_tecnico": "Un mensaje escondido dentro de un ticket logró que el "
                          "asistente intentara conectarse a una dirección interna del "
                          "sistema, sin que nadie se lo pidiera directamente.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Infraestructura interna: si el backend corre en una nube real "
                       "(AWS/GCP/Azure), esta función podría alcanzar el endpoint de "
                       "metadata real y filtrar credenciales de la instancia.",
            "no_tecnico": "Los sistemas internos de la empresa que nunca deberían ser "
                          "alcanzables desde una conversación de soporte.",
        },
        "como_se_resuelve": {
            "tecnico": "Restringir verificar_conectividad() con una allowlist de "
                       "dominios/rangos permitidos, bloqueando explícitamente rangos "
                       "de metadata de nube e IPs privadas (169.254.169.254, "
                       "127.0.0.0/8, 10.0.0.0/8, etc.).",
            "no_tecnico": "El asistente de soporte nunca debería poder intentar "
                          "conectarse a direcciones internas del sistema, sin importar "
                          "quién se lo pida ni cómo se lo pidan.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N", "score": 8.6},
        "owasp_risk_rating": "High",
    },

    "3.1": {
        "nivel": 1,
        "titulo": "Exposición de configuración sensible sin control de acceso",
        "eslabon_1": "LLM08: Excessive Agency",
        "eslabon_2": "A05: Security Misconfiguration",
        "que_paso": {
            "tecnico": "obtener_configuracion() devolvió el valor de la clave "
                       "'{clave}' sin ninguna restricción sobre qué claves son "
                       "consultables desde una herramienta de diagnóstico de tickets.",
            "no_tecnico": "El asistente entregó una contraseña interna del sistema "
                          "solo porque alguien se la pidió con una excusa razonable.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Secretos operativos: passwords, API keys y credenciales "
                       "internas quedan expuestas a cualquier conversación de soporte, "
                       "sin distinguir configuración pública de sensible.",
            "no_tecnico": "Las llaves de acceso a otros sistemas de la empresa, que "
                          "podrían usarse para entrar a lugares que no deberían ser "
                          "accesibles desde un chat de soporte.",
        },
        "como_se_resuelve": {
            "tecnico": "Separar configuración pública de secretos (usar un vault o "
                       "gestor de secretos dedicado); nunca exponer una función "
                       "genérica de 'obtener cualquier clave' a una herramienta con "
                       "LLM.",
            "no_tecnico": "Las contraseñas y llaves de acceso nunca deberían estar al "
                          "alcance de un asistente que responde preguntas de soporte.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", "score": 7.5},
        "owasp_risk_rating": "High",
    },

    "3.3": {
        "nivel": 3,
        "titulo": "Restricción insuficiente de alcance en consultas de búsqueda",
        "eslabon_1": "LLM02: Insecure Output Handling",
        "eslabon_2": "A01: Broken Access Control",
        "que_paso": {
            "tecnico": "buscar_tickets() usó el filtro '{filtro}' generado por el LLM "
                       "sin validar su alcance: un filtro vacío o comodín ('%') no "
                       "requiere romper la consulta, y aun así devuelve todos los "
                       "tickets sin ninguna condición real de búsqueda. Se probó "
                       "explícitamente si el modelo podía escalar a una inyección SQL "
                       "real (con ruptura de comillas) y consistentemente se rehusó a "
                       "hacerlo; el mecanismo real y reproducible es este, no la "
                       "inyección de sintaxis.",
            "no_tecnico": "El asistente, al pedirle 'muéstrame todos los tickets sin "
                          "excepción', dejó el campo de búsqueda vacío, y el sistema no "
                          "revisó que eso significaba 'ignora cualquier restricción' "
                          "antes de mostrar todos los tickets.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Confidencialidad del conjunto completo de tickets, no de otras "
                       "tablas de la base de datos: a diferencia de una inyección SQL "
                       "con ruptura de consulta, este mecanismo no demuestra capacidad "
                       "de leer datos fuera del recurso ya consultado por la función.",
            "no_tecnico": "Que cualquiera pueda ver todos los tickets de soporte de "
                          "todos los clientes de una sola vez, sin que el sistema "
                          "distinga entre una búsqueda puntual y una petición de "
                          "'mostrar todo'.",
        },
        "como_se_resuelve": {
            "tecnico": "Validar que el filtro de búsqueda tenga contenido real antes de "
                       "ejecutar la consulta (rechazar vacío o comodines puros), mismo "
                       "patrón que en 2.3, además de usar consultas parametrizadas como "
                       "buena práctica general.",
            "no_tecnico": "El sistema de tickets necesita el mismo tipo de protección "
                          "que cualquier otro buscador: exigir un criterio real antes de "
                          "mostrar resultados, en vez de interpretar 'sin texto' como "
                          "'muéstralo todo'.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", "score": 7.5},
        "owasp_risk_rating": "High",
    },

    "3.4": {
        "nivel": 4,
        "titulo": "Toma de cuenta de agente vía token filtrado en ticket",
        "eslabon_1": "LLM01 + LLM08 encadenados: Prompt Injection Indirecta + Excessive Agency",
        "eslabon_2": "A07: Identification and Authentication Failures (account takeover)",
        "que_paso": {
            "tecnico": "En un primer paso, el LLM leyó un ticket que filtraba un "
                       "token de recuperación en texto plano. En un segundo paso, "
                       "invocó resetear_credenciales_agente() con usuario="
                       "'{usuario}' y ese mismo token, sin que el backend validara "
                       "si el token era real ni si seguía vigente.",
            "no_tecnico": "Un dato sensible quedó expuesto en un ticket de soporte, y "
                          "el asistente lo usó para cambiarle la contraseña a una "
                          "cuenta de agente, sin comprobar que ese dato fuera legítimo.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Autenticación del sistema completo (A07, account takeover): "
                       "esta es la primera cadena que requiere dos pasos: "
                       "reconocimiento (leer el ticket) seguido de acción (resetear "
                       "credenciales): y compromete una cuenta con privilegios de "
                       "agente, no solo un dato puntual.",
            "no_tecnico": "El acceso completo a una cuenta de soporte, que después "
                          "podría usarse para hacer cualquier otra cosa que ese "
                          "agente pudiera hacer normalmente.",
        },
        "como_se_resuelve": {
            "tecnico": "resetear_credenciales_agente() debe validar el token contra "
                       "un valor real almacenado (con expiración y de un solo uso), "
                       "nunca aceptar cualquier string como válido. Los tickets nunca "
                       "deberían contener tokens de recuperación en texto plano.",
            "no_tecnico": "Cambiar la contraseña de una cuenta necesita comprobar de "
                          "verdad que quien lo pide tiene el código correcto, no solo "
                          "que mencionó algún código.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N", "score": 9.1},
        "owasp_risk_rating": "High",
    },

    "4.1": {
        "nivel": 1,
        "titulo": "Transferencia bancaria no autorizada vía jailbreak",
        "eslabon_1": "LLM01: Jailbreak / Prompt Injection Directa",
        "eslabon_2": "A01: Broken Access Control",
        "que_paso": {
            "tecnico": "El LLM aceptó una instrucción de 'modo desarrollador' dentro "
                       "del mensaje del usuario e invocó transferir() con "
                       "cuenta_origen='{cuenta_origen}', distinta de la cuenta "
                       "autenticada de la sesión, sin validación server-side "
                       "independiente.",
            "no_tecnico": "Alguien le pidió al asistente del banco, con un mensaje "
                          "engañoso, que moviera dinero de una cuenta que no le "
                          "pertenece, y el asistente lo hizo.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Integridad financiera: A01 Broken Access Control sobre la "
                       "función transferir(), que confía en el criterio del LLM en "
                       "vez de validar la titularidad de la cuenta de origen.",
            "no_tecnico": "El dinero de cualquier cliente del banco que use este "
                          "asistente, ya que podría ser transferido sin su permiso.",
        },
        "como_se_resuelve": {
            "tecnico": "Validar cuenta_origen == sesión.usuario_autenticado dentro de "
                       "transferir(), en el backend, nunca solo mediante instrucciones "
                       "en el system prompt.",
            "no_tecnico": "El banco necesita un sistema que compruebe de verdad quién "
                          "puede pedir una transferencia, en vez de confiar en lo que "
                          "dice la conversación con el asistente.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N", "score": 7.5},
        "owasp_risk_rating": "High",
    },

    "4.2": {
        "nivel": 2,
        "titulo": "Exposición de movimientos detallados de cuentas ajenas",
        "eslabon_1": "LLM06: Sensitive Information Disclosure",
        "eslabon_2": "A01: Broken Access Control",
        "que_paso": {
            "tecnico": "El LLM invocó consultar_movimientos_detallados() con "
                       "numero_cuenta='{numero_cuenta}', distinta de la cuenta "
                       "autenticada, y el backend devolvió el historial completo de "
                       "movimientos (concepto, canal) sin validar pertenencia.",
            "no_tecnico": "El asistente mostró el detalle de los movimientos de "
                          "dinero de otra persona, solo porque alguien se lo pidió.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Confidencialidad financiera: a diferencia de consultar_saldo(), "
                       "esta función expone metadata detallada (concepto, canal) de "
                       "cualquier cuenta, ampliando la superficie de disclosure.",
            "no_tecnico": "El detalle de en qué gasta o de dónde recibe dinero "
                          "cualquier cliente del banco, no solo cuánto tiene.",
        },
        "como_se_resuelve": {
            "tecnico": "Aplicar la misma validación de titularidad que debería tener "
                       "consultar_saldo() y transferir(): numero_cuenta debe "
                       "coincidir con la sesión autenticada antes de construir la "
                       "respuesta.",
            "no_tecnico": "El banco debe asegurarse de que el asistente solo pueda "
                          "mostrar el detalle de movimientos de la propia cuenta de "
                          "quien pregunta.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N", "score": 5.3},
        "owasp_risk_rating": "High",
    },

    "4.3": {
        "nivel": 3,
        "titulo": "Aumento de límite de transferencia sin flujo de aprobación",
        "eslabon_1": "LLM08: Excessive Agency",
        "eslabon_2": "A04: Insecure Design",
        "que_paso": {
            "tecnico": "El LLM invocó solicitar_aumento_limite() y cambió el límite "
                       "diario de '{limite_anterior}' a '{limite_nuevo}' en una sola "
                       "interacción, sin ningún paso de aprobación humana, cooldown, "
                       "o verificación de identidad adicional.",
            "no_tecnico": "El asistente subió el límite de cuánto dinero se puede "
                          "transferir en un día, solo porque alguien se lo pidió en "
                          "la conversación.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Control de riesgo financiero: un cambio de límite es una "
                       "decisión de alto impacto que normalmente requeriría un flujo "
                       "de aprobación (maker-checker); aquí el LLM tiene agencia "
                       "completa para ejecutarlo solo.",
            "no_tecnico": "La protección que existe para frenar movimientos grandes "
                          "de dinero en caso de fraude, ya que ese límite se puede "
                          "cambiar con solo pedirlo.",
        },
        "como_se_resuelve": {
            "tecnico": "Los cambios de límites de riesgo no deberían ser ejecutables "
                       "directamente por una función de LLM: requieren un flujo de "
                       "aprobación separado (segundo factor, revisión humana, o "
                       "cooldown antes de aplicarse).",
            "no_tecnico": "Cambiar un límite de seguridad debería necesitar más "
                          "pasos que simplemente pedírselo a un asistente de chat.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N", "score": 5.3},
        "owasp_risk_rating": "High",
    },

    "4.4": {
        "nivel": 4,
        "titulo": "Drenado masivo de múltiples cuentas en una sola operación",
        "eslabon_1": "LLM01 + LLM08 encadenados: Prompt Injection Indirecta + Excessive Agency",
        "eslabon_2": "A08: Software and Data Integrity Failures (alcance masivo)",
        "que_paso": {
            "tecnico": "En un primer paso, el LLM invocó consultar_saldos_todas() y "
                       "obtuvo el saldo de todas las cuentas del sistema sin filtro. "
                       "En un segundo paso, usó esos datos para invocar "
                       "transferencia_masiva() con cuentas_origen='{cuentas_origen}', "
                       "vaciando {cuentas_drenadas} cuentas hacia "
                       "cuenta_destino='{cuenta_destino}' en una sola operación.",
            "no_tecnico": "El asistente primero mostró el dinero de todas las cuentas "
                          "del banco, y después usó esa información para vaciar "
                          "varias cuentas a la vez hacia una sola cuenta.",
        },
        "que_esta_en_riesgo": {
            "tecnico": "Integridad financiera a escala del banco (A01, alcance "
                       "masivo): a diferencia de 4.1 (una sola cuenta), aquí el "
                       "reconocimiento previo permite drenar múltiples cuentas en una "
                       "única interacción: el mayor impacto posible del sistema.",
            "no_tecnico": "El dinero de varios clientes del banco a la vez, no solo "
                          "de uno: el tipo de incidente que sería noticia nacional "
                          "si pasara en un banco real.",
        },
        "como_se_resuelve": {
            "tecnico": "Ninguna función debería poder operar sobre una lista "
                       "arbitraria de cuentas sin límite ni aprobación; "
                       "consultar_saldos_todas() tampoco debería ser alcanzable sin "
                       "un rol administrativo real y auditado.",
            "no_tecnico": "El sistema nunca debería permitir mover dinero de varias "
                          "cuentas distintas en una sola operación, sin importar quién "
                          "lo pida ni cómo lo pida.",
        },
        "cvss": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N", "score": 9.1},
        "owasp_risk_rating": "Critical",
    },
}
