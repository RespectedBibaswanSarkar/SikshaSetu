import { useEffect, useState, useCallback } from "react";
import {
  BookOpen, LayoutDashboard, FileCheck2, Sparkles, Calendar,
  BookMarked, Settings, Bell, Search, ChevronDown,
  Home, BarChart3, MoreHorizontal, X
} from "lucide-react";
import { useStore, fetchDashboard, getSid } from "./store";
import DashboardPage from "./pages/DashboardPage";
import PracticePage from "./pages/PracticePage";
import CoursesPage from "./pages/CoursesPage";
import TestsPage from "./pages/TestsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import PlannerPage from "./pages/PlannerPage";
import NotesPage from "./pages/NotesPage";
import SettingsPage from "./pages/SettingsPage";
import ConceptPage from "./pages/ConceptPage";
import TestDetailPage from "./pages/TestDetailPage";
import OnboardingPage from "./pages/OnboardingPage";
import ErrorState from "./components/ErrorState";

export type NavPage =
  | "dashboard" | "courses" | "practice" | "tests" | "analytics"
  | "planner" | "notes" | "settings";

export type AnyPage =
  | { name: NavPage }
  | { name: "concept"; cid: string }
  | { name: "test-detail"; tid: string };

export default function App() {
  const store = useStore();
  const [page, setPage] = useState<AnyPage>({ name: "dashboard" });
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQ, setSearchQ] = useState("");

  useEffect(() => {
    document.title = "SikshaSetu — Learn · Analyse · Grow";
  }, []);

  const navigate = useCallback((p: AnyPage) => setPage(p), []);

  // Handle error state
  if (store.status === "error") {
    return (
      <div className="app-container">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh" }}>
          <ErrorState message={store.message} onRetry={fetchDashboard} />
        </div>
      </div>
    );
  }

  if (store.status === "onboarding") {
    return <OnboardingPage onComplete={fetchDashboard} />;
  }

  const dashboard = store.status === "ok" ? store.data : null;
  const sid = getSid() ?? "";
  const name = dashboard?.name ?? "Student";
  const initials = name.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase();

  const navPage = page.name === "concept" || page.name === "test-detail"
    ? "courses"
    : page.name as NavPage;

  const navItems: { key: NavPage; label: string; icon: React.ReactNode }[] = [
    { key: "dashboard",  label: "Dashboard",     icon: <LayoutDashboard size={18} /> },
    { key: "courses",    label: "My Courses",     icon: <BookOpen size={18} /> },
    { key: "practice",  label: "Practice",        icon: <BookMarked size={18} /> },
    { key: "tests",     label: "Mock Tests",      icon: <FileCheck2 size={18} /> },
    { key: "analytics", label: "AI Analytics",    icon: <Sparkles size={18} /> },
    { key: "planner",   label: "Study Planner",   icon: <Calendar size={18} /> },
    { key: "notes",     label: "Notes",           icon: <BookOpen size={18} /> },
    { key: "settings",  label: "Settings",        icon: <Settings size={18} /> },
  ];

  const mobileNavItems: { key: NavPage; label: string; icon: React.ReactNode; testid: string }[] = [
    { key: "dashboard", label: "Home",      icon: <Home size={20} />,     testid: "nav-dashboard" },
    { key: "practice",  label: "Practice",  icon: <BookMarked size={20}/>, testid: "nav-practice" },
    { key: "tests",     label: "Tests",     icon: <FileCheck2 size={20}/>, testid: "nav-tests" },
    { key: "analytics", label: "Analytics", icon: <BarChart3 size={20}/>, testid: "nav-analytics" },
    { key: "settings",  label: "More",      icon: <MoreHorizontal size={20}/>, testid: "nav-more" },
  ];

  function renderPage() {
    if (store.status === "loading") {
      return <div className="loading-spinner" aria-label="Loading…"><div className="spinner" /></div>;
    }
    if (!dashboard) return null;
    if (page.name === "concept") {
      return <ConceptPage cid={page.cid} sid={sid} navigate={navigate} />;
    }
    if (page.name === "test-detail") {
      return <TestDetailPage sid={sid} tid={page.tid} navigate={navigate} />;
    }
    switch (page.name) {
      case "dashboard":  return <DashboardPage dashboard={dashboard} navigate={navigate} />;
      case "courses":    return <CoursesPage sid={sid} navigate={navigate} />;
      case "practice":   return <PracticePage sid={sid} />;
      case "tests":      return <TestsPage sid={sid} navigate={navigate} />;
      case "analytics":  return <AnalyticsPage sid={sid} />;
      case "planner":    return <PlannerPage sid={sid} />;
      case "notes":      return <NotesPage sid={sid} />;
      case "settings":   return <SettingsPage sid={sid} dashboard={dashboard} navigate={navigate} />;
      default:           return <DashboardPage dashboard={dashboard} navigate={navigate} />;
    }
  }

  const notifCount = dashboard?.notifications?.length ?? 0;

  return (
    <div className="app-container">
      {/* Search overlay */}
      {searchOpen && (
        <div className="search-overlay" role="dialog" aria-label="Search">
          <div className="search-modal">
            <div className="search-modal-inner">
              <Search size={18} className="search-modal-icon" />
              <input
                className="search-modal-input"
                autoFocus
                placeholder="Search courses, topics…"
                value={searchQ}
                onChange={e => setSearchQ(e.target.value)}
                aria-label="Search query"
              />
              <button onClick={() => setSearchOpen(false)} aria-label="Close search" className="search-close-btn">
                <X size={18} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top Header */}
      <header className="app-topbar" role="banner">
        <div className="topbar-left-mobile">
          <div className="brand-logo-wrap" onClick={() => navigate({ name: "dashboard" })} role="button" tabIndex={0}
            onKeyDown={e => e.key === "Enter" && navigate({ name: "dashboard" })} aria-label="SikshaSetu home">
            <div className="brand-icon-box">
              <BookOpen size={22} className="brand-icon-svg" aria-hidden="true" />
            </div>
            <div className="brand-titles">
              <span className="brand-main">SikshaSetu</span>
              <span className="brand-sub">Learn · Analyse · Grow</span>
            </div>
          </div>
        </div>

        <div className="search-bar-container">
          <Search size={16} className="search-lens-icon" aria-hidden="true" />
          <input
            className="search-input-field"
            placeholder="Search courses, topics, or ask SikshaSetu…"
            aria-label="Search"
            onClick={() => setSearchOpen(true)}
            onFocus={() => setSearchOpen(true)}
            readOnly
          />
          <span className="search-shortcut-badge">Ctrl + K</span>
        </div>

        <div className="topbar-right-actions">
          <button className="icon-bell-btn" aria-label={`Notifications (${notifCount})`}
            onClick={() => navigate({ name: "dashboard" })}>
            <Bell size={18} aria-hidden="true" />
            {notifCount > 0 && <span className="notification-indicator-dot" aria-hidden="true" />}
          </button>
          <div className="user-profile-badge" role="button" tabIndex={0} aria-label={`User: ${name}`}
            onClick={() => navigate({ name: "settings" })}
            onKeyDown={e => e.key === "Enter" && navigate({ name: "settings" })}>
            <div className="user-avatar-circle" aria-hidden="true">{initials}</div>
            <span className="user-display-name">{name}</span>
            <ChevronDown size={14} className="dropdown-arrow" aria-hidden="true" />
          </div>
        </div>
      </header>

      <div className="app-main-layout">
        {/* Left Sidebar */}
        <aside className="app-sidebar" role="navigation" aria-label="Main navigation">
          <div className="sidebar-brand-box" onClick={() => navigate({ name: "dashboard" })}
            role="button" tabIndex={0} onKeyDown={e => e.key === "Enter" && navigate({ name: "dashboard" })}
            aria-label="SikshaSetu home">
            <div className="brand-icon-box">
              <BookOpen size={24} className="brand-icon-svg" aria-hidden="true" />
            </div>
            <div className="brand-titles">
              <span className="brand-main">SikshaSetu</span>
              <span className="brand-sub">Learn · Analyse · Grow</span>
            </div>
          </div>

          <nav className="sidebar-nav-links" aria-label="Sidebar navigation">
            {navItems.map(item => (
              <button
                key={item.key}
                className={`nav-btn ${navPage === item.key ? "active" : ""}`}
                onClick={() => navigate({ name: item.key })}
                data-testid={`nav-${item.key}`}
                aria-current={navPage === item.key ? "page" : undefined}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="main-content-area" id="main-content">
          {renderPage()}
        </main>
      </div>

      {/* Mobile Bottom Nav */}
      <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
        {mobileNavItems.map(item => (
          <button
            key={item.key}
            className={`mobile-tab-btn ${navPage === item.key ? "active" : ""}`}
            onClick={() => navigate({ name: item.key })}
            data-testid={item.testid}
            aria-label={item.label}
            aria-current={navPage === item.key ? "page" : undefined}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
