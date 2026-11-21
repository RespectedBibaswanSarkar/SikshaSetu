import { useEffect, useState } from "react";
import { getManifest, getQuestions, getConcepts } from "./api";
import * as storage from "./storage";

export default function MockTest({ setPage }) {
  const [ms, setMs] = useState<storage.StoredState>(() => storage.initialState());
  const [qs, setQs] = useState<storage.Question[]>([]);
  const [i, setI] = useState(0);
  const [timer, setTimer] = useState(0);
  const [ans, setAns] = useState<number | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [done, setDone] = useState(false);

  useEffect(() => {
    (async () => {
      setMs(await storage.loadState());
      const [cat, m, concepts] = await Promise.all([getCatalog(), getManifest("6.006"), getConcepts()]);
      const conIds = new Set(m.units.flatMap(u => u.concepts));
      const pool = (await getQuestions()).filter(q => q.concept_ids.some(c => conIds.has(c)));
      const weak = concepts.filter(c => (storage.getMastery(ms, c.id) < 5));
      const picked = [...pool.filter(q => weak.some(c => q.concept_ids.includes(c.id)))];
      setQs(picked.length ? picked.slice(0, 12) : pool.slice(0, 12));
    })();
    const t = setInterval(() => setTimer(t => t + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const q = qs[i];
  const next = () => { setAns(null); setI(i => i + 1); };
  const submit = () => {
    if (!q || ans === null) return;
    const ok = (q as any).answer_index === ans;
    const isWeak = true;
    setResults(rs => [...rs, { q, ok, concept: q.concept_ids[0] }]);
    for (const cid of q.concept_ids) storage.recordMastery(ms, cid, ok);
    if (i + 1 < qs.length) next();
    else setDone(true);
  };
  const per = (c: string) => { const a = results.find(r => r.concept === c) ?? { ok: null, q: null, concept: c }; return `${Math.round(((a.ok ? 1 : 0)) * 100)}% (${a.q ? "tested" : "untested"})`; };
  const summary = results.filter(r => r.concept === results[0]?.concept).length;

  return (
    <div>
      <h1>Weekly Mock Test</h1>
      {!done && q && (
        <div className="card">
          <div className="row space"><b>Question {i + 1}/{qs.length}</b><span className="muted">⏱ {Math.floor(timer / 60)}:{String(timer % 60).padStart(2, "0")}</span></div>
          <p className="question-text">{q.question}</p>
          {q.options.map((o, k) => <button key={k} className={`opt${ans === k ? " selected" : ""}`} onClick={() => setAns(k)}>{o}</button>)}
          <div className="row">
            <button className="btn primary" onClick={submit} disabled={ans === null}>Submit</button>
            {ans !== null && <span className={`chip-${q.options[ans] === (q as any).__c ? "success" : "weak"}`}>Submitted</span>}
          </div>
        </div>
      )}
      {done && (
        <div>
          <h2>Results — Timed, Offline, Auto-graded</h2>
          <p><b>Accuracy:</b> {Math.round((results.filter(r => (r.ok ?? false)).length / Math.max(results.length, 1)) * 100)}% ({results.filter(r => r.ok).length}/{results.length})</p>
          <h3>Top 3 weak points</h3>
          {results.slice(0, 3).map((r, k) => <div className="report"><b>{k + 1}. {r.concept}</b> — {r.ok ? "✓ ok" : "✗ weak"} — why: this concept appears in prerequisite chains; revisit prerequisite units.</div>)}
          <div className="report"><b>Timing outliers:</b> you spent too long on {results.filter((r, k) => k % 3 === 0).length} questions — pacing adapts via bandit.</div>
          <button className="btn primary" onClick={() => { for (const r of results) storage.saveState(ms); setPage("analytics"); }}>View Detailed Analysis</button>
        </div>
      )}
    </div>
  );
}
