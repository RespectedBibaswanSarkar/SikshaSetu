import { useState, useEffect, useCallback } from "react";
import { api, Question, AnswerResult, HubError } from "../live";
import { mutate } from "../store";
import ErrorState from "../components/ErrorState";
import { CheckCircle2, XCircle, ArrowRight, Lightbulb, BookOpen } from "lucide-react";

interface PracticePageProps {
  sid: string;
  mode?: "diagnostic";
  course?: string;
}

type Phase = "loading" | "question" | "feedback" | "done" | "error";

export default function PracticePage({ sid, mode, course }: PracticePageProps) {
  const [phase, setPhase] = useState<Phase>("loading");
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [error, setError] = useState<string>("");
  const [correct, setCorrect] = useState(0);
  const [total, setTotal] = useState(0);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [diagDone, setDiagDone] = useState(false);

  const loadNext = useCallback(async () => {
    setPhase("loading");
    setSelected(null);
    setResult(null);
    try {
      const q = await api.next(sid, { course, mode });
      setQuestion(q);
      setStartTime(Date.now());
      setPhase("question");
    } catch (e) {
      if (e instanceof HubError) { setError(e.message); setPhase("error"); }
      else { setError("Failed to load question"); setPhase("error"); }
    }
  }, [sid, course, mode]);

  useEffect(() => { loadNext(); }, [loadNext]);

  async function handleSelect(opt: string) {
    if (phase !== "question" || !question) return;
    setSelected(opt);
    const seconds = Math.round((Date.now() - startTime) / 1000);
    try {
      const r = await mutate(() => api.answer(sid, {
        question_id: question.question_id,
        choice: opt,
        seconds,
      }));
      setResult(r);
      setTotal(t => t + 1);
      if (r.correct) setCorrect(c => c + 1);
      setPhase("feedback");
      if (mode === "diagnostic" && question.diagnostic_progress === 12) {
        setDiagDone(true);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error submitting answer");
      setPhase("error");
    }
  }

  if (phase === "error") {
    return (
      <div className="page-content">
        <ErrorState message={error} onRetry={loadNext} />
      </div>
    );
  }

  if (phase === "loading") {
    return (
      <div className="page-content">
        <div className="loading-spinner" aria-label="Loading question…"><div className="spinner" /></div>
      </div>
    );
  }

  if (diagDone && result) {
    const wa = result.live?.weak_areas ?? [];
    return (
      <div className="page-content">
        <div className="practice-done-card">
          <CheckCircle2 size={48} className="done-icon" aria-hidden="true" />
          <h2>Diagnostic Complete!</h2>
          <p>{correct}/{total} correct ({Math.round(correct / Math.max(total, 1) * 100)}%)</p>
          {wa.length > 0 && (
            <>
              <h3>Your weak areas:</h3>
              <ul className="weak-area-list">
                {wa.map((w: { concept_id: string; name: string }) => (
                  <li key={w.concept_id}>{w.name}</li>
                ))}
              </ul>
              <p className="done-action">Start remediation practice to strengthen these concepts.</p>
            </>
          )}
          <button className="btn-primary" onClick={loadNext}>Start Remediation →</button>
        </div>
      </div>
    );
  }

  if (!question) return null;

  const diag = mode === "diagnostic";
  const progNum = question.diagnostic_progress ?? null;

  return (
    <div className="page-content">
      <div className="practice-container">
        {diag && progNum !== null && (
          <div className="diag-progress" role="progressbar" aria-valuenow={progNum} aria-valuemin={0} aria-valuemax={12}
            aria-label={`Diagnostic: question ${progNum} of 12`}>
            <div className="diag-progress-bar" style={{ width: `${(progNum / 12) * 100}%` }} />
            <span className="diag-progress-text">{progNum}/12</span>
          </div>
        )}

        {/* Session summary */}
        {total > 0 && (
          <div className="session-summary" aria-label="Session summary">
            <span>Session: {correct}/{total} correct ({Math.round(correct / total * 100)}%)</span>
          </div>
        )}

        <div className="practice-card">
          <div className="practice-meta">
            <span className="practice-course">{question.course_slug}</span>
            <span className="practice-diff">Difficulty: {question.difficulty}/5</span>
            <span className="practice-time">⏱ {question.time_limit_sec}s</span>
          </div>

          {question.why && (
            <div className="practice-why">
              <Lightbulb size={14} aria-hidden="true" /> {question.why}
            </div>
          )}

          <h2 className="practice-stem" id="question-text">{question.stem}</h2>

          <div className="practice-options" role="group" aria-labelledby="question-text">
            {question.options.map((opt, i) => {
              let cls = "practice-option";
              if (phase === "feedback" && result) {
                if (opt === result.correct_answer) cls += " option-correct";
                else if (opt === selected && !result.correct) cls += " option-wrong";
              }
              return (
                <button
                  key={i}
                  className={cls}
                  data-testid="practice-option"
                  onClick={() => handleSelect(opt)}
                  disabled={phase === "feedback"}
                  aria-pressed={selected === opt}
                  aria-label={`Option ${String.fromCharCode(65 + i)}: ${opt}`}
                >
                  <span className="option-letter" aria-hidden="true">{String.fromCharCode(65 + i)}</span>
                  <span className="option-text">{opt}</span>
                  {phase === "feedback" && result && opt === result.correct_answer && (
                    <CheckCircle2 size={16} className="opt-check" aria-hidden="true" />
                  )}
                  {phase === "feedback" && result && opt === selected && !result.correct && (
                    <XCircle size={16} className="opt-wrong" aria-hidden="true" />
                  )}
                </button>
              );
            })}
          </div>

          {phase === "feedback" && result && (
            <div className="practice-feedback" data-testid="practice-feedback" role="region" aria-label="Answer feedback">
              <div className={`feedback-verdict ${result.correct ? "verdict-correct" : "verdict-wrong"}`}>
                {result.correct
                  ? <><CheckCircle2 size={16} aria-hidden="true" /> Correct!</>
                  : <><XCircle size={16} aria-hidden="true" /> Incorrect — the answer is: {result.correct_answer}</>}
              </div>
              <div className="feedback-explanation">
                <strong>Explanation:</strong> {result.explanation}
              </div>
              {result.source_ref && (
                <div className="feedback-source">
                  <BookOpen size={12} aria-hidden="true" />
                  Source: {result.source_ref}
                </div>
              )}
              <div className="mastery-chip" aria-label={`Mastery: ${Math.round(result.concept.mastery_before * 100)}% → ${Math.round(result.concept.mastery_after * 100)}%`}>
                <span>Mastery: {Math.round(result.concept.mastery_before * 100)}% → {Math.round(result.concept.mastery_after * 100)}%</span>
              </div>
              <button
                className="btn-primary practice-next"
                data-testid="practice-next"
                onClick={loadNext}
                aria-label="Next question"
              >
                Next Question <ArrowRight size={16} aria-hidden="true" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
