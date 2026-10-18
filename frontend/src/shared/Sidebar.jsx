import Icon from "./Icon.jsx";
import "./sidebar.css";

export default function Sidebar({ items, active, onSelect, brand, sub }) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__brand-name">{brand}</span>
        {sub && <span className="sidebar__brand-sub">{sub}</span>}
      </div>
      <nav className="sidebar__nav" aria-label="Secciones del escenario">
        {items.map((item) => (
          <button
            key={item.id}
            className={`sidebar__item ${active === item.id ? "sidebar__item--active" : ""}`}
            aria-current={active === item.id ? "page" : undefined}
            onClick={() => onSelect(item.id)}
          >
            <Icon name={item.icon} size={16} className="sidebar__icon" />
            {item.label}
          </button>
        ))}
      </nav>
      <a href="/" className="sidebar__back">
        <Icon name="arrowLeft" size={14} />
        Volver a escenarios
      </a>
    </aside>
  );
}
