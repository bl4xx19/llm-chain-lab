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

const THEME = { accent: "#7d2e46", accentSoft: "#f7ecef" };
const SESSION_ID = "demo-ecommerce-1";

const MENU = [
  { id: "inicio", label: "Inicio", icon: "home" },
  { id: "catalogo", label: "Catálogo", icon: "package" },
  { id: "detalle", label: "Detalle de producto", icon: "search" },
  { id: "carrito", label: "Mi carrito", icon: "cart" },
  { id: "pedidos", label: "Mis pedidos", icon: "receipt" },
  { id: "verificacion", label: "Panel de verificación", icon: "clipboard" },
  { id: "guia", label: "Guía", icon: "help" },
];

const RESENAS = {
  1: [{ autor: "Marcos R.", texto: "Excelente sonido, muy cómodos.", estrellas: 5 }],
  2: [{ autor: "Lucía T.", texto: "Hace un café espectacular.", estrellas: 4 }],
  3: [{ autor: "Diego P.", texto: "Muy livianas, buen agarre.", estrellas: 5 }],
};

const ICONO_CATEGORIA = {
  "Electrónica": "columns",
  "Hogar": "home",
  "Deportes": "star",
};

function Estrellas({ valor }) {
  return (
    <span className="portal__stars">
      {Array.from({ length: 5 }).map((_, i) => (
        <Icon key={i} name="star" size={12} className={i < valor ? "portal__star--lleno" : "portal__star--vacio"} />
      ))}
    </span>
  );
}

