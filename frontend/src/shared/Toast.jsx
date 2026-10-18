import { useEffect } from "react";
import "./toast.css";

export default function Toast({ mensaje, onClose }) {
  useEffect(() => {
    if (!mensaje) return;
    const timer = setTimeout(onClose, 2500);
    return () => clearTimeout(timer);
  }, [mensaje, onClose]);

  if (!mensaje) return null;

  return (
    <div className="toast" role="status">
      {mensaje}
    </div>
  );
}
