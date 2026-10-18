import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { enviarMensaje, reiniciarSesion, obtenerResolucion } from "../shared/api.js";
import ResolutionPanel from "./ResolutionPanel.jsx";
import Icon from "./Icon.jsx";
import "./chatwindow.css";

function calcularResumen(data) {
  if (!data.function_called) {
    return { tono: "neutral", texto: "El asistente no ejecutó ninguna función esta vez, solo respondió con texto. Consulta los indicadores y la evidencia completa antes de concluir sobre la cadena." };
  }
  const bloques = [];
  if (data.indicadores_4_1) bloques.push(data.indicadores_4_1);
  if (data.indicadores) {
    const ind = data.indicadores;
    if ("IND-2" in ind) bloques.push(ind);
    else Object.values(ind).forEach((v) => bloques.push(v));
  }
  const huboAbuso = bloques.some((b) => b && b["IND-2"] === true);
  if (huboAbuso) {
    return {
      tono: "exito",
      texto: `El asistente ejecutó "${data.function_called}" con datos fuera del alcance autorizado. Los indicadores de esta respuesta señalan un acceso o una acción fuera de lo permitido. Consulta el detalle para entender lo ocurrido.`,
    };
  }
  return {
    tono: "normal",
    texto: `El asistente ejecutó "${data.function_called}", sin que esta respuesta indique un abuso confirmado. Hace falta revisar el detalle antes de concluir que la interacción fue segura.`,
  };
}

