import { useState } from "react";
import Icon from "./Icon.jsx";
import ChainDiagram from "./ChainDiagram.jsx";
import "./resolutionpanel.css";

export default function ResolutionPanel({ resolucion, onClose }) {
  const [audiencia, setAudiencia] = useState("no_tecnico");

  if (!resolucion) return null;

  return (
    <div className="resolutionpanel__overlay" onClick={onClose}>
      <div className="resolutionpanel" onClick={(e) => e.stopPropagation()}>
        <div className="resolutionpanel__header">
          <div>
            <span className="resolutionpanel__cadena">Cadena {resolucion.cadena_id}</span>
            <h3>{resolucion.titulo}</h3>
          </div>
          <button className="resolutionpanel__close" onClick={onClose}>
            <Icon name="x" size={16} />
          </button>
        </div>

        <ChainDiagram eslabon1={resolucion.eslabon_1} eslabon2={resolucion.eslabon_2} />

        <div className="resolutionpanel__toggle">
          <button
            className={audiencia === "no_tecnico" ? "resolutionpanel__toggle-btn--active" : "resolutionpanel__toggle-btn"}
            onClick={() => setAudiencia("no_tecnico")}
          >
            Vista no técnica
          </button>
          <button
            className={audiencia === "tecnico" ? "resolutionpanel__toggle-btn--active" : "resolutionpanel__toggle-btn"}
            onClick={() => setAudiencia("tecnico")}
          >
            Vista desarrollador
          </button>
        </div>

        <div className="resolutionpanel__section">
          <h4><Icon name="search" size={14} /> Qué pasó</h4>
          <p>{resolucion.que_paso[audiencia]}</p>
        </div>

        <div className="resolutionpanel__section">
          <h4><Icon name="alertTriangle" size={14} /> Qué está en riesgo</h4>
          <p>{resolucion.que_esta_en_riesgo[audiencia]}</p>
        </div>

        <div className="resolutionpanel__section">
          <h4><Icon name="tool" size={14} /> Cómo se resuelve</h4>
          <p>{resolucion.como_se_resuelve[audiencia]}</p>
        </div>

        {(resolucion.cvss || resolucion.owasp_risk_rating) && (
          <div className="resolutionpanel__severity">
            {resolucion.cvss && (
              <>
                <span>CVSS v3.1: {resolucion.cvss.score}</span>
                <span className="resolutionpanel__vector">{resolucion.cvss.vector}</span>
              </>
            )}
            {resolucion.owasp_risk_rating && <span>OWASP Risk Rating: {resolucion.owasp_risk_rating}</span>}
          </div>
        )}
        {!resolucion.cvss && !resolucion.owasp_risk_rating && (
          <div className="resolutionpanel__severity resolutionpanel__severity--pending">
            Severidad (CVSS v3.1 / OWASP Risk Rating): pendiente de calculo formal.
          </div>
        )}
      </div>
    </div>
  );
}
