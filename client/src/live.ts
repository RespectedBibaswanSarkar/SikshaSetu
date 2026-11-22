/**
 * live.ts — Single typed API client for SikshaSetu.
 * ALL data comes from /api/learn/*. No offline fallbacks, no mock data.
 * If the hub is unreachable, throws HubError so the UI can show error-state.
 */

export class HubError extends Error {
  constructor(msg = "Hub unreachable") { super(msg); this.name = "HubError"; }
}

const BASE = "/api/learn";

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const opts: RequestInit = {
    method,
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  let r: Response;
  try {
    r = await fetch(BASE + path, opts);
  } catch {
    throw new HubError();
  }
  if (!r.ok) {
    const txt = await r.text().catch(() => "");
    throw new HubError(`${r.status}: ${txt}`);
  }
  return r.json() as Promise<T>;
}

const get  = <T>(path: string)             => req<T>("GET",   path);
const post = <T>(path: string, body?: unknown) => req<T>("POST",  path, body);
const patch = <T>(path: string, body: unknown) => req<T>("PATCH", path, body);

// ── Types ────────────────────────────────────────────────────────────────

export interface CourseInfo {
  slug: string; title: string; term: string; ocw_url: string;
  description: string; concept_count: number; question_count: number;
}

export interface DashboardStats {
  overall_progress: number;
  tests_taken: number; tests_delta: number | null;
  accuracy: number | null; accuracy_delta: number | null;
  study_hours: number; study_delta: number | null;
  streak: number; streak_at_risk: boolean;
  focus_score: number | null;
  answered: number;
}

export interface WeakArea {
  concept_id: string; name: string; course: string; mastery: number;
}

export interface LearningPathItem {
  concept_id: string | null; label: string; title: string; action: string;
  course?: string;
}

export interface CourseProgress {
  slug: string; title: string; progress: number; mastered: number; total: number;
}

export interface Notification {
  kind: string; message: string; ts?: number;
}

export interface Dashboard {
  student_id: string; name: string; roll_no: string | null;
  stats: DashboardStats;
  weak_areas: WeakArea[];
  learning_path: LearningPathItem[];
  next_mock_test: string | null;
  courses: CourseProgress[];
  notifications: Notification[];
  cleared: string[];
}

export interface Question {
  question_id: string; course_slug: string; concept_id: string;
  stem: string; options: string[]; difficulty: number;
  time_limit_sec: number; why: string;
  diagnostic_progress?: number;
}

export interface AnswerResult {
  correct: boolean; correct_answer: string; explanation: string;
  source_ref: string; seconds: number;
  concept: { concept_id: string; name: string; mastery_before: number; mastery_after: number };
  live: Dashboard;
}

export interface TestInfo {
  test_id: string; ts: number; status: string;
  score_pct: number | null; total: number | null;
}

export interface TestDetail {
  test_id: string; total: number; answered: number; correct: number;
  score_pct: number;
  by_concept: { concept_id: string; name: string; correct: number; total: number }[];
  weak_points: { concept_id: string; name: string }[];
  review: {
    question_id: string; concept_id: string; stem: string; options: string[];
    your_choice: string; correct_answer: string; correct: boolean;
    explanation: string; source_ref: string; seconds: number;
  }[];
  dashboard: Dashboard;
}

export interface TestQuestion {
  question_id: string; concept_id: string; stem: string; options: string[];
  difficulty: number; time_limit_sec: number;
}

export interface Test {
  test_id: string;
  questions: TestQuestion[];
}

export interface AnalyticsData {
  mastery: {
    concept_id: string; name: string; course: string; mastery: number;
    attempts: number; correct: number; retention: number; weak: boolean;
  }[];
  by_day: { date: string; answered: number; correct: number; minutes: number; accuracy: number }[];
  theta_history: number[];
  reward_history: number[];
  bandit_arms: { concept: string; score: number; exploit: number; exploration_bonus: number }[];
  weak_areas: WeakArea[];
  strong: string[];
}

export interface ConceptPage {
  concept: {
    id: string; course_slug: string; name: string; description: string;
    prerequisites: string[]; difficulty: number;
  };
  prerequisites: { id: string; name: string }[];
  chunks: { id: string; title: string; page_number: number; content: string; source_ref: string }[];
  exercises: { id: string; title: string; problem_text: string; solution_text: string; source_ref: string }[];
  question_count: number;
}

