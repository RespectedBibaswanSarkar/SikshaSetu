import { useEffect, useState } from "react";
import { getCatalog, getManifest } from "./api";
import * as storage from "./storage";
import { Engine } from "./engine";
import { 
  Flame, GraduationCap, CheckCircle2, Trophy, Clock, 
  Target, Sparkles, AlertTriangle, Calendar, BookOpen, 
  FileText, MessageSquare, Settings, ArrowUpRight, ChevronRight,
  Lightbulb
} from "lucide-react";

interface StudentAppProps {
  page: string;
  setPage: (page: any) => void;
  setName: (name: string) => void;
  isMobile?: boolean;
}

export default function StudentApp({ setPage }: StudentAppProps) {
  const [mans, setMans] = useState<Record<string, storage.Manifest>>({});
  const [eng] = useState(() => new Engine([]));
  const [courses, setCourses] = useState<any[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const cat = await getCatalog();
        if (cat && cat.courses) {
          setCourses(cat.courses);
          const ms: Record<string, storage.Manifest> = {};
          for (const c of cat.courses) {
            try {
              ms[c.slug] = await getManifest(c.slug);
            } catch {}
          }
          setMans(ms);
          eng.concepts.push(...Object.values(ms).flatMap(m => m.units.flatMap(u => u.concepts)));
        }
      } catch (e) {
        console.error(e);
      }
    })();
  }, [eng]);

  return (
    <div className="dashboard-content">
      {/* Mobile view phone container for mobile breakpoint */}
      <div className="mobile-only-view">
        <div className="mobile-greeting-row">
          <div>
            <h1 className="mobile-greeting-title">Good Morning, Bibaswan!</h1>
          </div>
          <div className="streak-badge-mobile">
            <Flame size={16} className="flame-icon" />
            <div className="streak-num-mobile">12</div>
            <div className="streak-sub-mobile">Day Streak</div>
          </div>
        </div>

        {/* Mobile Progress Card */}
        <div className="mobile-progress-card">
          <div className="mobile-progress-left">
            <div className="mobile-progress-label">Progress</div>
            <div className="mobile-progress-val">72%</div>
            <div className="mobile-progress-next">Next: Revise Calculus (30 min)</div>
          </div>
          <div className="mobile-progress-donut">
            <svg width="68" height="68" viewBox="0 0 36 36" className="donut-svg">
              <path
                className="donut-bg"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="donut-stroke"
                strokeDasharray="72, 100"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
          </div>
        </div>

        {/* AI Insight */}
        <div className="mobile-insight-box">
          <div className="insight-header">
            <Lightbulb size={18} className="insight-bulb" />
            <span className="insight-title">AI Insight</span>
          </div>
          <div className="insight-body">Focus more on Probability Basics</div>
        </div>

        <button className="btn-mobile-start" onClick={() => setPage("planner")}>
          Start Learning →
        </button>
      </div>

      {/* Desktop view */}
      <div className="desktop-dashboard-view">
        {/* Hero banner */}
        <div className="hero-banner">
          <div className="hero-text-wrap">
            <h1 className="hero-heading">Good Morning, Bibaswan!</h1>
            <p className="hero-subheading">
              Let's continue your learning journey with SikshaSetu ✨
            </p>
          </div>
          <div className="hero-right-wrap">
            <div className="hero-quote">
              "Small steps every day<br />lead to big results."
            </div>
            <div className="streak-badge">
              <Flame size={24} className="flame-icon" />
              <div className="streak-info">
                <div className="streak-count">12</div>
                <div className="streak-label">Day Streak</div>
              </div>
            </div>
          </div>
        </div>

        {/* Top 4 Stat Cards */}
        <div className="stat-cards-grid">
          {/* Card 1: Overall Progress */}
          <div className="metric-card">
            <div className="metric-icon-wrap purple-glow">
              <GraduationCap size={22} className="metric-icon purple-text" />
            </div>
            <div className="metric-details">
              <span className="metric-label">Overall Progress</span>
              <div className="metric-value-row">
                <span className="metric-value">72%</span>
              </div>
              <div className="progress-bar-track">
                <div className="progress-bar-fill" style={{ width: "72%" }}></div>
              </div>
            </div>
          </div>

          {/* Card 2: Mock Tests Taken */}
          <div className="metric-card">
            <div className="metric-icon-wrap teal-glow">
              <CheckCircle2 size={22} className="metric-icon teal-text" />
            </div>
            <div className="metric-details">
              <span className="metric-label">Mock Tests Taken</span>
              <div className="metric-value-row">
                <span className="metric-value">8</span>
                <span className="delta-pill green-pill">↑ +2</span>
              </div>
            </div>
          </div>

          {/* Card 3: Accuracy */}
          <div className="metric-card">
            <div className="metric-icon-wrap amber-glow">
              <Trophy size={22} className="metric-icon amber-text" />
            </div>
            <div className="metric-details">
              <span className="metric-label">Accuracy</span>
              <div className="metric-value-row">
                <span className="metric-value">87%</span>
                <span className="delta-pill amber-pill">↑ +5%</span>
              </div>
            </div>
          </div>

          {/* Card 4: Study Time */}
          <div className="metric-card">
            <div className="metric-icon-wrap blue-glow">
              <Clock size={22} className="metric-icon blue-text" />
            </div>
            <div className="metric-details">
              <span className="metric-label">Study Time</span>
              <div className="metric-value-row">
                <span className="metric-value">24.5 hrs</span>
                <span className="delta-pill green-pill">↑ +3.2h</span>
              </div>
            </div>
          </div>
        </div>

        {/* Middle Row (3 cards) */}
        <div className="middle-cards-grid">
          {/* Card 1: Personalised Learning Path */}
          <div className="panel-card learning-path-card">
            <div className="panel-card-header">
              <div className="panel-header-left">
                <div className="target-icon-wrap">
                  <Target size={18} className="target-icon" />
                </div>
                <h3 className="panel-title">Your Personalised Learning Path</h3>
              </div>
              <button className="panel-pill-btn" onClick={() => setPage("planner")}>
                View Plan →
              </button>
            </div>

            <div className="timeline-steps">
              <div className="timeline-step">
                <div className="step-badge-col">
                  <span className="step-pill pill-today">Today</span>
                  <div className="timeline-line"></div>
                </div>
                <div className="step-content">
                  <div className="step-title">Revise: Calculus - Limits & Continuity</div>
                  <div className="step-duration">(30 min)</div>
                </div>
              </div>

              <div className="timeline-step">
                <div className="step-badge-col">
                  <span className="step-pill pill-next">Next</span>
                  <div className="timeline-line"></div>
                </div>
                <div className="step-content">
                  <div className="step-title">Practice: Arrays & Pointers (C++)</div>
                  <div className="step-duration">(45 min)</div>
                </div>
              </div>

              <div className="timeline-step">
                <div className="step-badge-col">
                  <span className="step-pill pill-later">Later</span>
                </div>
                <div className="step-content">
                  <div className="step-title">Explore: MIT OCW - Computer Systems</div>
                  <div className="step-duration">(1 hr)</div>
                </div>
              </div>
            </div>
          </div>

          {/* Card 2: AI Performance Analysis */}
          <div className="panel-card ai-perf-card">
            <div className="panel-card-header">
              <div className="panel-header-left">
                <Sparkles size={18} className="sparkle-icon" />
                <h3 className="panel-title">AI Performance Analysis</h3>
              </div>
              <span className="rl-badge">✨ Powered by RL</span>
            </div>

            <div className="ai-perf-body">
              <div className="donut-gauge-container">
                <svg width="110" height="110" viewBox="0 0 36 36" className="donut-chart-svg">
                  <path
                    className="donut-bg-dark"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    className="donut-stroke-gradient"
                    strokeDasharray="78, 100"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <div className="donut-center-text">
                  <div className="donut-score">78%</div>
                  <div className="donut-score-label">Focus Score</div>
                </div>
              </div>

              <div className="weak-areas-list">
                <div className="weak-areas-title">Weak Areas Detected:</div>
                <div className="weak-item">
                  <AlertTriangle size={14} className="weak-icon" />
                  <span>C++ Pointers & Memory</span>
                </div>
                <div className="weak-item">
                  <AlertTriangle size={14} className="weak-icon" />
                  <span>Probability Basics</span>
                </div>
                <div className="weak-item">
                  <AlertTriangle size={14} className="weak-icon" />
                  <span>Discrete Mathematics</span>
                </div>
              </div>
            </div>

            <button className="btn-view-analysis" onClick={() => setPage("analytics")}>
              View Detailed Analysis →
            </button>
          </div>

          {/* Card 3: Weekly Mock Test */}
          <div className="panel-card mock-test-card">
            <div className="panel-card-header">
              <div className="panel-header-left">
                <Calendar size={18} className="calendar-icon" />
                <h3 className="panel-title">Weekly Mock Test</h3>
              </div>
            </div>

            <div className="mock-test-body">
              <div className="mock-test-info">
                <p className="mock-test-ready">Your next mock test is ready!</p>
                <div className="mock-meta-row">
                  <span className="mock-meta-label">Topic:</span>
                  <span className="mock-meta-val">Data Structures</span>
                </div>
                <div className="mock-meta-row">
                  <span className="mock-meta-label">Date:</span>
                  <span className="mock-meta-val">Nov 22, 2026</span>
                </div>
              </div>

              <div className="mock-test-art">
                <svg width="74" height="84" viewBox="0 0 64 74" fill="none">
                  <rect x="8" y="10" width="48" height="60" rx="8" fill="#1e2538" stroke="#374151" strokeWidth="2" />
                  <rect x="22" y="4" width="20" height="10" rx="3" fill="#6d4aff" />
                  <path d="M18 26h28M18 36h28M18 46h18" stroke="#60a5fa" strokeWidth="2.5" strokeLinecap="round" />
                  <circle cx="50" cy="56" r="10" fill="#6d4aff" />
                  <path d="M50 51v5l3 2" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </div>
            </div>

            <button className="btn-start-test" onClick={() => setPage("test")}>
              Start Test →
            </button>
          </div>
        </div>

        {/* Bottom Section: MIT OCW Courses + Quick Access */}
        <div className="bottom-cards-grid">
          {/* MIT OCW Courses */}
          <div className="panel-card mit-courses-panel">
            <div className="mit-header-row">
              <div className="mit-title-wrap">
                <div className="mit-logo-badge">MIT</div>
                <div>
                  <h3 className="mit-heading">MIT OCW Courses (First Year CS)</h3>
                  <p className="mit-subheading">Curated course content for you</p>
                </div>
              </div>
              <button className="panel-pill-btn" onClick={() => setPage("library")}>
                Explore All →
              </button>
            </div>

            <div className="mit-course-cards-row">
              <div className="mit-mini-card" onClick={() => setPage("library")}>
                <div className="course-code">6.0001</div>
                <div className="course-name">Introduction to Computer Science</div>
              </div>

              <div className="mit-mini-card" onClick={() => setPage("library")}>
                <div className="course-code">6.006</div>
                <div className="course-name">Intro to Algorithms</div>
              </div>

              <div className="mit-mini-card" onClick={() => setPage("library")}>
                <div className="course-code">6.033</div>
                <div className="course-name">Computer Systems</div>
              </div>

              <div className="mit-mini-card" onClick={() => setPage("library")}>
                <div className="course-code">6.042</div>
                <div className="course-name">Mathematics for Computer Science</div>
              </div>
            </div>
          </div>

          {/* Quick Access */}
          <div className="panel-card quick-access-panel">
            <h3 className="quick-access-title">Quick Access</h3>
            <div className="quick-access-grid">
              <button className="quick-action-tile" onClick={() => setPage("library")}>
                <div className="quick-tile-icon-wrap">
                  <FileText size={20} className="quick-tile-icon" />
                </div>
                <span className="quick-tile-label">Offline Notes</span>
              </button>

              <button className="quick-action-tile" onClick={() => setPage("planner")}>
                <div className="quick-tile-icon-wrap">
                  <Calendar size={20} className="quick-tile-icon" />
                </div>
                <span className="quick-tile-label">Study Planner</span>
              </button>

              <button className="quick-action-tile" onClick={() => setPage("resources")}>
                <div className="quick-tile-icon-wrap">
                  <MessageSquare size={20} className="quick-tile-icon" />
                </div>
                <span className="quick-tile-label">Ask SikshaSetu</span>
              </button>

              <button className="quick-action-tile" onClick={() => setPage("settings")}>
                <div className="quick-tile-icon-wrap">
                  <Settings size={20} className="quick-tile-icon" />
                </div>
                <span className="quick-tile-label">Settings</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
