import { Outlet } from "react-router-dom";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import "./AppLayout.css";

export function AppLayout() {
  return (
    <div className="app-layout">
      <Header />
      <div className="app-layout-body">
        <Sidebar />
        <main className="app-layout-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
