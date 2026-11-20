import { useEffect, useState } from "react";
import { searchOffline, getQuestions, getManifest } from "./api";
import * as storage from "./storage";
import { Bandit, COLD_START } from "./bandit";

export default function Misc({ section, page, setPage, setName }) {
  const [st, setSt] = useState<storage.StoredState>(() => storage.initialState());
  const [bandit] = useState(() => new Bandit(COLD_START));
  const [banditState, setBanditState] = useState<any>(COLD_START);
  const [out, setOut] = useState<any[]>([]);
  const [files, setFiles] = useState<string[]>([]);
  const [ans, setAns] = useState<number | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => { (async () => { setSt(await storage.loadState()); })() }, []);

  const name = "You";
  const ask = async (q: string) => { setOut([]); if (!q.trim()) return; setMsg("Searching offline (courses, topics, concepts, transcripts)…"); const r = await searchOffline(q); setOut(r.matches); setMsg(r.matches.length ? `${r.matches.length} matches — segments, concepts and questions are searchable offline` : "No offline matches yet — download units first"); };
  const openSeg = (m: string, id: string) => { const man =mans?.find(x => x.id === m); setMsg(`Segment ${id} — timestamp ${man?.segments?.find(s => s.id === id)?.start ?? 0}s`); setPage("library"); };
  const mans: any[] = [];

  if (section === "analytics") {
    const rows = Object.entries(st.mastery).sort((a, b) => a[1] - b[1]).slice(0, 8);
    const tip = st.questionAcc ? Object.keys(st.questionAcc).sort((a, b) => (st.questionAcc[a]?.total - st.questionAcc[b]?.total) || 0).slice(0, 2) : [];
    return (<div><h1>AI Analytics</h1><div className="donut"><canvas id="donut" width="120" height="120"></canvas><span className="donut-label">Mastery</span></div><ul>{rows.map(([k, v]) => <li key={k}><b>{k}</b> {Math.round(v * 10)}/10</li>)}</ul><p className="muted small">Cold-start bandit params: q={banditState.q.toFixed(2)}, a={banditState.a.toFixed(1)}, f={banditState.f.toFixed(2)}</p></div>);
  }
  if (section === "planner") {
    const weak = Object.entries(st.mastery).filter(([, v]) => v < 5).slice(0, 5);
    return (<div><h1>Study Planner</h1><p>Time available: {storage.weeklyHours(st)}h this week</p><h2>Focus on (weak + recently studied)</h2><ul>{weak.map(([k, v]) => <li key={k}><b>{k}</b> — mastery {Math.round(v * 10)}/10 — {Math.round(storage.forgetting(st, k) * 100)}% forgetting risk</li>)}</ul><h2>Pacing</h2><p className="muted">Weekly hours adapt: {Math.min(Math.max(Math.round(storage.weeklyHours(st) / 12), 3), 10)}min/unit</p></div>);
  }
  if (section === "resources") {
    return (<div><h1>Offline Notes</h1><p>Search uses the catalog and manifests of the seed courses (6.006, 6.100L, 18.06). <button className="btn primary" onClick={() => { window.dispatchEvent(new Event("open-search")); document.getElementById("ask-search")?.focus(); }}>Open search</button></p><h2>Topics</h2><ul className="muted">{["asymptotics", "divide & conquer", "dynamic programming", "graphs", "linear algebra", "LA: systems", "LA: eigen", "LA: svd", "probability"].map(t => <li key={t}>{t}</li>)}</ul><h2>Ask SikshaSetu</h2><div className="row"><input id="ask-input" placeholder="Ask SikshaSetu…" onKeyDown={(e: any) => e.key === "Enter" && ask(e.target.value)} onChange={() => {}} /><button className="btn primary" onClick={() => { const i = (document.getElementById("ask-input") as HTMLInputElement)?.value || ""; ask(i); }}>Search</button></div><div id="ask-out" className="muted small">{out.length > 0 && out.map((m: any, k) => <div key={m.id} className="muted"><b>{m.type}</b>: {m.name || m.excerpt}<br />{m.excerpt?.slice(0, 90)}{m.ts != null ? ` · t=${Math.round(m.ts)}s` : ""}</div>)}</div><p className="muted">Note: offline retrieval over concepts, notes and transcripts — no LLM at runtime.</p></div>);
  }
  if (section === "sync") {
    return (<div><h1>Sync Progress</h1><p>Progress sync by short code. Your local mastery vector is personal — export it or enter a peer/admin code to import. Restore codes into the admin panel's Roster import.</p><input className="muted" placeholder="Paste sync code…" /></div>);
  }
  return (<div><h1>Settings</h1><div className="row"><label><input type="checkbox" checked={st.libraryPlanOnly} onChange={(e) => setSt({ ...st, libraryPlanOnly: e.target.checked })} /> Download only my plan</label></div><div className="row"><button className="btn ghost" onClick={async () => { await storage.saveState(st); setMsg("Saved"); }}>Save</button> {msg && <span className="muted small">{msg}</span>}</div></div>);
}
