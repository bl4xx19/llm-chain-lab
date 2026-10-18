import { BrowserRouter, Routes, Route } from "react-router-dom";
import Selector from "./selector/Selector.jsx";
import BancaPortal from "./scenarios/banca/BancaPortal.jsx";
import EcommercePortal from "./scenarios/ecommerce/EcommercePortal.jsx";
import SoportePortal from "./scenarios/soporte/SoportePortal.jsx";
import SaludPortal from "./scenarios/salud/SaludPortal.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Selector />} />
        <Route path="/banca" element={<BancaPortal />} />
        <Route path="/salud" element={<SaludPortal />} />
        <Route path="/ecommerce" element={<EcommercePortal />} />
        <Route path="/soporte" element={<SoportePortal />} />
      </Routes>
    </BrowserRouter>
  );
}
