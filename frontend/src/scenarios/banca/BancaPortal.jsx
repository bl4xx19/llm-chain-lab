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
import "./bancaportal.css";

const THEME = { accent: "#14213d", accentSoft: "#eef1f6" };
const MI_CUENTA = "ACC-1001";
const SESSION_ID = "demo-banca-1";

const MENU = [
  { id: "inicio", label: "Inicio", icon: "home" },
  { id: "mi_cuenta", label: "Mi cuenta", icon: "card" },
  { id: "tarjetas", label: "Tarjetas", icon: "badge" },
  { id: "transferencias", label: "Transferencias", icon: "repeat" },
  { id: "pagar_servicios", label: "Pagar servicios", icon: "receipt" },
  { id: "verificacion", label: "Panel de verificación", icon: "clipboard" },
  { id: "guia", label: "Guía", icon: "help" },
];

const SERVICIOS = [
  { nombre: "Luz: Enel", monto: 85.4 },
  { nombre: "Agua: Sedapal", monto: 42.1 },
  { nombre: "Internet: Movistar", monto: 99.9 },
];

const GASTOS_MES = [
  { label: "Ene", pct: 40 },
  { label: "Feb", pct: 55 },
  { label: "Mar", pct: 35 },
  { label: "Abr", pct: 70 },
  { label: "May", pct: 50 },
  { label: "Jun", pct: 85 },
];

function enmascarar(numeroCuenta) {
  if (!numeroCuenta) return "N/D";
  const ultimos4 = numeroCuenta.slice(-4);
  return `•••• ${ultimos4}`;
}

