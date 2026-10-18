import { useState } from "react";
import ChatWindow from "./ChatWindow.jsx";
import Icon from "./Icon.jsx";
import "./floatingchat.css";

export default function FloatingChat({
  escenario, theme, header, sessionId, welcomeMessage,
  open, onOpenChange, prefill, prefillNonce, context,
}) {
  const [openInterno, setOpenInterno] = useState(false);
  const isOpen = open !== undefined ? open : openInterno;
  const setOpen = onOpenChange ?? setOpenInterno;

  return (
    <>
      {isOpen && <div className="floatingchat__scrim" onClick={() => setOpen(false)} />}

      <div className={`floatingchat__panel ${isOpen ? "floatingchat__panel--open" : ""}`} style={{ "--accent": theme.accent }} inert={isOpen ? undefined : ""} aria-hidden={!isOpen}>
        {(
          <ChatWindow
            escenario={escenario}
            theme={theme}
            header={header}
            sessionId={sessionId}
            welcomeMessage={welcomeMessage}
            variant="floating"
            onClose={() => setOpen(false)}
            prefill={prefill}
            context={context}
            prefillNonce={prefillNonce}
          />
        )}
      </div>

      <button
        className={`floatingchat__bubble ${isOpen ? "floatingchat__bubble--hidden" : ""}`}
        style={{ "--accent": theme.accent }}
        onClick={() => setOpen(true)}
        title="Abrir chat"
      >
        <Icon name="message" size={22} />
      </button>
    </>
  );
}
