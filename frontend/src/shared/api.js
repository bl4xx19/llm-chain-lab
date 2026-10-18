export async function enviarMensaje(escenario, sessionId, mensaje, opciones = {}) {
  const res = await fetch(`/chat/${escenario}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message: mensaje,
      intento_cadena_id: opciones.cadenaId ?? null,
      tecnica: opciones.tecnica ?? null,
    }),
  });
  if (!res.ok) {
    throw new Error(`Error del servidor: ${res.status}`);
  }
  return res.json();
}

export async function reiniciarSesion(escenario, sessionId) {
  const res = await fetch(`/chat/${escenario}/reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) {
    throw new Error(`Error del servidor: ${res.status}`);
  }
  return res.json();
}

export async function consultarEstado(escenario) {
  const res = await fetch(`/admin/${escenario}/estado`);
  if (!res.ok) {
    throw new Error(`Error del servidor: ${res.status}`);
  }
  return res.json();
}

export async function obtenerResolucion(logId) {
  const res = await fetch(`/resolucion?log_id=${logId}`);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error(`Error del servidor: ${res.status}`);
  }
  return res.json();
}

export async function obtenerCatalogo(escenario) {
  const res = await fetch(`/resolucion/catalogo?escenario=${escenario}`);
  if (!res.ok) {
    throw new Error(`Error del servidor: ${res.status}`);
  }
  return res.json();
}