export default function ChatWindow({
  escenario, theme, header, sessionId, welcomeMessage,
  variant = "fullscreen", onClose, prefill, prefillNonce, context,
}) {
  const [messages, setMessages] = useState(
    welcomeMessage ? [{ role: "assistant", content: welcomeMessage }] : []
  );
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastDebug, setLastDebug] = useState(null);
  const [showDebug, setShowDebug] = useState(false);
  const [showTecnico, setShowTecnico] = useState(false);
  const [intentos, setIntentos] = useState({ total: 0, conFuncion: 0 });
  const [resetting, setResetting] = useState(false);
  const [resolucion, setResolucion] = useState(null);
  const [buscandoResolucion, setBuscandoResolucion] = useState(false);
  const [status, setStatus] = useState("Lista para una interacción");
  const [nivel, setNivel] = useState("directa");
  const [cadenaTag, setCadenaTag] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (prefillNonce !== undefined && prefillNonce !== null) {
      setInput(prefill || "");
      if (context) { setNivel(context.tecnica); setCadenaTag(context.cadenaId); }
    }
  }, [prefillNonce, context, prefill]);

  async function handleSend() {
    const texto = input.trim();
    if (!texto || loading || resetting) return;

    setMessages((m) => [...m, { role: "user", content: texto }]);
    setInput("");
    setLoading(true);
    setStatus("Ejecutando interacción…");

    try {
      const data = await enviarMensaje(escenario, sessionId, texto, {
        tecnica: nivel,
        cadenaId: cadenaTag.trim() || null,
      });
      const resumen = calcularResumen(data);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: data.response },
        { role: "system", tono: resumen.tono, content: resumen.texto },
      ]);
      setLastDebug(data);
      setStatus("Interacción completada · revisar indicadores");
      setIntentos((prev) => ({
        total: prev.total + 1,
        conFuncion: prev.conFuncion + (data.function_called ? 1 : 0),
      }));
    } catch (err) {
      setStatus("Error · revisar conexión con el backend");
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error de conexión: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleReset() {
    if (resetting || loading) return;
    setResetting(true);
    try {
      await reiniciarSesion(escenario, sessionId);
      setMessages(welcomeMessage ? [{ role: "assistant", content: welcomeMessage }] : []);
      setLastDebug(null);
      setStatus("Sesión reiniciada");
      setInput("");
      setIntentos({ total: 0, conFuncion: 0 });
    } catch (err) {
      setStatus("Error · revisar conexión con el backend");
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `No se pudo reiniciar: ${err.message}` },
      ]);
    } finally {
      setResetting(false);
    }
  }

  async function handleVerResolucion() {
    if (!lastDebug?.log_id || buscandoResolucion) return;
    setBuscandoResolucion(true);
    try {
      const data = await obtenerResolucion(lastDebug.log_id);
      if (data) {
        setResolucion(data);
      } else {
        setMessages((m) => [
          ...m,
          { role: "assistant", content: "Esta interacción no corresponde a ninguna cadena reconocida todavía." },
        ]);
      }
    } catch (err) {
      setStatus("Error · revisar conexión con el backend");
      setMessages((m) => [...m, { role: "assistant", content: `Error al buscar resolución: ${err.message}` }]);
    } finally {
      setBuscandoResolucion(false);
    }
  }

  function downloadEvidence() {
    const url = URL.createObjectURL(new Blob([JSON.stringify({ source: "sesion_interactiva", escenario, session_id: sessionId, exported_at: new Date().toISOString(), response: lastDebug }, null, 2)], {type:"application/json"}));
    const link = document.createElement("a"); link.href = url; link.download = `interaccion-${escenario}-${Date.now()}.json`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div
      className={`chatwindow chatwindow--${variant}`}
      style={{ "--accent": theme.accent, "--accent-soft": theme.accentSoft }}
    >
      <div className="chatwindow__header">
        {variant === "fullscreen" && <a href="/" className="chatwindow__back"><Icon name="arrowLeft" size={14} /> Escenarios</a>}
        {header}
        <button
          className="chatwindow__reset"
          onClick={handleReset}
          disabled={resetting || loading}
          title="Borra la conversación y restaura los datos a su estado inicial"
        >
          {resetting ? "Reiniciando…" : "Reiniciar"}
        </button>
        <button
          className="chatwindow__debug-toggle"
          onClick={() => setShowDebug((s) => !s)}
          title="Ver qué hizo realmente el asistente en la última respuesta"
        >
          {showDebug ? "Volver al chat" : "¿Qué pasó?"}
        </button>
        {variant === "floating" && onClose && (
          <button className="chatwindow__close" onClick={onClose} title="Cerrar chat">
            <Icon name="x" size={16} />
          </button>
        )}
      </div>

      <div className="chatwindow__status" role="status">{status}</div>
      <details className="chatwindow__advanced"><summary>Opciones técnicas del mensaje</summary>
            <div className="chatwindow__debug-controls">
              <label>
                Técnica
                <select disabled={loading || resetting} value={nivel} onChange={(e) => setNivel(e.target.value)}>
                  <option value="directa">Directa</option>
                  <option value="autoridad">Autoridad</option>
                  <option value="jailbreak">Forzada</option>
                  <option value="escalada">Avanzado · Varios mensajes</option>
                </select>
              </label>
              <label>
                Cadena (registro opcional)
                <input
                  type="text"
                  placeholder="ej. 4.1"
                  disabled={loading || resetting}
                  value={cadenaTag}
                  onChange={(e) => setCadenaTag(e.target.value)}
                />
              </label>
            </div>

      </details>
      <div className="chatwindow__body">
        <div className="chatwindow__messages" ref={scrollRef} role="log" aria-label="Conversación con el asistente">
          {messages.map((m, i) =>
            m.role === "system" ? (
              <div key={i} className={`chatwindow__system chatwindow__system--${m.tono}`}>
                <span className={`chatwindow__status-dot chatwindow__status-dot--${m.tono}`} />
                {m.content}
              </div>
            ) : (
              <div key={i} className={`chatwindow__bubble chatwindow__bubble--${m.role}`}>
                {m.role === "assistant" ? (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({ children }) => (
                        <div className="chatwindow__table-wrap">
                          <table>{children}</table>
                        </div>
                      ),
                    }}
                  >
                    {m.content || ""}
                  </ReactMarkdown>
                ) : (
                  m.content
                )}
              </div>
            )
          )}
          {loading && <div className="chatwindow__bubble chatwindow__bubble--assistant" role="status">Esperando respuesta del asistente…</div>}
        </div>

        {showDebug && (
          <div className="chatwindow__debug">
            <h4>¿Qué hizo el asistente?</h4>
            <p className="lab-session-note">Aquí puedes revisar la última interacción de esta demostración.</p>
            <p className="chatwindow__debug-explainer">
              Cada vez que le escribes al asistente, puede responder solo con texto
              o puede ejecutar una acción real del sistema. Aquí ves cuál de las dos
              pasó, y si esa acción se salió de los límites que debería respetar.
            </p>

            <div className="chatwindow__debug-counter">
              Intentos en esta sesión: {intentos.total} · con acción real ejecutada: {intentos.conFuncion}
            </div>


            {lastDebug ? (
              <>
                {lastDebug.log_id && (
                  <button
                    className="chatwindow__resolution-btn"
                    onClick={handleVerResolucion}
                    disabled={buscandoResolucion}
                  >
                    {buscandoResolucion ? "Buscando…" : (
                      <>
                        <Icon name="clipboard" size={14} /> Ver explicación completa de esto
                      </>
                    )}
                  </button>
                )}

                <button
                  className="chatwindow__tecnico-toggle"
                  onClick={() => setShowTecnico((s) => !s)}
                >
                  {showTecnico ? "Ocultar detalle técnico" : "Ver detalle técnico (JSON)"}
                </button>

                {showTecnico && (
                  <>
                <button className="chatwindow__tecnico-toggle" onClick={downloadEvidence}>Descargar respuesta JSON · sesión interactiva</button>

                    <div>
                      <strong>Acción ejecutada:</strong> {lastDebug.function_called ?? "ninguna, solo respondió texto"}
                    </div>
                    <div>
                      <strong>Datos que usó para ejecutarla:</strong>
                      <pre>{JSON.stringify(lastDebug.function_args, null, 2)}</pre>
                    </div>
                    <div>
                      <strong>Lo que devolvió esa acción:</strong>
                      <pre>{JSON.stringify(lastDebug.function_result, null, 2)}</pre>
                    </div>
                    {lastDebug.indicadores_4_1 && (
                      <div>
                        <strong>Indicadores (cadena 4.1):</strong>
                        <pre>{JSON.stringify(lastDebug.indicadores_4_1, null, 2)}</pre>
                      </div>
                    )}
                    {lastDebug.indicadores && (
                      <div>
                        <strong>Indicadores:</strong>
                        <pre>{JSON.stringify(lastDebug.indicadores, null, 2)}</pre>
                      </div>
                    )}
                    <div className="chatwindow__debug-logid">log_id: {lastDebug.log_id}</div>
                  </>
                )}
              </>
            ) : (
              <p>Aún no hay datos. Envía un mensaje.</p>
            )}
          </div>
        )}
      </div>

      <div className="chatwindow__inputbar">
        <textarea
          aria-label="Mensaje para el asistente"
          disabled={loading || resetting}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe un mensaje…"
          rows={1}
        />
        <button onClick={handleSend} disabled={loading || resetting || !input.trim()}>
          Enviar
        </button>
      </div>

      {resolucion && (
        <ResolutionPanel resolucion={resolucion} onClose={() => setResolucion(null)} />
      )}
    </div>
  );
}