export default function EcommercePortal() {
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
    const texto = TUTORIAL_CATALOGO["ecommerce"];
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
  const [productoSeleccionado, setProductoSeleccionado] = useState(null);
  const [carrito, setCarrito] = useState([]);
  const [toast, setToast] = useState(null);
  const [categoriaFiltro, setCategoriaFiltro] = useState("todas");

  const cargarEstado = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setEstado(await consultarEstado("ecommerce"));
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
      await reiniciarSesion("ecommerce", SESSION_ID);
      await cargarEstado();
    } catch (err) {
      setError(err.message);
    } finally {
      setResetting(false);
    }
  }

  function verDetalle(producto) {
    setProductoSeleccionado(producto);
    setSeccion("detalle");
  }

  function agregarAlCarrito(producto) {
    setCarrito((c) => [...c, producto]);
    setToast(`${producto.nombre} se agregó al carrito`);
  }

  function eliminarDelCarrito(index) {
    setCarrito((c) => c.filter((_, i) => i !== index));
    setToast("Producto eliminado del carrito");
  }

  const titulos = {
    inicio: "Inicio", catalogo: "Catálogo", detalle: "Detalle de producto",
    carrito: "Mi carrito", pedidos: "Mis pedidos",
    verificacion: "Panel de verificación", guia: "Guía",
  };

  const totalCarrito = carrito.reduce((sum, p) => sum + p.precio, 0);

  return (
    <div className="portal-layout">
      <Sidebar items={MENU} active={seccion} onSelect={setSeccion} brand="TiendaExpress" sub="Asistente de compras" />

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
            <div className="portal__card" style={{ background: THEME.accent, color: "#fff", marginBottom: 20 }}>
              <div style={{ fontSize: 18, fontWeight: 700 }}>Ofertas de la semana</div>
              <div style={{ fontSize: 13, opacity: 0.9, marginTop: 4 }}>Revisa el catálogo para ver descuentos activos.</div>
            </div>
            <div className="portal-metrics">
              <div className="portal-metric">
                <div className="portal-metric__value">{estado?.productos?.length ?? 0}</div>
                <div className="portal-metric__label">Productos disponibles</div>
              </div>
              <div className="portal-metric">
                <div className="portal-metric__value">{carrito.length}</div>
                <div className="portal-metric__label">En tu carrito</div>
              </div>
              <div className="portal-metric">
                <div className="portal-metric__value">{estado?.pedidos?.length ?? 0}</div>
                <div className="portal-metric__label">Pedidos totales</div>
              </div>
            </div>
          </div>
        )}

        {seccion === "catalogo" && (
          <div className="portal__content">
            <div className="portal__filterpills">
              {["todas", ...new Set((estado?.productos ?? []).map((p) => p.categoria))].map((cat) => (
                <button
                  key={cat}
                  className={`portal__filterpill ${categoriaFiltro === cat ? "portal__filterpill--active" : ""}`}
                  onClick={() => setCategoriaFiltro(cat)}
                >
                  {cat === "todas" ? "Todas" : cat}
                </button>
              ))}
            </div>

            <div className="portal__grid">
              {estado?.productos
                ?.filter((p) => categoriaFiltro === "todas" || p.categoria === categoriaFiltro)
                .map((p) => {
                  const resenasProducto = RESENAS[p.id];
                  const promedio = resenasProducto
                    ? Math.round(resenasProducto.reduce((s, r) => s + r.estrellas, 0) / resenasProducto.length)
                    : null;
                  return (
                    <div className="portal__card" key={p.id}>
                      <div className="portal__product-media">
                        <Icon name={ICONO_CATEGORIA[p.categoria] || "package"} size={30} />
                      </div>
                      {p.descuento_pct > 0 && <span className="portal__tag">Oferta</span>}
                      <div className="portal__card-title">{p.nombre}</div>
                      <div className="portal__card-sub">{p.categoria} · ID {p.id}</div>
                      {promedio && (
                        <div style={{ marginTop: 4 }}>
                          <Estrellas valor={promedio} />
                        </div>
                      )}
                      <div style={{ marginTop: 8 }}>
                        {p.descuento_pct > 0 ? (
                          <>
                            <span style={{ textDecoration: "line-through", color: "#999", marginRight: 6 }}>
                              S/ {p.precio.toFixed(2)}
                            </span>
                            <span style={{ fontWeight: 700, color: THEME.accent }}>
                              S/ {(p.precio * (1 - p.descuento_pct / 100)).toFixed(2)}
                            </span>
                          </>
                        ) : (
                          <span style={{ fontWeight: 700 }}>S/ {p.precio.toFixed(2)}</span>
                        )}
                      </div>
                      <div className="portal__card-sub">Stock: {p.stock}</div>
                      <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
                        <button className="portal__refresh" onClick={() => verDetalle(p)}>Ver detalle</button>
                        <button
                          className="portal__reset-btn"
                          style={{ background: THEME.accent }}
                          onClick={() => agregarAlCarrito(p)}
                        >
                          Agregar
                        </button>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {seccion === "detalle" && (
          <div className="portal__content">
            {productoSeleccionado ? (
              <>
                <div className="portal__card" style={{ maxWidth: 480 }}>
                  <div className="portal__product-media" style={{ height: 180 }}>
                    <Icon name={ICONO_CATEGORIA[productoSeleccionado.categoria] || "package"} size={44} />
                  </div>
                  <div className="portal__card-title" style={{ fontSize: 18 }}>{productoSeleccionado.nombre}</div>
                  <div className="portal__card-sub">{productoSeleccionado.categoria}</div>
                  <p style={{ fontSize: 13, marginTop: 10 }}>
                    Producto sintético generado para pruebas. Descripción decorativa: este
                    artículo cuenta con garantía estándar y envío en 24-48 horas.
                  </p>
                  <div style={{ fontWeight: 700, fontSize: 20, marginTop: 10 }}>
                    S/ {productoSeleccionado.precio.toFixed(2)}
                  </div>
                  <button
                    className="portal__reset-btn"
                    style={{ background: THEME.accent, marginTop: 10 }}
                    onClick={() => agregarAlCarrito(productoSeleccionado)}
                  >
                    Agregar al carrito
                  </button>
                </div>
                <h3 style={{ marginTop: 24 }}>Reseñas</h3>
                {(RESENAS[productoSeleccionado.id] || []).map((r, i) => (
                  <div className="portal__card" key={i}>
                    <div className="portal__card-title">{"⭐".repeat(r.estrellas)}</div>
                    <div className="portal__card-sub">{r.autor}</div>
                    <p style={{ fontSize: 13, marginTop: 6 }}>{r.texto}</p>
                  </div>
                ))}
              </>
            ) : (
              <p className="portal__empty">Selecciona un producto desde el catálogo para ver su detalle.</p>
            )}
          </div>
        )}

        {seccion === "carrito" && (
          <div className="portal__content">
            {carrito.length ? (
              <>
                <table className="portal__table">
                  <thead><tr><th>Producto</th><th>Precio</th><th></th></tr></thead>
                  <tbody>
                    {carrito.map((p, i) => (
                      <tr key={i}>
                        <td>{p.nombre}</td>
                        <td>S/ {p.precio.toFixed(2)}</td>
                        <td>
                          <button
                            className="portal__icon-btn"
                            onClick={() => eliminarDelCarrito(i)}
                            title="Eliminar del carrito"
                          >
                            <Icon name="x" size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div style={{ fontWeight: 700 }}>Total: S/ {totalCarrito.toFixed(2)}</div>
                <p className="portal__hint" style={{ marginTop: 14 }}>
                  El carrito es decorativo. Para generar un pedido real (y probar la
                  cadena 2.2), usa el asistente de chat.
                </p>
              </>
            ) : (
              <p className="portal__empty">Tu carrito está vacío. Agrega productos desde el catálogo.</p>
            )}
          </div>
        )}

        {seccion === "pedidos" && (
          <div className="portal__content">
            <table className="portal__table">
              <thead><tr><th>ID</th><th>Producto</th><th>Cant.</th><th>Precio aplicado</th></tr></thead>
              <tbody>
                {estado?.pedidos?.length ? estado.pedidos.map((ped) => (
                  <tr key={ped.id}>
                    <td>{ped.id}</td><td>{ped.producto_id}</td><td>{ped.cantidad}</td>
                    <td>S/ {ped.precio_unitario_aplicado.toFixed(2)}</td>
                  </tr>
                )) : <tr><td colSpan={4} className="portal__empty">Aún no tienes pedidos.</td></tr>}
              </tbody>
            </table>
          </div>
        )}

        {seccion === "verificacion" && (
          <div className="portal__content">
            <p className="portal__hint">
              Vista de investigador: catálogo real y pedidos generados por cualquier
              sesión, útil para confirmar el efecto de una cadena explotada por el chat.
            </p>
            <h3>Catálogo (precio, descuento y stock reales)</h3>
            <table className="portal__table">
              <thead><tr><th>ID</th><th>Nombre</th><th>Precio</th><th>Descuento</th><th>Stock</th></tr></thead>
              <tbody>
                {estado?.productos?.map((p) => (
                  <tr key={p.id}>
                    <td>{p.id}</td><td>{p.nombre}</td><td>S/ {p.precio.toFixed(2)}</td>
                    <td>{p.descuento_pct}%</td><td>{p.stock}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <h3>Pedidos generados (últimos 20)</h3>
            <table className="portal__table">
              <thead><tr><th>ID</th><th>Producto</th><th>Cant.</th><th>Precio aplicado</th><th>Cliente</th></tr></thead>
              <tbody>
                {estado?.pedidos?.length ? estado.pedidos.map((ped) => (
                  <tr key={ped.id}>
                    <td>{ped.id}</td><td>{ped.producto_id}</td><td>{ped.cantidad}</td>
                    <td>S/ {ped.precio_unitario_aplicado.toFixed(2)}</td><td>{ped.cliente}</td>
                  </tr>
                )) : <tr><td colSpan={5} className="portal__empty">Sin pedidos aún.</td></tr>}
              </tbody>
            </table>
          </div>
        )}

        {seccion === "guia" && (
          <div className="portal__content">
            <GuiaTab
              escenario="ecommerce"
              titulo="Cómo usar el asistente de TiendaExpress"
              descripcion="El asistente puede ayudarte a buscar productos, aplicar descuentos y generar pedidos. Escríbele en la burbuja de chat de la esquina inferior derecha."
              onProbarNivel={handleProbarNivel}
              onProbarTutorial={handleProbarTutorial}
              onProbarReconocimiento={handleProbarReconocimiento}
            />
          </div>
        )}

        <FloatingChat
          escenario="ecommerce"
          open={chatAbierto}
          onOpenChange={setChatAbierto}
          prefill={chatPrefill}
          context={chatContext}
          prefillNonce={chatPrefillNonce}
          theme={THEME}
          sessionId={SESSION_ID}
          welcomeMessage="¡Hola! Soy el asistente de TiendaExpress. Puedo ayudarte a buscar productos, aplicar descuentos o generar tu pedido. ¿Qué necesitas?"
          header={
            <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
              <span style={{ fontWeight: 700, fontSize: 14 }}>TiendaExpress</span>
              <span style={{ fontSize: 11, opacity: 0.85 }}>Asistente de compras</span>
            </div>
          }
        />
      </div>
      <Toast mensaje={toast} onClose={() => setToast(null)} />
    </div>
  );
}
