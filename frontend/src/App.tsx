import { NavLink, Route, Routes } from "react-router-dom";

import { Alerts } from "./pages/Alerts";
import { EquipmentCard } from "./pages/EquipmentCard";
import { EquipmentList } from "./pages/EquipmentList";

export function App() {
  return (
    <>
      <header className="header">
        <span className="logo">OFF-Tech</span>
        <nav>
          <NavLink to="/" end>
            Оборудование
          </NavLink>
          <NavLink to="/alerts">Алерты</NavLink>
        </nav>
      </header>

      <main className="main">
        <Routes>
          <Route path="/" element={<EquipmentList />} />
          <Route path="/equipment/:id" element={<EquipmentCard />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="*" element={<p>Страница не найдена</p>} />
        </Routes>
      </main>
    </>
  );
}
