import {
  Flame, GraduationCap, CheckCircle2, Trophy, Clock,
  Target, Sparkles, AlertTriangle, ArrowUpRight, ChevronRight,
  BookOpen, FileText, Bell
} from "lucide-react";
import { Dashboard, LearningPathItem, WeakArea, CourseProgress } from "../live";
import { AnyPage } from "../App";

interface DashboardPageProps {
  dashboard: Dashboard;
  navigate: (p: AnyPage) => void;
}

function fmt(v: number | null, suffix = ""): string {
  if (v === null || v === undefined) return "—";
  return v + suffix;
}

function DeltaBadge({ delta, unit = "" }: { delta: number | null; unit?: string }) {
  if (delta === null || delta === undefined) return null;
  const up = delta >= 0;
  return (
    <span className={`delta-badge ${up ? "delta-up" : "delta-down"}`} aria-label={`${up ? "+" : ""}${delta}${unit}`}>
      {up ? "▲" : "▼"} {Math.abs(delta)}{unit}
    </span>
  );
}

function DonutRing({ value, size = 80 }: { value: number | null; size?: number }) {
  const v = value ?? 0;
  const r = 15.9155;
  const circ = 2 * Math.PI * r;
  const dash = (v / 100) * circ;
  return (
    <svg width={size} height={size} viewBox="0 0 36 36" className="donut-svg" aria-hidden="true">
      <circle cx="18" cy="18" r={r} fill="none" stroke="var(--border-subtle)" strokeWidth="3.5" />
      <circle cx="18" cy="18" r={r} fill="none" stroke="var(--primary-purple)" strokeWidth="3.5"
        strokeDasharray={`${dash} ${circ - dash}`} strokeLinecap="round"
        transform="rotate(-90 18 18)" />
      <text x="18" y="22" textAnchor="middle" className="donut-label" fontSize="8">
        {value === null ? "—" : `${v}%`}
      </text>
    </svg>
  );
}

