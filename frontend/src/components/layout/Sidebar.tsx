import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/strategies", label: "Strategy Picker" },
  { to: "/backtest", label: "Backtest Results" },
  { to: "/alerts", label: "Alert Settings" },
];

export function Sidebar() {
  return (
    <nav className="app-sidebar" aria-label="Main navigation">
      <ul className="app-sidebar-list">
        {NAV_ITEMS.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                isActive ? "app-sidebar-link is-active" : "app-sidebar-link"
              }
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
