import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";

type AppLayoutProps = {
  children: ReactNode;
};

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/pipeline", label: "Pipeline" },
  { to: "/contacts", label: "Contacts" },
  { to: "/map", label: "Map" },
  { to: "/tasks", label: "Tasks" }
];

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <strong>MEREA</strong>
          <span>Internal CRM</span>
        </div>
        <nav className="nav-list">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className="nav-link">
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
