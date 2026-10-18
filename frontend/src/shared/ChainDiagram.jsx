import "./chaindiagram.css";

export default function ChainDiagram({ eslabon1, eslabon2 }) {
  return (
    <div className="chaindiagram">
      <div className="chaindiagram__node">
        <span className="chaindiagram__node-label">Eslabon 1</span>
        <span className="chaindiagram__node-value">{eslabon1}</span>
      </div>
      <svg className="chaindiagram__link" width="28" height="16" viewBox="0 0 28 16" fill="none">
        <rect x="1" y="4" width="10" height="8" rx="4" stroke="currentColor" strokeWidth="1.6" />
        <rect x="17" y="4" width="10" height="8" rx="4" stroke="currentColor" strokeWidth="1.6" />
        <line x1="11" y1="8" x2="17" y2="8" stroke="currentColor" strokeWidth="1.6" />
      </svg>
      <div className="chaindiagram__node">
        <span className="chaindiagram__node-label">Eslabon 2</span>
        <span className="chaindiagram__node-value">{eslabon2}</span>
      </div>
    </div>
  );
}