export interface CourseTree {
  modules: {
    id: string; title: string; sort_order: number;
    concepts: {
      id: string; name: string; difficulty: number;
      mastery: number; attempts: number; weak: boolean;
      question_count: number;
    }[];
  }[];
}

export interface SearchResult {
  id: string; title: string; course_slug: string;
  page_number: number; source_ref: string; excerpt: string;
}

export interface PlannerItem {
  id: string; concept_id: string | null; concept_name: string;
  action: string; label: string; done: boolean; due_date: string | null;
}

export interface NoteChunk {
  id: string; title: string; course_slug: string; module_id: string;
  page_number: number; content: string; source_ref: string; word_count: number;
}

export interface StudentProfile {
  id: string; name: string; roll_no: string | null;
  courses: string[]; weekly_hours: number; created: number;
}

export interface Institution {
  name: string; logo_url: string | null; admin_email: string | null;
}

// ── API calls ────────────────────────────────────────────────────────────

export const api = {
  health: () => get<{ status: string }>("/../../api/health"),

  courses: () => get<CourseInfo[]>("/courses"),

  registerStudent: (body: { name: string; roll_no?: string; courses?: string[]; weekly_hours?: number }) =>
    post<{ student_id: string }>("/students", body),

  dashboard: (sid: string) => get<Dashboard>(`/students/${sid}/dashboard`),

  patchStudent: (sid: string, body: Partial<{ name: string; roll_no: string; courses: string[]; weekly_hours: number }>) =>
    patch<StudentProfile>(`/students/${sid}`, body),

  next: (sid: string, params?: { course?: string; mode?: string }) => {
    const qs = new URLSearchParams();
    if (params?.course) qs.set("course", params.course);
    if (params?.mode) qs.set("mode", params.mode);
    const q = qs.toString();
    return get<Question>(`/students/${sid}/next${q ? "?" + q : ""}`);
  },

  answer: (sid: string, body: { question_id: string; choice: string; seconds: number }) =>
    post<AnswerResult>(`/students/${sid}/answer`, body),

  tests: (sid: string) => get<TestInfo[]>(`/students/${sid}/tests`),

  createTest: (sid: string, body?: { course?: string }) =>
    post<Test>(`/students/${sid}/tests`, body ?? {}),

  getTest: (sid: string, tid: string) => get<TestDetail>(`/students/${sid}/tests/${tid}`),

  submitTest: (sid: string, tid: string, answers: { question_id: string; choice: string; seconds: number }[]) =>
    post<TestDetail>(`/students/${sid}/tests/${tid}/submit`, { answers }),

  analytics: (sid: string) => get<AnalyticsData>(`/students/${sid}/analytics`),

  courseTree: (sid: string, slug: string) => get<CourseTree>(`/courses/${slug}/tree?sid=${sid}`),

  concept: (cid: string) => get<ConceptPage>(`/concepts/${cid}`),

  search: (q: string) => get<SearchResult[]>(`/search?q=${encodeURIComponent(q)}`),

  planner: (sid: string) => get<PlannerItem[]>(`/students/${sid}/planner`),

  plannerDone: (sid: string, item: string) => post<{ ok: boolean }>(`/students/${sid}/planner/${item}/done`),

  plannerRegenerate: (sid: string) => post<PlannerItem[]>(`/students/${sid}/planner/regenerate`),

  notes: (course?: string, type?: string) => {
    const qs = new URLSearchParams();
    if (course) qs.set("course", course);
    if (type) qs.set("type", type);
    return get<NoteChunk[]>(`/notes?${qs.toString()}`);
  },

  exportStudent: (sid: string) => get<unknown>(`/students/${sid}/export`),

  importStudent: (sid: string, data: unknown) => post<{ ok: boolean }>(`/students/${sid}/import`, data),

  resetStudent: (sid: string) => post<{ ok: boolean }>(`/students/${sid}/reset`),

  profile: (sid: string) => get<StudentProfile>(`/students/${sid}/profile`),
};