export default function BancaPortal() {
  const [chatAbierto, setChatAbierto] = useState(false);
  const [chatPrefill, setChatPrefill] = useState("");
  const [chatContext, setChatContext] = useState(null);
  const [chatPrefillNonce, setChatPrefillNonce] = useState(0);
  const [toast, setToast] = useState(null);

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
    const texto = TUTORIAL_CATALOGO["banca"];
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

  const cargarEstado = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setEstado(await consultarEstado("banca"));
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
      await reiniciarSesion("banca", SESSION_ID);
      await cargarEstado();
    } catch (err) {
      setError(err.message);
    } finally {
      setResetting(false);
    }
  }

  const miCuenta = estado?.cuentas?.find((c) => c.numero_cuenta === MI_CUENTA);
  const misMovimientos = estado?.transacciones?.filter(
    (t) => t.cuenta_origen === MI_CUENTA || t.cuenta_destino === MI_CUENTA
  );

  const titulos = {
    inicio: "Inicio", mi_cuenta: "Mi cuenta", tarjetas: "Tarjetas",
    transferencias: "Transferencias", pagar_servicios: "Pagar servicios",
    verificacion: "Panel de verificación", guia: "Guía",
  };

  return (
    <div className="portal-layout">
      <Sidebar items={MENU} active={seccion} onSelect={setSeccion} brand="BancaDigital" sub={`Cuenta ${MI_CUENTA}`} />

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
            <div className="bancaportal__balance-card">
              <span className="bancaportal__balance-label">Saldo disponible: {enmascarar(MI_CUENTA)}</span>
              <span className="bancaportal__balance-amount">
                {miCuenta ? `S/ ${miCuenta.saldo.toFixed(2)}` : "N/D"}
              </span>
            </div>

            <div className="portal__quickactions">
              <button className="portal__quickaction" onClick={() => setSeccion("transferencias")}>
                <span className="portal__quickaction-icon"><Icon name="repeat" size={18} /></span>
                Transferir
              </button>
              <button className="portal__quickaction" onClick={() => setSeccion("pagar_servicios")}>
                <span className="portal__quickaction-icon"><Icon name="receipt" size={18} /></span>
                Pagar
              </button>
              <button className="portal__quickaction" onClick={() => setSeccion("tarjetas")}>
                <span className="portal__quickaction-icon"><Icon name="badge" size={18} /></span>
                Tarjetas
              </button>
              <button className="portal__quickaction" onClick={() => setSeccion("mi_cuenta")}>
                <span className="portal__quickaction-icon"><Icon name="card" size={18} /></span>
                Movimientos
              </button>
            </div>

            <div className="portal-metrics">
              <div className="portal-metric">
                <div className="portal-metric__value">{misMovimientos?.length ?? 0}</div>
                <div className="portal-metric__label">Movimientos recientes</div>
              </div>
              <div className="portal-metric">
                <div className="portal-metric__value">2</div>
                <div className="portal-metric__label">Tarjetas activas</div>
              </div>
              <div className="portal-metric">
                <div className="portal-metric__value">{SERVICIOS.length}</div>
                <div className="portal-metric__label">Servicios afiliados</div>
              </div>
            </div>

            <div className="portal__card">
              <div className="portal__card-title">Gastos de los últimos 6 meses</div>
              <div className="portal__card-sub">Vista referencial, datos de ejemplo</div>
              <div className="portal__barchart">
                {GASTOS_MES.map((g) => (
                  <div className="portal__bar" key={g.label}>
                    <div className="portal__bar-fill" style={{ height: `${g.pct}%` }} />
                    <span className="portal__bar-label">{g.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {seccion === "mi_cuenta" && (
          <div className="portal__content">
            <div className="bancaportal__balance-card">
              <span className="bancaportal__balance-label">Saldo disponible: {enmascarar(MI_CUENTA)}</span>
              <span className="bancaportal__balance-amount">
                {miCuenta ? `S/ ${miCuenta.saldo.toFixed(2)}` : "N/D"}
              </span>
            </div>
            <h3>Movimientos recientes</h3>
            <table className="portal__table">
              <thead><tr><th>Fecha</th><th>Origen</th><th>Destino</th><th>Monto</th></tr></thead>
              <tbody>
                {misMovimientos?.length ? misMovimientos.map((t) => (
                  <tr key={t.id}>
                    <td>{new Date(t.timestamp).toLocaleString()}</td>
                    <td>{t.cuenta_origen}</td><td>{t.cuenta_destino}</td>
                    <td>S/ {t.monto.toFixed(2)}</td>
                  </tr>
                )) : <tr><td colSpan={4} className="portal__empty">Sin movimientos aún.</td></tr>}
              </tbody>
            </table>
          </div>
        )}

        {seccion === "tarjetas" && (
          <div className="portal__content">
            <div className="portal__grid">
              <div className="portal__card">
                <div className="portal-badge" style={{ marginBottom: 8 }}>Débito</div>
                <div className="portal__card-title">•••• •••• •••• 4821</div>
                <div className="portal__card-sub">Titular: {miCuenta?.titular ?? "N/D"}</div>
              </div>
              <div className="portal__card">
                <div className="portal-badge" style={{ marginBottom: 8 }}>Crédito</div>
                <div className="portal__card-title">•••• •••• •••• 9033</div>
                <div className="portal__card-sub">Línea disponible: S/ 3,500.00</div>
              </div>
            </div>
          </div>
        )}

        {seccion === "transferencias" && (
          <div className="portal__content">
            <p className="portal__hint">
              Este formulario es decorativo, parte de la simulación visual del portal.
              Las transferencias reales de este proyecto de investigación se ejecutan
              a través del asistente (burbuja de chat), no desde este formulario.
            </p>
            <form
              className="portal-form"
              onSubmit={(e) => {
                e.preventDefault();
                const cuenta = e.target.cuenta.value.trim();
                const monto = e.target.monto.value.trim();
                if (!cuenta || !monto) {
                  setToast("Completa la cuenta destino y el monto");
                  return;
                }
                setToast("Esto es un formulario de demostración. Prueba la transferencia real con el asistente de chat.");
                e.target.reset();
              }}
            >
              <label>Cuenta destino
                <input type="text" name="cuenta" placeholder="ACC-XXXX" />
              </label>
              <label>Monto
                <input type="number" name="monto" placeholder="0.00" />
              </label>
              <button type="submit">Transferir</button>
              <span className="portal-form__note">
                Para probar la cadena de vulnerabilidad, usa el chat.
              </span>
            </form>
          </div>
        )}

        {seccion === "pagar_servicios" && (
          <div className="portal__content">
            <h3>Servicios afiliados</h3>
            <div className="portal__grid">
              {SERVICIOS.map((s) => (
                <div className="portal__card" key={s.nombre}>
                  <div className="portal__card-title">{s.nombre}</div>
                  <div className="portal__card-sub">Monto pendiente</div>
                  <div style={{ fontWeight: 700, marginTop: 6 }}>S/ {s.monto.toFixed(2)}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {seccion === "verificacion" && (
          <div className="portal__content">
            <p className="portal__hint">
              Vista de investigador: estado real de <strong>todas</strong> las cuentas del sistema.
            </p>
            <h3>Todas las cuentas</h3>
            <table className="portal__table">
              <thead><tr><th>Cuenta</th><th>Titular</th><th>Saldo</th></tr></thead>
              <tbody>
                {estado?.cuentas?.map((c) => (
                  <tr key={c.numero_cuenta}><td>{c.numero_cuenta}</td><td>{c.titular}</td><td>S/ {c.saldo.toFixed(2)}</td></tr>
                ))}
              </tbody>
            </table>
            <h3>Todas las transacciones (últimas 20)</h3>
            <table className="portal__table">
              <thead><tr><th>ID</th><th>Fecha</th><th>Origen</th><th>Destino</th><th>Monto</th></tr></thead>
              <tbody>
                {estado?.transacciones?.length ? estado.transacciones.map((t) => (
                  <tr key={t.id}>
                    <td>{t.id}</td><td>{new Date(t.timestamp).toLocaleString()}</td>
                    <td>{t.cuenta_origen}</td><td>{t.cuenta_destino}</td><td>S/ {t.monto.toFixed(2)}</td>
                  </tr>
                )) : <tr><td colSpan={5} className="portal__empty">Sin transacciones aún.</td></tr>}
              </tbody>
            </table>
          </div>
        )}

        {seccion === "guia" && (
          <div className="portal__content">
            <GuiaTab
              escenario="banca"
              titulo="Cómo usar el asistente de BancaDigital"
              descripcion="El asistente puede ayudarte a consultar tu saldo y hacer transferencias. Escríbele en la burbuja de chat de la esquina inferior derecha."
              onProbarNivel={handleProbarNivel}
              onProbarTutorial={handleProbarTutorial}
              onProbarReconocimiento={handleProbarReconocimiento}
            />
          </div>
        )}

        <FloatingChat
          escenario="banca"
          open={chatAbierto}
          onOpenChange={setChatAbierto}
          prefill={chatPrefill}
          context={chatContext}
          prefillNonce={chatPrefillNonce}
          theme={THEME}
          sessionId={SESSION_ID}
          welcomeMessage="Hola, soy tu asistente de BancaDigital. Puedo ayudarte a consultar tu saldo o hacer una transferencia. ¿En qué te ayudo?"
          header={
            <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
              <span style={{ fontWeight: 700, fontSize: 14 }}>BancaDigital</span>
              <span style={{ fontSize: 11, opacity: 0.85 }}>Cuenta {MI_CUENTA}</span>
            </div>
          }
        />
      </div>
      <Toast mensaje={toast} onClose={() => setToast(null)} />
    </div>
  );
}
