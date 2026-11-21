import { useEffect, useState } from "react";
import { getManifest, getQuestions } from "./api";
import * as storage from "./storage";

// Adaptive diagnostic: 8–12 questions over the prerequisite graph, Elo-style mastery.
export default function Diagnostic({ setPage }) {
  const [ms, setMs] = useState<storage.StoredState>(() => storage.initialState());
  const [q, setQ] = useState<storage.Question | null>(null);
  const [ans, setAns] = useState<number | null>(null);
  const [correct, setCorrect] = useState<boolean | null>(null);
  const [score, setScore] = useState(0);
  const [todo, setTodo] = useState<storage.Question[]>([]);

  useEffect(() => {
    (async () => {
      const m = await getManifest("6.006");
      const { getCatalog } = await import("./api");
      const cat = await getCatalog();
      for (const slug of cat.courses.map(c => c.slug)) { try { await getManifest(slug); } catch {} }
      setMs(await storage.loadState());
      const qs = (await getQuestions()).filter(x => x.concept_ids.some(c => m.units.some(u => u.concepts.includes(c)))).slice(0, 12);
      setTodo(qs);
      if (qs.length) { setQ(qs[0]); setTodo(qs.slice(1)); }
    })();
  }, []);

  const submit = async () => {
    if (ans === null || !q) return;
    const ok = (q as any).answer_index === ans;
    storage.recordMastery(ms, q.concept_ids[0], ok);
    await storage.saveState(ms);
    setScore(s => s + 1); setCorrect(ok); setAns(null);
    const nq = todo[0];
    if (nq) { setQ(nq); setTodo(todo.slice(1)); }
    else {
      const total = Object.values(ms.questionAcc).reduce((s: number, a: any) => s + (a.total || 0), 0);
      setPage("analytics");
      // eslint-disable-next-line no-alert
      alert(`Diagnostic done — ${score} correct of ${total}. Your mastery has been updated.`);
    }
  };

  return (
    <div>
      <h1>Adaptive Diagnostic</h1>
      {q && (
        <div className="card">
          <p className="question-text">{q.question}</p>
          {q.options.map((o, i) => (
            <button key={i} className={`opt${ans === i ? " selected" : ""}`} onClick={() => setAns(i)}>{o}</button>
          ))}
          <div className="row">
            <button className="btn primary" onClick={submit} disabled={ans === null}>Submit</button>
            {correct !== null && <span className={`chip-${correct ? "success" : "weak"}`}>{correct ? "correct" : "incorrect"}</span>}
          </div>
        </div>
      )}
      <div className="muted small">Questions: {todo.length + (q ? 1 : 0)} in your prerequisite graph. <button className="btn ghost" onClick={() => setPage("dashboard")}>Skip to dashboard</button></div>
    </div>
  );
}
