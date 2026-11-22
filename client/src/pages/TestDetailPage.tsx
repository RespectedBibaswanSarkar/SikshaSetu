import { useState, useEffect } from "react";
import { api, TestDetail, HubError } from "../live";
import { AnyPage } from "../App";
import ErrorState from "../components/ErrorState";
import { CheckCircle2, XCircle, ArrowLeft, Trophy } from "lucide-react";

interface TestDetailPageProps {
  sid: string;
  tid: string;
  navigate: (p: AnyPage) => void;
}

export default function TestDetailPage({ sid, tid, navigate }: TestDetailPageProps) {
  const [detail, setDetail] = useState<TestDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showReview, setShowReview] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getTest(sid, tid)
      .then(d => { setDetail(d); setLoading(false); })
      .catch((e: unknown) => {
        setError(e instanceof HubError ? e.message : "Error loading test");
        setLoading(false);
      });
  }, [sid, tid]);

  if (loading) return (
    <div className="page-content">
      <div className="loading-spinner" aria-label="Loading test results…"><div className="spinner" /></div>
    </div>
  );

  if (error || !detail) return (
    <div className="page-content">
      <ErrorState message={error ?? "Test not found"} onRetry={() => navigate({ name: "tests" })} />
    </div>
  );

  const pct = detail.score_pct ?? 0;

  return (
    <div className="page-content">
      <div className="test-detail-page">
        <button className="btn-back" onClick={() => navigate({ name: "tests" })}
          aria-label="Back to tests">
          <ArrowLeft size={16} aria-hidden="true" /> Back
        </button>

        <div className="test-result-card">
          <Trophy size={48} className={`result-trophy ${pct >= 70 ? "trophy-gold" : pct >= 50 ? "trophy-silver" : "trophy-bronze"}`} aria-hidden="true" />
          <h1 className="result-score" aria-label={`Score: ${pct}%`}>{pct}%</h1>
          <p className="result-summary">
            {detail.correct}/{detail.total} correct — {detail.answered} answered
          </p>
        </div>

        <div className="by-concept-grid">
          <h2>By Concept</h2>
          <ul className="by-concept-list" role="list">
            {detail.by_concept.map(bc => (
              <li key={bc.concept_id} className="by-concept-item" role="listitem">
                <span className="by-concept-name">{bc.name}</span>
                <div className="by-concept-bar" aria-hidden="true">
                  <div className="by-concept-fill" style={{ width: `${Math.round(bc.correct / Math.max(bc.total, 1) * 100)}%` }} />
                </div>
                <span className="by-concept-pct">{bc.correct}/{bc.total}</span>
              </li>
            ))}
          </ul>
        </div>

        {detail.weak_points.length > 0 && (
          <div className="weak-points-section">
            <h2>Areas to Improve</h2>
            <ul className="weak-points-list" role="list">
              {detail.weak_points.map(w => (
                <li key={w.concept_id} role="listitem">
                  <button className="weak-point-btn"
                    onClick={() => navigate({ name: "concept", cid: w.concept_id })}
                    aria-label={`Practice ${w.name}`}>
                    {w.name} →
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="review-section">
          <button className="btn-secondary" onClick={() => setShowReview(r => !r)}>
            {showReview ? "Hide" : "Show"} Per-Question Review
          </button>
          {showReview && (
            <div className="review-list">
              {detail.review.map((r, i) => (
                <div key={r.question_id} className={`review-item ${r.correct ? "review-correct" : "review-wrong"}`}>
                  <div className="review-header">
                    <span className="review-num">Q{i + 1}</span>
                    {r.correct
                      ? <><CheckCircle2 size={14} className="status-done" aria-hidden="true" /> Correct</>
                      : <><XCircle size={14} className="status-pending" aria-hidden="true" /> Wrong</>}
                  </div>
                  <p className="review-stem">{r.stem}</p>
                  <p className="review-your">Your answer: {r.your_choice || "(skipped)"}</p>
                  {!r.correct && <p className="review-correct-ans">Correct: {r.correct_answer}</p>}
                  <p className="review-expl">{r.explanation}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
