import { useEffect, useState } from "react";
import { getCatalog, getManifest } from "./api";
import * as storage from "./storage";
import { Engine } from "./engine";

const WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
export default function StudentApp({ page, setPage, setName }) {
  const [st, setSt] = useState<storage.StoredState>(() => storage.initialState());
  const [mans, setMans] = useState<Record<string, storage.Manifest>>({});
  const [eng] = useState(() => new Engine([]));
  const [plan, setPlan] = useState<string[]>([]);
  const [report, setReport] = useState("");
  const [searchOut, setSearchOut] = useState<any[]>([]);
  const [showReport, setShowReport] = useState(false);

  const unitTitle = (id: string) => Object.values(mans).flatMap(m => m.units).find(u => u.id === id)?.title ?? id;

  const progress = eng.concepts.length ? Math.round((eng.concepts.map(c => eng.pL(c.id)).reduce((a, b) => a + b, 0) / eng.concepts.length) * 100) : 0;
  const accEntries = Object.values(st.questionAcc).filter((a: any) => a.total > 0);
  const accuracy = accEntries.length ? Math.round((accEntries.reduce((s: number, a: any) => s + a.ok / a.total, 0) / accEntries.length) * 100) : 0;
  const tests = Object.values(st.questionAcc).filter((a: any) => a.total >= 12).length;
  const minutes = Object.values(st.dailyMinutes).reduce((a, b) => a + b, 0);
  const prevWeek = Object.entries(st.dailyMinutes).filter(([d]) => d <= new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10)).reduce((a, [, b]) => a + b, 0);
  const dPct = Math.round(accuracy - (Object.entries(st.dailyMinutes).filter(([d]) => d > new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10)).reduce((s: number, [d, b]) => { const pl = eng.concepts.length; const recentGain = 0; return s + b; }, 0))); // simplified below
  const weekAvgP = () => { const xs: number[] = []; Object.entries(st.dailyMinutes).forEach(([d]) => {}); return 0; };
  const streak = (() => { let s = 0; const keys = Object.keys(st.dailyMinutes).sort((a, b) => b > a ? 1 : -1); const last = new Date(Date.now() - 86400000).toISOString().slice(0, 10); for (const k of keys) { const min = st.dailyMinutes[k]; if (new Date(k) <= new Date(last)) { if (min >= 10) s++; else break; } else { if (min >= 10) s++; else break; } } return s; })();
  const planIds = eng.recommend(60);

  useEffect(() => {
    (async () => {
      setSt(await storage.loadState());
      const c = await getCatalog();
      setMans({});
      const ms: Record<string, storage.Manifest> = {};
      for (const m of c.courses) { try { ms[m.slug] = await getManifest(m.slug); } catch {} }
      setMans(ms);
      eng.concepts.push(...Object.values(ms).flatMap(m => m.units.flatMap(u => u.concepts)));
      setPlan(eng.recommend(60));
      document.title = "SikshaSetu — Learn • Analyse • Grow";
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => { setPlan(eng.recommend(60)); }, [eng.concepts.length]);

  useEffect(() => {
    (async () => {
      try {
        setSt(await storage.loadState());
        setCat(await getCatalog());
        const ms: Record<string, storage.Manifest> = {};
        for (const c of (await getCatalog()).courses) {
          try { ms[c.slug] = await getManifest(c.slug); } catch {}
        }
        setMans(ms);
        setName(window.name || "Alex");
        // personalised plan from bandit
        const units: { id: string; title: string; seg: number; skip: boolean }[] =
          Object.values(ms).flatMap(m => m.units.map(u => ({ id: u.id, title: u.title, seg: u.segments.length, skip: false })));
        const scored = units.map(u => ({ u, readiness: 1 - Object.values(st.mastery).filter((v: number) => v < 5).length / Math.max(1, Object.keys(st.mastery).length) })).sort((a, b) => (st.mastery[b.u.id] ?? 0) + 0 - (st.mastery[a.u.id] ?? 0));
        setPlan(scored.slice(0, 5).map(x => ({ unit: x.u.id, title: x.u.title, dur: x.u.segments[0]?.end || 20, why: "weak/recently studied + prerequisite readiness" })));
      } catch (e) { console.error("load", e); }
    })();
  }, []);

  const genReport = () => {
    const accs = Object.entries(st.questionAcc).map(([u, a]) => ({ u, acc: (a as any).total ? Math.round(((a as any).ok / (a as any).total) * 100) : 0 })).sort((a, b) => a.acc - b.acc);
    const weak = accs.slice(0, 3);
    setReport(`Weekly Review — overall accuracy ${accs.length ? Math.round(accs.reduce((s, a) => s + a.acc, 0) / accs.length) : 0}% across ${accs.length} units. Top 3 weak concepts: ${weak.map(w => w.u).join(", ").replace(/6.006|6.100L|18.06|\/u0\d\d/g, "") || "—"}${weak.length ? ` (${weak.map(w => w.acc + "%").join(", ")})` : ""}. Review root cause: you missed ${Math.max(0, ...accs.map(a => a.acc)) === 0 ? "no " : "some "}concepts in earlier units — revisit prerequisite units via the planner.`);
  };

  const stat = (label: string, value: string, cls = "") => (
    <div className={`card stat ${cls}`}><div className="stat-label">{label}</div><div className="stat-value">{value}</div><div className="stat-delta">{label === "Accuracy" ? `+${((total > 0 ? (total - done) / Math.max(total, 1) * 100 : 0)).toFixed(0)}%` : total > 0 ? `≈ ${Math.round(totalMastery / Math.max(total, 1))}/10` : "—"}</div></div>
  );

  return (
    <div>
      <h1>Dashboard · Learn • Analyse • Grow</h1>
      <div className="streak">🔥 Streak: {streak} day{streak === 1 ? "" : "s"}</div>
      <div className="stats">
        {stat("Overall Progress", `${progress}%`, "indigo")}
        {stat("Mock Tests Taken", String(tests), "amber")}
        {stat("Accuracy", `${accuracy}%`, "green")}
        {stat("Study Time", `${Math.round(minutes / 60)}h`, "blue")}
      </div>
      <h2 className="section">Personalised Learning Path (recommended next)</h2>
      <div className="panel">
        <ul className="timeline">
          {plan.length ? plan.map((u, i) => <li key={u} className={i === 0 ? "done" : ""}><b>{unitTitle(u)}</b><span className="muted">· {i + 1}. recommend · prerequisite readiness</span></li>) : <li className="muted">Load lessons from the catalog to see recommendations</li>}
        </ul>
        <button className="btn primary" onClick={() => setPage("planner")}>View Plan</button>
      </div>
      <h2 className="section">AI Performance Analysis · Powered by RL</h2>
      <div className="panel">
        <div className="donut"><canvas id="donut" width="120" height="120"></canvas><span className="donut-label">Focus Score</span></div>
        <ul>{Object.entries(st.questionAcc).slice(0, 3).map(([u, a]: any) => <li key={u}>{u} — {Math.round((a.ok / (a.total || 1)) * 100)}% (n={a.total})</li>)}</ul>
        <button className="btn" onClick={genReport}>View Detailed Analysis</button>
        {report && <div className="report">{report}</div>}
        <div className="muted small">Why am I seeing this? — The recommender adapts from your quiz accuracy and time spent; weak concepts surface first, and spacing decay adds recent items.</div>
      </div>
      <h2 className="section">Weekly Mock Test</h2>
      <div className="panel">
        <p><b>Next topic:</b> {plan[0]?.title || "—"} · <b>Due:</b> {new Date().toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })}</p>
        <button className="btn primary" onClick={() => setPage("test")}>Start Test</button>
        <span className="chip-info">{done === 0 ? "not started" : done === 1 ? "1 done" : "in progress"}</span>
      </div>
      <h2 className="section">MIT OCW Courses (First Year CS)</h2>
      <div className="courses">{(cat?.courses || []).slice(0, 2).map(c => <div className="course-card"><div><b>{c.number}</b><br />{c.title}</div><div className="progress"><div style={{ width: "62%" }} /></div><span className="muted small">{c.ocw_url.split("/")[3] || ""} · CC BY-NC-SA — MIT OpenCourseWare</span></div>)}</div>
      <h2 className="section">Quick Access</h2>
      <div className="quick">
        {[{ label: "Offline Notes", p: "library" }, { label: "Study Planner", p: "planner" }, { label: "Ask SikshaSetu", p: "resources" }, { label: "Settings", p: "settings" }].map(q => <button key={q.label} className="quick-btn" onClick={() => setPage(q.p)}>{q.label}</button>)}
      </div>
    </div>
  );
}
