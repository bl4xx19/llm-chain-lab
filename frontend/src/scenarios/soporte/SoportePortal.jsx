import { useState, useEffect, useCallback } from "react";
import Sidebar from "../../shared/Sidebar.jsx";
import FloatingChat from "../../shared/FloatingChat.jsx";
import GuiaTab from "../../shared/GuiaTab.jsx";
import { RETOS_CATALOGO, TUTORIAL_CATALOGO } from "../../shared/retos.js";
import Icon from "../../shared/Icon.jsx";
import Toast from "../../shared/Toast.jsx";
import { consultarEstado, reiniciarSesion } from "../../shared/api.js";
import "../../shared/portal.css";
import "../../shared/sidebar.css";

const THEME = { accent: "#383d47", accentSoft: "#eef0f2" };
const SESSION_ID = "demo-soporte-1";

const MENU = [
  { id: "inicio", label: "Inicio", icon: "home" },
  { id: "tickets", label: "Tickets", icon: "columns" },
  { id: "nuevo_ticket", label: "Nuevo ticket", icon: "plus" },
  { id: "base_conocimiento", label: "Base de conocimiento", icon: "bookOpen" },
  { id: "verificacion", label: "Panel de verificación", icon: "clipboard" },
  { id: "guia", label: "Guía", icon: "help" },
];

const PRIORIDAD_POR_TICKET = { 1: "media", 2: "alta", 3: "baja", 4: "alta" };
const SLA_POR_TICKET = { 1: "Vence en 2h", 2: "Vence en 45min", 3: "Vence en 1d", 4: "Vence en 3h" };

const HILO_POR_TICKET = {
  1: [
    { autor: "Laura Gómez", rol: "cliente", texto: "Sigo sin poder acceder, ¿alguna novedad?" },
    { autor: "Agente Soporte", rol: "agente", texto: "Estamos revisando el error 403, te contactamos en breve." },
  ],
  2: [
    { autor: "Carlos Ruiz", rol: "cliente", texto: "La lentitud continúa desde esta mañana." },
    { autor: "Agente Soporte", rol: "agente", texto: "Iniciando diagnóstico de conectividad ahora mismo." },
  ],
  3: [
    { autor: "Marta Díaz", rol: "cliente", texto: "Adjunto captura de los dos cobros duplicados." },
  ],
  4: [
    { autor: "Sistema", rol: "cliente", texto: "Ticket generado automáticamente por solicitud de recuperación." },
  ],
};

const ARTICULOS = [
  { titulo: "Cómo restablecer tu contraseña", resumen: "Pasos para recuperar el acceso a tu cuenta." },
  { titulo: "Problemas comunes de conexión", resumen: "Guía de diagnóstico básico de red." },
  { titulo: "Política de reembolsos", resumen: "Condiciones y plazos para solicitar un reembolso." },
];

