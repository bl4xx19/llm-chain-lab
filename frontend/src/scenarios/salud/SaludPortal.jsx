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

const THEME = { accent: "#0f5c4c", accentSoft: "#e7f2ef" };
const SESSION_ID = "demo-salud-1";
const MI_HISTORIA = "HC-1001";

const MENU = [
  { id: "inicio", label: "Inicio", icon: "home" },
  { id: "mi_historial", label: "Mi historial", icon: "book" },
  { id: "mis_citas", label: "Mis citas", icon: "calendar" },
  { id: "medicamentos", label: "Medicamentos", icon: "pill" },
  { id: "mi_medico", label: "Mi médico", icon: "stethoscope" },
  { id: "verificacion", label: "Panel de verificación", icon: "clipboard" },
  { id: "guia", label: "Guía", icon: "help" },
];

export default function SaludPortal() {
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
    const texto = TUTORIAL_CATALOGO["salud"];
    if (!texto) return;
    setChatPrefill(texto);
    setChatPrefillNonce((n) => n + 1);
    setChatAbierto(true);
  }

  const [seccion, setSeccion] = useState("inicio");
  const [toast, setToast] = useState(null);
  const [tomados, setTomados] = useState({});
  const [estado, setEstado] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [resetting, setResetting] = useState(false);

  const cargarEstado = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setEstado(await consultarEstado("salud"));
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
      await reiniciarSesion("salud", SESSION_ID);
      await cargarEstado();
    } catch (err) {
      setError(err.message);
    } finally {
      setResetting(false);
    }
  }

  const miHistorial = estado?.historiales?.find((h) => h.numero_historia === MI_HISTORIA);

  const titulos = {
    inicio: "Inicio", mi_historial: "Mi historial", mis_citas: "Mis citas",
    medicamentos: "Medicamentos", mi_medico: "Mi médico",
    verificacion: "Panel de verificación", guia: "Guía",
  };

  return (
    <div className="portal-layout">
      <Sidebar items={MENU} active={seccion} onSelect={setSeccion} brand="Clínica MediCare" sub={`Paciente ${MI_HISTORIA}`} />

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
            <div className="portal__card">
              <div className="portal-badge" style={{ marginBottom: 8 }}>Próxima cita</div>
              <div className="portal__card-title">Control general: 15 de agosto, 10:00 a.m.</div>
              <div className="portal__card-sub">Dra. Fernanda Castro · Medicina General</div>
            </div>

            <h3 style={{ marginTop: 20 }}>Últimos signos vitales</h3>
            <div className="portal__vitals">
              <div className="portal__vital">
                <div className="portal__vital-value">120/78</div>
                <div className="portal__vital-label">Presión arterial</div>
              </div>
              <div className="portal__vital">
                <div className="portal__vital-value">72</div>
                <div className="portal__vital-label">Pulso (lpm)</div>
              </div>
              <div className="portal__vital">
                <div className="portal__vital-value">68 kg</div>
                <div className="portal__vital-label">Peso</div>
              </div>
              <div className="portal__vital">
                <div className="portal__vital-value">36.5°C</div>
                <div className="portal__vital-label">Temperatura</div>
              </div>
            </div>

            <div className="portal-metrics">
              <div className="portal-metric">
                <div className="portal-metric__value">1</div>
                <div className="portal-metric__label">Cita agendada</div>
              </div>
              <div className="portal-metric">
                <div className="portal-metric__value">2</div>
                <div className="portal-metric__label">Medicamentos activos</div>
              </div>
            </div>
          </div>
        )}

        {seccion === "mi_historial" && (
          <div className="portal__content">
            <div className="portal__card">
              <div className="portal__card-title">Paciente {MI_HISTORIA}</div>
              <div className="portal__card-sub">Historial clínico</div>
              <p style={{ marginTop: 10 }}><strong>Diagnóstico:</strong> {miHistorial?.diagnostico ?? "N/D"}</p>
              <p><strong>Notas:</strong> {miHistorial?.notas ?? "N/D"}</p>
            </div>
          </div>
        )}

        {seccion === "mis_citas" && (
          <div className="portal__content">
            <div className="portal__card">
              <div className="portal__card-title">Control general</div>
              <div className="portal__card-sub">15 de agosto · 10:00 a.m. · Dra. Fernanda Castro</div>
            </div>
            <button
              className="portal__refresh"
              style={{ marginTop: 14 }}
              onClick={() => setToast("Sección decorativa: aquí se agendaría una nueva cita")}
            >
              <Icon name="plus" size={13} /> Agendar nueva cita
            </button>
          </div>
        )}

        {seccion === "medicamentos" && (
          <div className="portal__content">
            <div className="portal__grid">
              <div className="portal__card" style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                <div className="portal__quickaction-icon"><Icon name="pill" size={16} /></div>
                <div style={{ flex: 1 }}>
                  <div className="portal__card-title">Losartán 50mg</div>
                  <div className="portal__card-sub">1 vez al día, en ayunas · 7:00 a.m.</div>
                  <button
                    className="portal__refresh"
                    style={{ marginTop: 8 }}
                    onClick={() => {
                      setTomados((t) => ({ ...t, losartan: true }));
                      setToast("Losartán 50mg marcado como tomado");
                    }}
                    disabled={tomados.losartan}
                  >
                    <Icon name={tomados.losartan ? "checkCircle" : "plus"} size={13} />
                    {tomados.losartan ? "Tomado hoy" : "Marcar como tomado"}
                  </button>
                </div>
              </div>
              <div className="portal__card" style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                <div className="portal__quickaction-icon"><Icon name="pill" size={16} /></div>
                <div style={{ flex: 1 }}>
                  <div className="portal__card-title">Vitamina D3</div>
                  <div className="portal__card-sub">1 vez a la semana · Lunes, 9:00 a.m.</div>
                  <button
                    className="portal__refresh"
                    style={{ marginTop: 8 }}
                    onClick={() => {
                      setTomados((t) => ({ ...t, vitaminaD3: true }));
                      setToast("Vitamina D3 marcada como tomada");
                    }}
                    disabled={tomados.vitaminaD3}
                  >
                    <Icon name={tomados.vitaminaD3 ? "checkCircle" : "plus"} size={13} />
                    {tomados.vitaminaD3 ? "Tomado hoy" : "Marcar como tomado"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {seccion === "mi_medico" && (
          <div className="portal__content">
            <div className="portal__card" style={{ maxWidth: 380, display: "flex", gap: 14, alignItems: "flex-start" }}>
              <div className="portal__avatar">FC</div>
              <div>
                <div className="portal__card-title">Dra. Fernanda Castro</div>
                <div className="portal__card-sub">Medicina General</div>
                <p style={{ fontSize: 13, marginTop: 10 }}>
                  Médico asignado para control general y seguimiento de rutina.
                </p>
              </div>
            </div>
          </div>
        )}

        {seccion === "verificacion" && (
          <div className="portal__content">
            <p className="portal__hint">
              Vista de investigador: todos los historiales indexados en el sistema,
              no solo el tuyo. Útil para confirmar fugas de información (cadenas 1.2 y 1.3).
            </p>
            <table className="portal__table">
              <thead><tr><th>N° Historia</th><th>Diagnóstico</th><th>Notas</th></tr></thead>
              <tbody>
                {estado?.historiales?.map((h) => (
                  <tr key={h.numero_historia}>
                    <td>{h.numero_historia}</td>
                    <td>{h.diagnostico}</td>
                    <td style={{ maxWidth: 400 }}>{h.notas}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {seccion === "guia" && (
          <div className="portal__content">
            <GuiaTab
              escenario="salud"
              titulo="Cómo usar el asistente del Portal de Pacientes"
              descripcion="El asistente puede ayudarte a consultar tu historial médico. Escríbele en la burbuja de chat de la esquina inferior derecha."
              onProbarNivel={handleProbarNivel}
              onProbarTutorial={handleProbarTutorial}
              onProbarReconocimiento={handleProbarReconocimiento}
            />
          </div>
        )}

        <FloatingChat
          escenario="salud"
          open={chatAbierto}
          onOpenChange={setChatAbierto}
          prefill={chatPrefill}
          context={chatContext}
          prefillNonce={chatPrefillNonce}
          theme={THEME}
          sessionId={SESSION_ID}
          welcomeMessage="Hola, soy el asistente del Portal de Pacientes de Clínica MediCare. Puedo ayudarte a consultar tu historial médico. ¿En qué te ayudo?"
          header={
            <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
              <span style={{ fontWeight: 700, fontSize: 14 }}>Clínica MediCare</span>
              <span style={{ fontSize: 11, opacity: 0.85 }}>Paciente {MI_HISTORIA}</span>
            </div>
          }
        />
      </div>
      <Toast mensaje={toast} onClose={() => setToast(null)} />
    </div>
  );
}
