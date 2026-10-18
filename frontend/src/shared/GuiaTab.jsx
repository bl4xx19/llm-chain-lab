import { useState, useEffect } from "react";
import { obtenerCatalogo } from "./api.js";
import { RETOS_CATALOGO, TECNICA_LABELS, TUTORIAL_CATALOGO } from "./retos.js";
import Icon from "./Icon.jsx";
import ChainDiagram from "./ChainDiagram.jsx";
import "./guiatab.css";


function severidadDesdeCVSS(score) {
  if (score == null) return null;
  if (score < 4.0) return { label: "Low", clase: "guiatab__badge--low" };
  if (score < 7.0) return { label: "Medium", clase: "guiatab__badge--medium" };
  if (score < 9.0) return { label: "High", clase: "guiatab__badge--high" };
  return { label: "Critical", clase: "guiatab__badge--critical" };
}

export default function GuiaTab({ escenario, titulo, descripcion, onProbarNivel, onProbarTutorial, onProbarReconocimiento }) {
  const [catalogo, setCatalogo] = useState(null);
  const [error, setError] = useState(null);
  const [abierta, setAbierta] = useState(null);
  const [audiencia, setAudiencia] = useState("no_tecnico");

  useEffect(() => {
    obtenerCatalogo(escenario)
      .then((data) => {
        const ordenado = [...data].sort((a, b) => (a.nivel ?? 0) - (b.nivel ?? 0));
        setCatalogo(ordenado);
        if (ordenado.length) setAbierta(ordenado[0].cadena_id);
      })
      .catch((err) => setError(err.message));
  }, [escenario]);

  return (
    <div className="guiatab">
      <h3>{titulo}</h3>
      <p className="guiatab__desc">{descripcion}</p>

      <div className="guiatab__conceptos">
        <h4>Antes de empezar: 3 conceptos clave</h4>
        <div className="guiatab__concepto">
          <strong>Vulnerabilidad web clásica</strong>
          <p>Una falla que existe en cualquier aplicación, tenga IA o no. Ejemplo: un
          sistema que deja ver datos de otro usuario porque nunca comprueba a quién
          pertenecen.</p>
        </div>
        <div className="guiatab__concepto">
          <strong>Vulnerabilidad de IA (asistente con LLM)</strong>
          <p>Una falla que solo existe porque hay un asistente de inteligencia
          artificial de por medio. Ejemplo: convencer al asistente con palabras de
          que ignore una regla que debería respetar.</p>
        </div>
        <div className="guiatab__concepto">
          <strong>Encadenamiento</strong>
          <p>Cuando la falla de IA es la que abre la puerta para explotar la falla
          clásica. Ninguna de las dos funciona sola: primero se convence al
          asistente (falla de IA), y eso permite llegar a la falla clásica de
          siempre (ver datos ajenos, mover dinero, alterar un registro). Cada
          cadena de abajo es un ejemplo real de este encadenamiento.</p>
        </div>
      </div>

      <div className="guiatab__tutorial">
        <div className="guiatab__tutorial-header">
          <span className="guiatab__badge guiatab__badge--tutorial">Tutorial</span>
          <span className="guiatab__tutorial-note">No es un ataque</span>
        </div>
        <p className="guiatab__tutorial-desc">
          Así se ve una interacción normal y segura con el asistente, antes de ver
          cómo se puede romper en las cadenas de abajo.
        </p>
        <button className="guiatab__nivel-btn" onClick={() => onProbarTutorial && onProbarTutorial()}>
          Probar interacción legítima
        </button>
      </div>

      <div className="guiatab__catalogo-header">
        <h4 style={{ margin: 0 }}>Cadenas de este escenario</h4>
        <div className="guiatab__toggle">
          <button
            className={audiencia === "no_tecnico" ? "guiatab__toggle-btn--active" : "guiatab__toggle-btn"}
            onClick={() => setAudiencia("no_tecnico")}
          >
            Explicación simple
          </button>
          <button
            className={audiencia === "tecnico" ? "guiatab__toggle-btn--active" : "guiatab__toggle-btn"}
            onClick={() => setAudiencia("tecnico")}
          >
            Explicación técnica
          </button>
        </div>
      </div>

      <p className="guiatab__catalogo-intro">
        Cada tarjeta representa una cadena. El nivel indica complejidad, no severidad.
        Consulta el CVSS por separado y elige una técnica: directa, autoridad o forzada.
      </p>

      {!catalogo && !error && <p className="guiatab__loading" role="status">Cargando catálogo de cadenas…</p>}
      {catalogo?.length === 0 && <p>No hay cadenas disponibles para este escenario.</p>}
      {error && <p className="guiatab__error">No se pudo cargar el catálogo: {error}</p>}

      {catalogo?.map((c) => {
        const reto = RETOS_CATALOGO[c.cadena_id];
        const sevReal = severidadDesdeCVSS(c.cvss?.score);
        return (
          <div className="guiatab__card" key={c.cadena_id}>
            <button
              className="guiatab__card-header"
              aria-expanded={abierta === c.cadena_id}
              onClick={() => setAbierta(abierta === c.cadena_id ? null : c.cadena_id)}
            >
              <span className="guiatab__badge guiatab__badge--nivel">
                Cadena {c.cadena_id} · Nivel {c.nivel}
              </span>
              {sevReal && (
                <span className={`guiatab__badge ${sevReal.clase}`} title={c.cvss?.vector}>
                  CVSS {c.cvss.score} · {sevReal.label}
                </span>
              )}
              <span className="guiatab__card-titulo">{c.titulo}</span>
              <span className="guiatab__card-toggle">{abierta === c.cadena_id ? "\u2212" : "+"}</span>
            </button>

            {abierta === c.cadena_id && (
              <div className="guiatab__card-body">
                <ChainDiagram eslabon1={c.eslabon_1} eslabon2={c.eslabon_2} />

                {reto && (
                  <>
                    <div className="guiatab__seccion">
                      <strong><Icon name="bookOpen" size={14} className="guiatab__seccion-icon" /> Contexto de esta cadena</strong>
                      <p>{reto.contexto}</p>
                    </div>

                    {reto.reconocimiento && (
                      <div className="guiatab__seccion">
                        <strong><Icon name="search" size={14} className="guiatab__seccion-icon" /> Paso 0: reconocimiento</strong>
                        <p className="guiatab__nivel-hint">
                          Antes de atacar, explora qué puede hacer el asistente. En un
                          ataque real, esto siempre va primero.
                        </p>
                        <button
                          className="guiatab__nivel-btn guiatab__nivel-btn--recon"
                          onClick={() => onProbarReconocimiento(c.cadena_id)}
                        >
                          Probar reconocimiento
                        </button>
                      </div>
                    )}

                    <div className="guiatab__seccion">
                      <strong><Icon name="play" size={14} className="guiatab__seccion-icon" /> Prueba esta cadena</strong>
                      {reto.multiturno ? (
                        <p className="guiatab__nivel-hint">
                          Esta cadena necesita 2 mensajes. Manda el Paso 1 (que ya es el
                          reconocimiento), espera la respuesta del asistente, y luego
                          manda el Paso 2 usando la misma técnica.
                        </p>
                      ) : (
                        <p className="guiatab__nivel-hint">
                          Elige una técnica de las 3. Se abre el chat con el mensaje
                          ya escrito, solo tienes que darle enviar.
                        </p>
                      )}
                      <div className="guiatab__niveles">
                        {[1, 2, 3].map((n) =>
                          reto.multiturno ? (
                            <div className="guiatab__nivel-multiturno" key={n}>
                              <span className="guiatab__nivel-multiturno-label">{TECNICA_LABELS[n]}</span>
                              <button className="guiatab__nivel-btn" onClick={() => onProbarNivel(c.cadena_id, n, 0)}>
                                Paso 1
                              </button>
                              <button className="guiatab__nivel-btn" onClick={() => onProbarNivel(c.cadena_id, n, 1)}>
                                Paso 2
                              </button>
                            </div>
                          ) : (
                            <button
                              key={n}
                              className="guiatab__nivel-btn"
                              onClick={() => onProbarNivel(c.cadena_id, n)}
                            >
                              {TECNICA_LABELS[n]}
                            </button>
                          )
                        )}
                      </div>
                    </div>
                  </>
                )}

                <div className="guiatab__seccion">
                  <strong><Icon name="search" size={14} className="guiatab__seccion-icon" /> Qué podría pasar</strong>
                  <p>{c.que_paso[audiencia]}</p>
                </div>
                <div className="guiatab__seccion">
                  <strong><Icon name="alertTriangle" size={14} className="guiatab__seccion-icon" /> Qué estaría en riesgo</strong>
                  <p>{c.que_esta_en_riesgo[audiencia]}</p>
                </div>
                <div className="guiatab__seccion">
                  <strong><Icon name="tool" size={14} className="guiatab__seccion-icon" /> Cómo se resuelve</strong>
                  <p>{c.como_se_resuelve[audiencia]}</p>
                </div>
              </div>
            )}
          </div>
        );
      })}

      <p className="guiatab__nota">
        Puedes usar el botón "Reiniciar" en cualquier momento para dejar los
        datos como al inicio.
      </p>
    </div>
  );
}
