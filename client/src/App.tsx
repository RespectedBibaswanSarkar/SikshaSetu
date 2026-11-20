import { useEffect, useState } from "react";
import StudentApp from "./StudentApp";
import Offline from "./Offline";
import Diagnostic from "./Diagnostic";
import MockTest from "./MockTest";
import Misc from "./Misc";
import { useTheme } from "./theme";

type Page = "dashboard" | "library" | "player" | "diagnostic" | "test" | "analytics" | "planner" | "resources" | "settings" | "sync";
const PAGES: { id: Page; label: string }[] = [
  { id: "dashboard", label: "Dashboard" }, { id: "library", label: "Library" }, { id: "diagnostic", label: "Diagnostic" },
  { id: "test", label: "Mock Tests" }, { id: "analytics", label: "Analytics" }, { id: "planner", label: "Planner" },
  { id: "resources", label: "Resources" }, { id: "sync", label: "Sync" }, { id: "settings", label: "Settings" },
];

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [name, setName] = useState("You");
  const { online } = useTheme();
  useEffect(() => { document.title = "SikshaSetu — Learn • Analyse • Grow"; }, []);
  const Props = { page, setPage, setName };
  return (
    <div className="app">
      <header className="topbar">
        <div className="brand" onClick={() => setPage("dashboard")}>SikshaSetu</div>
        <input className="search" id="ask-search" placeholder="Ask SikshaSetu…" aria-label="Ask SikshaSetu" />
        <button className="bell">🔔</button>
        <div className="avatar" title={name}>{name.slice(0, 2).toUpperCase()}</div>
      </header>
      <div className="layout">
        <nav className="sidebar">
          {PAGES.map(p => <button key={p.id} className={page === p.id ? "active" : ""} onClick={() => setPage(p.id)}>{p.label}</button>)}
        </nav>
        <main className="main">
          {page === "dashboard" && <StudentApp {...Props} />}
          {page === "library" && <Offline {...Props} />}
          {page === "player" && <Offline {...Props} playerOnly />}
          {page === "diagnostic" && <Diagnostic {...Props} />}
          {page === "test" && <MockTest {...Props} />}
          {page === "analytics" && <Misc section="analytics" {...Props} />}
          {page === "planner" && <Misc section="planner" {...Props} />}
          {page === "resources" && <Misc section="resources" {...Props} />}
          {page === "sync" && <Misc section="sync" {...Props} />}
          {page === "settings" && <Misc section="settings" {...Props} />}
        </main>
      </div>
      <footer className="statusbar">{online ? "Online, sync available" : "Offline Mode — all features available ✓"}</footer>
    </div>
  );
}
