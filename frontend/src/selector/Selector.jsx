import { Link } from "react-router-dom";
import Icon from "../shared/Icon.jsx";
import "./selector.css";
const scenarios = [
  {id:"salud", n:"01", name:"Salud", icon:"stethoscope", desc:"Historiales clínicos y privacidad de pacientes."},
  {id:"ecommerce", n:"02", name:"Comercio", icon:"cart", desc:"Productos, pedidos y datos de clientes."},
  {id:"soporte", n:"03", name:"Soporte", icon:"message", desc:"Tickets, consultas y acceso a información."},
  {id:"banca", n:"04", name:"Banca", icon:"card", desc:"Cuentas, saldos y operaciones financieras."},
];
function ScenarioIcon({ scenario }) {
  const paths = {
    salud: <><path d="M10 4h4v6h6v4h-6v6h-4v-6H4v-4h6Z" /></>,
    ecommerce: <><path d="M5 8h14l1 12H4L5 8Z"/><path d="M8 9V6a4 4 0 0 1 8 0v3"/></>,
    soporte: <><path d="M4 13v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="11" width="4" height="7" rx="2"/><rect x="17" y="11" width="4" height="7" rx="2"/><path d="M19 18v1a2 2 0 0 1-2 2h-4"/><path d="M11 21h2"/></>,
    banca: <><path d="m3 8 9-5 9 5H3Z"/><path d="M5 11v7m7-7v7m7-7v7M3 21h18"/></>,
  };
  return <span className="studio-scenario-icon" aria-hidden="true"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round">{paths[scenario]}</svg></span>;
}
export default function Selector(){return <div className="studio">
  <header className="studio-header"><Link to="/" className="studio-brand" aria-label="LLM Chain Lab, inicio"><span className="studio-symbol"><Icon name="link" size={20}/></span>LLM Chain Lab</Link><span className="studio-environment">Laboratorio interactivo <span aria-hidden="true">↗</span></span></header>
  <main className="studio-main"><section className="studio-intro"><p className="studio-eyebrow">LABORATORIO DE VULNERABILIDADES ENCADENADAS</p><h1>Una falla<br/>lleva a otra.</h1><p className="studio-description">Descubre cómo una vulnerabilidad del chatbot puede abrir paso a otra en la aplicación.</p></section>
  <section aria-labelledby="scenario-heading"><div className="studio-section-head"><h2 id="scenario-heading">Selecciona un escenario</h2><span>01 — 04</span></div><div className="studio-grid">{scenarios.map(s=><Link key={s.id} to={`/${s.id}`} className="studio-card"><div className="studio-card-top"><ScenarioIcon scenario={s.id}/><span>{s.n}</span></div><div className="studio-card-content"><h3>{s.name}</h3><p>{s.desc}</p></div><footer><span>4 retos</span><span className="studio-open" aria-hidden="true">↗</span></footer></Link>)}</div></section>
  <div className="studio-bottom"><Icon name="bookOpen" size={15}/><span>Empieza con la guía. Consulta el detalle técnico cuando lo necesites.</span></div></main>
  <footer className="studio-footer"><span>LLM Chain Lab</span><span>Entorno de demostración</span></footer>
</div>}
