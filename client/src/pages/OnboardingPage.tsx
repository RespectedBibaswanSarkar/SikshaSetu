import { useState } from "react";
import { BookOpen } from "lucide-react";
import { api } from "../live";
import { setSid } from "../store";

interface OnboardingPageProps {
  onComplete: () => void;
}

export default function OnboardingPage({ onComplete }: OnboardingPageProps) {
  const [name, setName] = useState("");
  const [roll, setRoll] = useState("");
  const [courses, setCourses] = useState<string[]>(["6.006", "6.100L", "18.06"]);
  const [hours, setHours] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const AVAILABLE_COURSES = [
    { slug: "6.006", title: "Introduction to Algorithms" },
    { slug: "6.100L", title: "Intro to CS & Programming (Python)" },
    { slug: "18.06", title: "Linear Algebra" },
  ];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) { setError("Please enter your name."); return; }
    setLoading(true); setError(null);
    try {
      const r = await api.registerStudent({
        name: name.trim(),
        roll_no: roll.trim() || undefined,
        courses,
        weekly_hours: hours,
      });
      setSid(r.student_id);
      onComplete();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  function toggleCourse(slug: string) {
    setCourses(prev =>
      prev.includes(slug) ? prev.filter(c => c !== slug) : [...prev, slug]
    );
  }

  return (
    <div className="onboarding-page" role="main">
      <div className="onboarding-card">
        <div className="onboarding-brand">
          <div className="brand-icon-box">
            <BookOpen size={28} className="brand-icon-svg" aria-hidden="true" />
          </div>
          <div>
            <div className="brand-main" style={{ fontSize: "1.5rem" }}>SikshaSetu</div>
            <div className="brand-sub">Learn · Analyse · Grow</div>
          </div>
        </div>

        <h1 className="onboarding-title">Welcome! Let's get you set up.</h1>
        <p className="onboarding-sub">
          Personalized MIT OCW practice — algorithms, Python, and linear algebra.
        </p>

        <form onSubmit={handleSubmit} className="onboarding-form" noValidate>
          <div className="form-group">
            <label htmlFor="onboarding-name">Full Name *</label>
            <input
              id="onboarding-name"
              data-testid="onboarding-name"
              type="text"
              className="form-input"
              placeholder="e.g. Priya Sharma"
              value={name}
              onChange={e => setName(e.target.value)}
              required
              autoFocus
              aria-required="true"
            />
          </div>

          <div className="form-group">
            <label htmlFor="onboarding-roll">Roll Number (optional)</label>
            <input
              id="onboarding-roll"
              type="text"
              className="form-input"
              placeholder="e.g. 2023CS001"
              value={roll}
              onChange={e => setRoll(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Courses to enroll</label>
            <div className="course-checkboxes">
              {AVAILABLE_COURSES.map(c => (
                <label key={c.slug} className="course-checkbox-label">
                  <input
                    type="checkbox"
                    checked={courses.includes(c.slug)}
                    onChange={() => toggleCourse(c.slug)}
                    aria-label={`Enroll in ${c.title}`}
                  />
                  <span>{c.slug}: {c.title}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="onboarding-hours">Weekly study hours: {hours}h</label>
            <input
              id="onboarding-hours"
              type="range"
              min={1} max={40} step={1}
              value={hours}
              onChange={e => setHours(Number(e.target.value))}
              className="form-range"
              aria-label={`Weekly hours: ${hours}`}
            />
          </div>

          {error && <div className="form-error" role="alert">{error}</div>}

          <button
            type="submit"
            className="btn-primary onboarding-submit"
            data-testid="onboarding-submit"
            disabled={loading || courses.length === 0}
            aria-busy={loading}
          >
            {loading ? "Setting up…" : "Start Learning →"}
          </button>
        </form>
      </div>
    </div>
  );
}
