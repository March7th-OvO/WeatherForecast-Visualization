import { BarChart3, CloudSun, History, LayoutDashboard, Map } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "首页", icon: LayoutDashboard, end: true },
  { to: "/map", label: "天气地图", icon: Map },
  { to: "/analysis", label: "天气分析", icon: BarChart3 },
  { to: "/history", label: "15日天气", icon: History },
];

export function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            <CloudSun size={28} />
          </span>
          <h1>气象数据观测台</h1>
        </div>
        <nav className="nav-list" aria-label="主导航">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              <item.icon size={18} aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content" aria-label="页面内容">
        <Outlet />
      </main>
    </div>
  );
}