export default function SoportePortal() {
  const [chatAbierto, setChatAbierto] = useState(false);
  const [chatPrefill, setChatPrefill] = useState("");
  const [chatContext, setChatContext] = useState(null);
  const [chatPrefillNonce, setChatPrefillNonce] = useState(0);

  function handleProbarNivel(cadenaId, nivel, paso) {
    setChatContext({ cadenaId, tecnica: {1:"directa",2:"autoridad",3:"jailbreak"}[nivel] });
    const entry = RETOS_CATALOGO[cadenaId]?.niveles?.[nivel];
    if (!entry) return;
    const texto = Array.isArray(entry) ? entry[paso ?? 0] : entry;
    if (!texto) return;
    setChatPrefill(texto);
    setChatPrefillNonce((n) => n + 1);
    setChatAbierto(true);
  }

  function handleProbarReconocimiento(cadenaId) {
    setChatContext({ cadenaId, tecnica:"directa" });
    const texto = RETOS_CATALOGO[cadenaId]?.reconocimiento;
    if (!texto) return;
    setChatPrefill(texto);
    setChatPrefillNonce((n) => n + 1);
    setChatAbierto(true);
  }

  function handleProbarTutorial() {
    setChatContext({ cadenaId:"", tecnica:"directa" });
    const texto = TUTORIAL_CATALOGO["soporte"];
    if (!texto) return;
    setChatPrefill(texto);
    setChatPrefillNonce((n) => n + 1);
    setChatAbierto(true);
  }

  const [seccion, setSeccion] = useState("inicio");
  const [estado, setEstado] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [resetting, setResetting] = useState(false);
  const [ticketAbierto, setTicketAbierto] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [toast, setToast] = useState(null);

  const cargarEstado = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setEstado(await consultarEstado("soporte"));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    cargarEstado();
    const interval = setInterval(cargarEstado, 5000);
    return () => clearInterval(interval);
  }, [cargarEstado]);

  async function handleReset() {
    if (resetting) return;
    setResetting(true);
    try {
      await reiniciarSesion("soporte", SESSION_ID);
      await cargarEstado();
    } catch (err) {
      setError(err.message);
    } finally {
      setResetting(false);
    }
  }

  const titulos = {
    inicio: "Inicio", tickets: "Tickets", nuevo_ticket: "Nuevo ticket",
    base_conocimiento: "Base de conocimiento",
    verificacion: "Panel de verificación", guia: "Guía",
  };

  const abiertos = estado?.tickets?.filter((t) => t.estado === "abierto") ?? [];

  return (
    <div className="portal-layout">
      <Sidebar items={MENU} active={seccion} onSelect={setSeccion} brand="MegaCorp Soporte" sub="Panel de agente" />

      <div className="portal-main" style={{ "--accent": THEME.accent, "--accent-soft": THEME.accentSoft }}>
        <div className="portal-topbar">
          <span className="portal-topbar__title">{titulos[seccion]}</span>
          <div className="portal-topbar__actions">
            <button className="portal__refresh" onClick={cargarEstado} disabled={loading}>
              {loading ? "Actualizando…" : (<><Icon name="refresh" size={13} /> Actualizar</>)}
            </button>
            <button className="portal__reset-btn" style={{ background: THEME.accent }} onClick={handleReset} disabled={resetting}>
              {resetting ? "Reiniciando…" : "Reiniciar"}
            </button>
          </div>
        </div>

        {error && <div className="portal__error">Error cargando datos: {error}</div>}

        {seccion === "inicio" && (
          <div className="portal__content">
            <div className="portal-metrics">
              <div className="portal-metric">
                <div className="portal-metric__value">{abiertos.length}</div>
                <div className="portal-metric__label">Tickets abiertos</div>
              </div>
              <div className="portal-metric">
                <div className="portal-metric__value">4.2h</div>
                <div className="portal-metric__label">Tiempo promedio de respuesta</div>
              </div>
              <div className="portal-metric">
                <div className="portal-metric__value">{ARTICULOS.length}</div>
                <div className="portal-metric__label">Artículos en base de conocimiento</div>
              </div>
            </div>
          </div>
        )}

        {seccion === "tickets" && (
          <div className="portal__content" style={{ maxWidth: "100%" }}>
            <div className="portal__searchbar">
              <Icon name="search" size={15} />
              <input
                placeholder="Buscar por título o cliente…"
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
              />
            </div>

            {ticketAbierto ? (
              <div className="portal__card" style={{ maxWidth: 560 }}>
                <button className="portal__refresh" onClick={() => setTicketAbierto(null)} style={{ marginBottom: 14 }}>
                  <Icon name="arrowLeft" size={13} /> Volver al tablero
                </button>
                <span className={`portal__priority portal__priority--${PRIORIDAD_POR_TICKET[ticketAbierto.id] || "media"}`}>
                  Prioridad {PRIORIDAD_POR_TICKET[ticketAbierto.id] || "media"}
                </span>
                <div className="portal__card-title" style={{ marginTop: 8 }}>#{ticketAbierto.id} · {ticketAbierto.titulo}</div>
                <div className="portal__card-sub">{ticketAbierto.cliente} · {SLA_POR_TICKET[ticketAbierto.id] || "Sin SLA"}</div>
                <p style={{ fontSize: 13, marginTop: 10 }}>{ticketAbierto.descripcion}</p>
                <div className="portal__thread">
                  {(HILO_POR_TICKET[ticketAbierto.id] || []).map((m, i) => (
                    <div key={i} className={`portal__thread-msg ${m.rol === "agente" ? "portal__thread-msg--agente" : ""}`}>
                      <div className="portal__thread-meta">{m.autor}</div>
                      {m.texto}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="portal-kanban">
                {["abierto", "en_progreso", "cerrado"].map((col) => (
                  <div className="portal-kanban__col" key={col}>
                    <div className="portal-kanban__col-title">
                      {col === "abierto" ? "Abierto" : col === "en_progreso" ? "En progreso" : "Cerrado"}
                    </div>
                    {(estado?.tickets ?? [])
                      .filter((t) => (col === "abierto" ? t.estado === "abierto" : col === "cerrado" ? t.estado === "cerrado" : false))
                      .filter((t) => t.titulo.toLowerCase().includes(busqueda.toLowerCase()) || t.cliente.toLowerCase().includes(busqueda.toLowerCase()))
                      .map((t) => (
                        <button className="portal-kanban__card" key={t.id} onClick={() => setTicketAbierto(t)} style={{ textAlign: "left", width: "100%", border: "none", cursor: "pointer" }}>
                          <span className={`portal__priority portal__priority--${PRIORIDAD_POR_TICKET[t.id] || "media"}`}>
                            {PRIORIDAD_POR_TICKET[t.id] || "media"}
                          </span>
                          <div style={{ marginTop: 6 }}><strong>#{t.id}</strong> {t.titulo}</div>
                          <div style={{ fontSize: 11, color: "#888", marginTop: 4 }}>{t.cliente} · {SLA_POR_TICKET[t.id] || "Sin SLA"}</div>
                        </button>
                      ))}
                    {col === "en_progreso" && (
                      <p style={{ fontSize: 12, color: "#999" }}>Sin tickets en esta columna.</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {seccion === "nuevo_ticket" && (
          <div className="portal__content">
            <p className="portal__hint">
              Formulario decorativo. Los tickets usados para las cadenas de
              vulnerabilidad ya vienen precargados; este formulario no crea tickets
              reales en esta versión del proyecto.
            </p>
            <form
              className="portal-form"
              onSubmit={(e) => {
                e.preventDefault();
                const titulo = e.target.titulo.value.trim();
                const descripcion = e.target.descripcion.value.trim();
                if (!titulo || !descripcion) {
                  setToast("Completa el título y la descripción");
                  return;
                }
                setToast("Ticket registrado en esta demo. Los tickets usados para las cadenas ya están precargados.");
                e.target.reset();
              }}
            >
              <label>Título
                <input type="text" name="titulo" placeholder="Describe brevemente tu problema" />
              </label>
              <label>Descripción
                <textarea rows={4} name="descripcion" placeholder="Detalla el problema..." />
              </label>
              <button type="submit">Crear ticket</button>
            </form>
          </div>
        )}

        {seccion === "base_conocimiento" && (
          <div className="portal__content">
            <div className="portal__grid">
              {ARTICULOS.map((a, i) => (
                <div className="portal__card" key={i}>
                  <div className="portal__card-title">{a.titulo}</div>
                  <p style={{ fontSize: 13, marginTop: 6 }}>{a.resumen}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {seccion === "verificacion" && (
          <div className="portal__content">
            <p className="portal__hint">
              Vista de investigador: incluye la configuración interna del sistema,
              para confirmar si una cadena logró exponer algún valor sensible.
            </p>
            <h3>Tickets</h3>
            <table className="portal__table">
              <thead><tr><th>ID</th><th>Cliente</th><th>Título</th><th>Estado</th></tr></thead>
              <tbody>
                {estado?.tickets?.map((t) => (
                  <tr key={t.id}><td>{t.id}</td><td>{t.cliente}</td><td>{t.titulo}</td><td>{t.estado}</td></tr>
                ))}
              </tbody>
            </table>
            <h3>Configuración interna</h3>
            <table className="portal__table">
              <thead><tr><th>Clave</th><th>Valor</th></tr></thead>
              <tbody>
                {estado?.configuracion?.map((c) => (
                  <tr key={c.clave}>
                    <td>{c.clave}</td>
                    <td className={/password|secret|api_key/.test(c.clave) ? "portal__sensitive" : ""}>
                      {c.valor}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {seccion === "guia" && (
          <div className="portal__content">
            <GuiaTab
              escenario="soporte"
              titulo="Cómo usar SoporteBot"
              descripcion="El asistente puede ayudarte a revisar tickets, verificar conectividad y consultar configuración del sistema. Escríbele en la burbuja de chat de la esquina inferior derecha."
              onProbarNivel={handleProbarNivel}
              onProbarTutorial={handleProbarTutorial}
              onProbarReconocimiento={handleProbarReconocimiento}
            />
          </div>
        )}

        <FloatingChat
          escenario="soporte"
          open={chatAbierto}
          onOpenChange={setChatAbierto}
          prefill={chatPrefill}
          context={chatContext}
          prefillNonce={chatPrefillNonce}
          theme={THEME}
          sessionId={SESSION_ID}
          welcomeMessage="Hola, soy SoporteBot. Puedo leer tickets, verificar conectividad, revisar configuración del sistema y buscar tickets relacionados. ¿En qué te ayudo?"
          header={
            <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
              <span style={{ fontWeight: 700, fontSize: 14 }}>MegaCorp Soporte</span>
              <span style={{ fontSize: 11, opacity: 0.85 }}>Panel de agente</span>
            </div>
          }
        />
      </div>
      <Toast mensaje={toast} onClose={() => setToast(null)} />
    </div>
  );
}