export default function DashboardPage({ dashboard, navigate }: DashboardPageProps) {
  const { stats, weak_areas, learning_path, next_mock_test, courses, notifications } = dashboard;
  const name = dashboard.name ?? "Student";
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good Morning" : hour < 17 ? "Good Afternoon" : "Good Evening";

  return (
    <div className="dashboard-content">
      {/* Mobile Layout */}
      <div className="mobile-only-view">
        <div className="mobile-greeting-row">
          <div>
            <h1 className="mobile-greeting-title">{greeting}, {name.split(" ")[0]}!</h1>
          </div>
          <div className="streak-badge-mobile" aria-label={`Streak: ${stats.streak} days`}>
            <Flame size={16} className="flame-icon" aria-hidden="true" />
            <div className="streak-num-mobile">{stats.streak}</div>
            <div className="streak-sub-mobile">Day Streak</div>
          </div>
        </div>

        <div className="mobile-progress-card">
          <div className="mobile-progress-left">
            <div className="mobile-progress-label">Progress</div>
            <div className="mobile-progress-val" data-testid="stat-progress">{stats.overall_progress}%</div>
            {learning_path[0] && (
              <div className="mobile-progress-next">Next: {learning_path[0].title}</div>
            )}
          </div>
          <div className="mobile-progress-donut">
            <DonutRing value={stats.focus_score} size={68} />
          </div>
        </div>

        {weak_areas.length > 0 && (
          <div className="mobile-insight-box">
            <div className="insight-header">
              <Sparkles size={18} className="insight-bulb" aria-hidden="true" />
              <span className="insight-title">AI Insight</span>
            </div>
            <div className="insight-body">Focus more on {weak_areas[0].name}</div>
          </div>
        )}

        <button className="btn-mobile-start" onClick={() => navigate({ name: "practice" })}>
          Start Learning →
        </button>
      </div>

      {/* Desktop Layout */}
      <div className="desktop-dashboard-view">
        {/* Hero Banner */}
        <div className="hero-banner">
          <div className="hero-text-wrap">
            <h1 className="hero-title">{greeting}, {name.split(" ")[0]}! 👋</h1>
            <p className="hero-subtitle">
              {stats.overall_progress === 0
                ? "Start with the diagnostic to personalize your learning path."
                : `You're ${stats.overall_progress}% through your courses. Keep going!`}
            </p>
          </div>
          {stats.streak_at_risk && (
            <div className="streak-risk-badge" role="alert" aria-live="polite">
              <Flame size={16} aria-hidden="true" /> Streak at risk!
            </div>
          )}
        </div>

        {/* Stats Row */}
        <div className="stats-grid" role="region" aria-label="Your statistics">
          <div className="stat-card" data-testid="stat-progress">
            <div className="stat-icon-wrap stat-icon-blue"><GraduationCap size={20} aria-hidden="true" /></div>
            <div className="stat-info">
              <div className="stat-label">Overall Progress</div>
              <div className="stat-value">{fmt(stats.overall_progress, "%")}</div>
            </div>
          </div>

          <div className="stat-card" data-testid="stat-tests">
            <div className="stat-icon-wrap stat-icon-green"><CheckCircle2 size={20} aria-hidden="true" /></div>
            <div className="stat-info">
              <div className="stat-label">Tests Taken</div>
              <div className="stat-value">
                {stats.tests_taken}
                <DeltaBadge delta={stats.tests_delta} />
              </div>
            </div>
          </div>

          <div className="stat-card" data-testid="stat-accuracy">
            <div className="stat-icon-wrap stat-icon-purple"><Trophy size={20} aria-hidden="true" /></div>
            <div className="stat-info">
              <div className="stat-label">Accuracy</div>
              <div className="stat-value">
                {fmt(stats.accuracy, "%")}
                <DeltaBadge delta={stats.accuracy_delta} unit="%" />
              </div>
            </div>
          </div>

          <div className="stat-card" data-testid="stat-study">
            <div className="stat-icon-wrap stat-icon-teal"><Clock size={20} aria-hidden="true" /></div>
            <div className="stat-info">
              <div className="stat-label">Study Hours</div>
              <div className="stat-value">
                {fmt(stats.study_hours, "h")}
                <DeltaBadge delta={stats.study_delta} unit="h" />
              </div>
            </div>
          </div>

          <div className="stat-card" data-testid="stat-streak">
            <div className="stat-icon-wrap stat-icon-orange"><Flame size={20} aria-hidden="true" /></div>
            <div className="stat-info">
              <div className="stat-label">Streak</div>
              <div className="stat-value">{stats.streak} days</div>
            </div>
          </div>

          <div className="stat-card" data-testid="stat-focus">
            <div className="stat-icon-wrap stat-icon-pink"><Target size={20} aria-hidden="true" /></div>
            <div className="stat-info">
              <div className="stat-label">Focus Score</div>
              <div className="stat-value"><DonutRing value={stats.focus_score} size={40} /></div>
            </div>
          </div>
        </div>

        <div className="dashboard-lower-grid">
          {/* Weak Areas */}
          <section className="dashboard-card" aria-labelledby="weak-areas-heading">
            <h2 id="weak-areas-heading" className="card-title">
              <AlertTriangle size={16} aria-hidden="true" /> Weak Areas
            </h2>
            <div data-testid="weak-areas">
              {weak_areas.length === 0 ? (
                <p className="empty-state-text">None yet — take the diagnostic</p>
              ) : (
                <ul className="weak-area-list" role="list">
                  {weak_areas.slice(0, 5).map((w: WeakArea) => (
                    <li key={w.concept_id} className="weak-area-item"
                      role="listitem">
                      <button className="weak-area-btn" onClick={() => navigate({ name: "concept", cid: w.concept_id })}
                        aria-label={`Practice ${w.name} (${Math.round(w.mastery * 100)}% mastery)`}>
                        <span className="weak-area-name">{w.name}</span>
                        <span className="weak-area-course">{w.course}</span>
                        <div className="mastery-bar" aria-hidden="true">
                          <div className="mastery-fill" style={{ width: `${Math.round(w.mastery * 100)}%` }} />
                        </div>
                        <span className="weak-area-pct">{Math.round(w.mastery * 100)}%</span>
                        <ArrowUpRight size={14} className="arrow-icon" aria-hidden="true" />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          {/* Learning Path */}
          <section className="dashboard-card" aria-labelledby="learning-path-heading">
            <h2 id="learning-path-heading" className="card-title">
              <Sparkles size={16} aria-hidden="true" /> Recommended Path
            </h2>
            <div data-testid="learning-path">
              {learning_path.length === 0 ? (
                <p className="empty-state-text">Complete more practice to unlock recommendations</p>
              ) : (
                <ol className="learning-path-list" role="list">
                  {learning_path.slice(0, 5).map((item: LearningPathItem, i: number) => (
                    <li key={i} className="learning-path-item" role="listitem">
                      <button
                        className="learning-path-btn"
                        onClick={() => {
                          if (item.action === "diagnostic") navigate({ name: "practice" });
                          else if (item.concept_id) navigate({ name: "concept", cid: item.concept_id });
                          else navigate({ name: "practice" });
                        }}
                        aria-label={`${item.label}: ${item.title}`}
                      >
                        <span className="path-num">{i + 1}</span>
                        <div className="path-text">
                          <span className="path-label">{item.label}</span>
                          <span className="path-title">{item.title}</span>
                        </div>
                        <ChevronRight size={14} className="arrow-icon" aria-hidden="true" />
                      </button>
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </section>

          {/* Courses */}
          <section className="dashboard-card" aria-labelledby="courses-heading">
            <div className="card-header-row">
              <h2 id="courses-heading" className="card-title">
                <BookOpen size={16} aria-hidden="true" /> My Courses
              </h2>
              <button className="card-link" onClick={() => navigate({ name: "courses" })}>
                Explore All <ArrowUpRight size={14} aria-hidden="true" />
              </button>
            </div>
            {courses.length === 0 ? (
              <p className="empty-state-text">No courses enrolled</p>
            ) : (
              <ul className="course-cards-list" role="list">
                {courses.map((c: CourseProgress) => (
                  <li key={c.slug} className="course-card" data-testid="course-card" role="listitem">
                    <button className="course-card-btn"
                      onClick={() => navigate({ name: "courses" })}
                      aria-label={`${c.title}: ${c.progress}% progress`}>
                      <div className="course-card-title">{c.title}</div>
                      <div className="course-card-meta">{c.slug}</div>
                      <div className="course-progress-bar" aria-hidden="true">
                        <div className="course-progress-fill" style={{ width: `${c.progress}%` }} />
                      </div>
                      <div className="course-card-stats">
                        <span>{c.progress}% complete</span>
                        <span>{c.mastered}/{c.total} concepts</span>
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* Notifications */}
          <section className="dashboard-card" aria-labelledby="notif-heading">
            <h2 id="notif-heading" className="card-title">
              <Bell size={16} aria-hidden="true" /> Notifications
            </h2>
            {notifications.length === 0 ? (
              <p className="empty-state-text">No notifications</p>
            ) : (
              <ul className="notif-list" role="list">
                {notifications.slice(0, 5).map((n, i) => (
                  <li key={i} className="notif-item" role="listitem">
                    <span className={`notif-dot notif-${n.kind}`} aria-hidden="true" />
                    <span>{n.message}</span>
                  </li>
                ))}
              </ul>
            )}
            {next_mock_test && (
              <div className="next-test-banner">
                <span>Next mock test: {next_mock_test}</span>
                <button className="btn-secondary" onClick={() => navigate({ name: "tests" })}>
                  Start Test →
                </button>
              </div>
            )}
          </section>

          {/* Quick tiles */}
          <section className="dashboard-card quick-tiles-card" aria-labelledby="tiles-heading">
            <h2 id="tiles-heading" className="card-title">Quick Actions</h2>
            <div className="quick-tiles">
              <button className="quick-tile" onClick={() => navigate({ name: "notes" })}
                aria-label="Open Notes">
                <FileText size={20} aria-hidden="true" /><span>Notes</span>
              </button>
              <button className="quick-tile" onClick={() => navigate({ name: "planner" })}
                aria-label="Open Study Planner">
                <Clock size={20} aria-hidden="true" /><span>Planner</span>
              </button>
              <button className="quick-tile" onClick={() => navigate({ name: "analytics" })}
                aria-label="Open AI Analytics">
                <Sparkles size={20} aria-hidden="true" /><span>Analytics</span>
              </button>
              <button className="quick-tile" onClick={() => navigate({ name: "settings" })}
                aria-label="Open Settings">
                <Target size={20} aria-hidden="true" /><span>Settings</span>
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
