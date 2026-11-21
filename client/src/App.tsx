import { useEffect, useState } from "react";
import StudentApp from "./StudentApp";
import Offline from "./Offline";
import Diagnostic from "./Diagnostic";
import MockTest from "./MockTest";
import Misc from "./Misc";
import { useTheme } from "./theme";
import {
  BookOpen, LayoutDashboard, FileCheck2, Sparkles, Calendar,
  FolderGit2, BookMarked, Settings, Bell, Search, ChevronDown,
  Home, BarChart3, MoreHorizontal
} from "lucide-react";

type Page = "dashboard" | "library" | "player" | "diagnostic" | "test" | "analytics" | "planner" | "resources" | "settings" | "sync";

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [name, setName] = useState("Bibaswan");
  const { online } = useTheme();

  useEffect(() => {
    document.title = "SikshaSetu — Learn • Analyse • Grow";
  }, []);

  const Props = { page, setPage, setName };

  return (
    <div className="app-container">
      {/* Top Header */}
      <header className="app-topbar">
        <div className="topbar-left-mobile">
          <div className="brand-logo-wrap" onClick={() => setPage("dashboard")}>
            <div className="brand-icon-box">
              <BookOpen size={22} className="brand-icon-svg" />
            </div>
            <div className="brand-titles">
              <span className="brand-main">SikshaSetu</span>
              <span className="brand-sub">Learn · Analyse · Grow</span>
            </div>
          </div>
        </div>

        <div className="search-bar-container">
          <Search size={16} className="search-lens-icon" />
          <input
            className="search-input-field"
            placeholder="Search courses, topics, or ask SikshaSetu..."
            aria-label="Search"
          />
          <span className="search-shortcut-badge">Ctrl + K</span>
        </div>

        <div className="topbar-right-actions">
          <button className="icon-bell-btn" aria-label="Notifications">
            <Bell size={18} />
            <span className="notification-indicator-dot"></span>
          </button>

          <div className="user-profile-badge">
            <div className="user-avatar-circle">BS</div>
            <span className="user-display-name">Bibaswan</span>
            <ChevronDown size={14} className="dropdown-arrow" />
          </div>
        </div>
      </header>

      <div className="app-main-layout">
        {/* Left Sidebar */}
        <aside className="app-sidebar">
          {/* Logo on desktop sidebar */}
          <div className="sidebar-brand-box" onClick={() => setPage("dashboard")}>
            <div className="brand-icon-box">
              <BookOpen size={24} className="brand-icon-svg" />
            </div>
            <div className="brand-titles">
              <span className="brand-main">SikshaSetu</span>
              <span className="brand-sub">Learn · Analyse · Grow</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="sidebar-nav-links">
            <button
              className={`nav-btn ${page === "dashboard" ? "active" : ""}`}
              onClick={() => setPage("dashboard")}
            >
              <LayoutDashboard size={18} />
              <span>Dashboard</span>
            </button>

            <button
              className={`nav-btn ${page === "library" ? "active" : ""}`}
              onClick={() => setPage("library")}
            >
              <BookOpen size={18} />
              <span>My Courses</span>
            </button>

            <button
              className={`nav-btn ${page === "test" ? "active" : ""}`}
              onClick={() => setPage("test")}
            >
              <FileCheck2 size={18} />
              <span>Mock Tests</span>
            </button>

            <button
              className={`nav-btn ${page === "analytics" ? "active" : ""}`}
              onClick={() => setPage("analytics")}
            >
              <Sparkles size={18} />
              <span>AI Analytics</span>
            </button>

            <button
              className={`nav-btn ${page === "planner" ? "active" : ""}`}
              onClick={() => setPage("planner")}
            >
              <Calendar size={18} />
              <span>Study Planner</span>
            </button>

            <button
              className={`nav-btn ${page === "resources" ? "active" : ""}`}
              onClick={() => setPage("resources")}
            >
              <FolderGit2 size={18} />
              <span>Resources</span>
            </button>

            <button
              className={`nav-btn ${page === "player" ? "active" : ""}`}
              onClick={() => setPage("player")}
            >
              <BookMarked size={18} />
              <span>Offline Library</span>
            </button>

            <button
              className={`nav-btn ${page === "settings" ? "active" : ""}`}
              onClick={() => setPage("settings")}
            >
              <Settings size={18} />
              <span>Settings</span>
            </button>
          </nav>

          {/* Bottom Offline Badge */}
          <div className="sidebar-bottom-offline">
            <div className="offline-pulse-dot"></div>
            <div className="offline-status-text">
              <div className="offline-status-heading">Offline Mode</div>
              <div className="offline-status-desc">All features available</div>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="app-main-viewport">
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

      {/* Mobile Bottom Tab Bar */}
      <nav className="mobile-bottom-tabs">
        <button
          className={`mobile-tab-btn ${page === "dashboard" ? "active" : ""}`}
          onClick={() => setPage("dashboard")}
        >
          <Home size={20} />
          <span>Home</span>
        </button>

        <button
          className={`mobile-tab-btn ${page === "test" ? "active" : ""}`}
          onClick={() => setPage("test")}
        >
          <FileCheck2 size={20} />
          <span>Tests</span>
        </button>

        <button
          className={`mobile-tab-btn ${page === "analytics" ? "active" : ""}`}
          onClick={() => setPage("analytics")}
        >
          <BarChart3 size={20} />
          <span>Analytics</span>
        </button>

        <button
          className={`mobile-tab-btn ${page === "settings" || page === "resources" ? "active" : ""}`}
          onClick={() => setPage("settings")}
        >
          <MoreHorizontal size={20} />
          <span>More</span>
        </button>
      </nav>
    </div>
  );
}
