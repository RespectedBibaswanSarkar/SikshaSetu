import { useState, useEffect } from "react";
import { api, TestInfo, HubError } from "../live";
import { mutate } from "../store";
import { AnyPage } from "../App";
import ErrorState from "../components/ErrorState";
import { FileCheck2, ArrowRight, Clock, CheckCircle2, XCircle, Flag } from "lucide-react";

interface TestsPageProps {
  sid: string;
  navigate: (p: AnyPage) => void;
}

type Phase = "list" | "in-test" | "submitting" | "error" | "loading";

interface ActiveTest {
  test_id: string;
  questions: { question_id: string; concept_id: string; stem: string; options: string[]; difficulty: number; time_limit_sec: number }[];
}

export default function TestsPage({ sid, navigate }: TestsPageProps) {
  const [phase, setPhase] = useState<Phase>("loading");
  const [tests, setTests] = useState<TestInfo[]>([]);
  const [activeTest, setActiveTest] = useState<ActiveTest | null>(null);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Map<string, { choice: string; seconds: number; flagged: boolean }>>(new Map());
  const [selected, setSelected] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [error, setError] = useState("");

  useEffect(() => {
    loadTests();
  }, []);

  async function loadTests() {
    setPhase("loading");
    try {
      const t = await api.tests(sid);
      setTests(t);
      setPhase("list");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
      setPhase("error");
    }
  }

  async function startTest() {
    setPhase("loading");
    try {
      const t = await mutate(() => api.createTest(sid));
      setActiveTest(t);
      setCurrent(0);
      setAnswers(new Map());
      setSelected(null);
      setStartTime(Date.now());
      setPhase("in-test");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
      setPhase("error");
    }
  }

  function selectOption(opt: string) {
    if (!activeTest) return;
    const q = activeTest.questions[current];
    const secs = Math.round((Date.now() - startTime) / 1000);
    setSelected(opt);
    const newAnswers = new Map(answers);
    newAnswers.set(q.question_id, { choice: opt, seconds: secs, flagged: answers.get(q.question_id)?.flagged ?? false });
    setAnswers(newAnswers);
  }

  function goTo(idx: number) {
    if (!activeTest) return;
    setStartTime(Date.now());
    setSelected(answers.get(activeTest.questions[idx].question_id)?.choice ?? null);
    setCurrent(idx);
  }

  function toggleFlag() {
    if (!activeTest) return;
    const q = activeTest.questions[current];
    const newAnswers = new Map(answers);
    const existing = newAnswers.get(q.question_id);
    newAnswers.set(q.question_id, { choice: existing?.choice ?? "", seconds: existing?.seconds ?? 0, flagged: !(existing?.flagged ?? false) });
    setAnswers(newAnswers);
  }

  async function submitTest() {
    if (!activeTest) return;
    setPhase("submitting");
    const ans = activeTest.questions.map(q => ({
      question_id: q.question_id,
      choice: answers.get(q.question_id)?.choice ?? "",
      seconds: answers.get(q.question_id)?.seconds ?? 60,
    }));
    try {
      const r = await mutate(() => api.submitTest(sid, activeTest.test_id, ans));
      navigate({ name: "test-detail", tid: r.test_id });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error submitting");
      setPhase("error");
    }
  }

  if (phase === "error") return (
    <div className="page-content">
      <ErrorState message={error} onRetry={loadTests} />
    </div>
  );

  if (phase === "loading" || phase === "submitting") return (
    <div className="page-content">
      <div className="loading-spinner" aria-label={phase === "submitting" ? "Submitting…" : "Loading…"}>
        <div className="spinner" />
        {phase === "submitting" && <p style={{ marginTop: 16 }}>Submitting your answers…</p>}
      </div>
    </div>
  );

  if (phase === "in-test" && activeTest) {
    const q = activeTest.questions[current];
    const total = activeTest.questions.length;
    const answered = answers.size;
    const isFlagged = answers.get(q.question_id)?.flagged ?? false;

    return (
      <div className="page-content">
        <div className="test-container">
          <div className="test-header">
            <h1>Mock Test</h1>
            <div className="test-progress-info">
              <span>{answered}/{total} answered</span>
              <button className={`flag-btn ${isFlagged ? "flagged" : ""}`} onClick={toggleFlag}
                aria-label={isFlagged ? "Unflag question" : "Flag for review"}
                aria-pressed={isFlagged}>
                <Flag size={16} aria-hidden="true" /> {isFlagged ? "Flagged" : "Flag"}
              </button>
            </div>
          </div>

          {/* Question Navigator */}
          <div className="question-nav" role="navigation" aria-label="Question navigation">
            {activeTest.questions.map((qq, i) => (
              <button key={i}
                className={`q-nav-btn ${i === current ? "current" : ""} ${answers.has(qq.question_id) ? "answered" : ""} ${answers.get(qq.question_id)?.flagged ? "flagged" : ""}`}
                onClick={() => goTo(i)}
                aria-label={`Question ${i + 1}${answers.has(qq.question_id) ? " (answered)" : ""}`}
                aria-current={i === current ? "true" : undefined}>
                {i + 1}
              </button>
            ))}
          </div>

          <div className="test-card">
            <div className="test-q-meta">
              <span>Q{current + 1} / {total}</span>
              <span className="test-diff">Difficulty: {q.difficulty}/5</span>
            </div>
            <h2 className="test-stem" id="test-question">{q.stem}</h2>

            <div className="test-options" role="group" aria-labelledby="test-question">
              {q.options.map((opt, i) => (
                <button
                  key={i}
                  className={`practice-option ${selected === opt ? "option-selected" : ""}`}
                  data-testid="practice-option"
                  onClick={() => selectOption(opt)}
                  aria-pressed={selected === opt}
                  aria-label={`Option ${String.fromCharCode(65 + i)}: ${opt}`}
                >
                  <span className="option-letter" aria-hidden="true">{String.fromCharCode(65 + i)}</span>
                  <span className="option-text">{opt}</span>
                </button>
              ))}
            </div>

            <div className="test-nav-actions">
              {current > 0 && (
                <button className="btn-secondary" onClick={() => goTo(current - 1)}>← Previous</button>
              )}
              {current < total - 1 ? (
                <button className="btn-primary" onClick={() => goTo(current + 1)}>
                  Next <ArrowRight size={16} aria-hidden="true" />
                </button>
              ) : (
                <button className="btn-primary btn-submit" onClick={submitTest}>
                  Submit Test →
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // List view
  return (
    <div className="page-content">
      <div className="tests-page">
        <div className="page-header">
          <h1>Mock Tests</h1>
          <button className="btn-primary" onClick={startTest}>
            <FileCheck2 size={16} aria-hidden="true" /> Start New Test
          </button>
        </div>

        {tests.length === 0 ? (
          <div className="empty-state">
            <FileCheck2 size={48} className="empty-icon" aria-hidden="true" />
            <h2>No tests yet</h2>
            <p>Take your first mock test to see how you're doing!</p>
            <button className="btn-primary" onClick={startTest}>Start Test →</button>
          </div>
        ) : (
          <ul className="test-history-list" role="list">
            {tests.map(t => (
              <li key={t.test_id} className="test-history-item" role="listitem">
                <button className="test-history-btn"
                  onClick={() => navigate({ name: "test-detail", tid: t.test_id })}
                  aria-label={`Test from ${new Date(t.ts * 1000).toLocaleDateString()}: ${t.score_pct ?? "not submitted"}%`}>
                  <div className="test-hist-left">
                    <div className="test-hist-date">
                      <Clock size={14} aria-hidden="true" />
                      {new Date(t.ts * 1000).toLocaleDateString()}
                    </div>
                    <div className="test-hist-status" aria-label={`Status: ${t.status}`}>
                      {t.status === "submitted" ? (
                        <><CheckCircle2 size={14} className="status-done" aria-hidden="true" /> Completed</>
                      ) : (
                        <><XCircle size={14} className="status-pending" aria-hidden="true" /> In Progress</>
                      )}
                    </div>
                  </div>
                  <div className="test-hist-score">
                    {t.score_pct !== null ? (
                      <span className="score-badge" aria-label={`Score: ${t.score_pct}%`}>{t.score_pct}%</span>
                    ) : (
                      <span className="score-badge score-pending">—</span>
                    )}
                  </div>
                  <ArrowRight size={16} className="arrow-icon" aria-hidden="true" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
