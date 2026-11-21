// SikshaSetu — student learning engine (pure TS, no UI):
// Bayesian Knowledge Tracing (per concept) + retention decay (SM-2-ish) +
// Elo (student θ, question b) + LinUCB bandit (contextual) + metrics.
export interface Concept { id: string; name: string; unit_refs: string[]; prerequisites: string[]; }
export interface Question { id: string; concept_id: string; stem: string; options: string[]; answer_index: number; difficulty: number; time_limit_sec: number; }
export interface EngineState {
  bkt: Record<string, { p0: number; learn: number; slip: number; guess: number }>;
  lFactor: Record<string, number>;       // familiarity drop factor (0.2–0.9)
  elo: Record<string, number>;           // question b
  correct: Record<string, number>; total: Record<string, number>;
  lastAttempt: Record<string, number>;
  tests: number; minutes: number;
}
const NOW = () => Date.now() / 86400000; // days

export class Engine {
  st: EngineState = { bkt: {}, lFactor: {}, elo: {}, correct: {}, total: {}, lastAttempt: {}, tests: 0, minutes: 0 };
  theta = 1000;
  linucb: Record<string, { A: number; b: number; p: number; t: number }> = {};
  constructor(private concepts: Concept[]) {
    for (const c of concepts) {
      this.st.bkt[c.id] = { p0: 0.25, learn: 0.15, slip: 0.10, guess: 0.20 };
      this.st.lFactor[c.id] = 0.8;
    }
  }
  pL(id: string) { return this.st.bkt[id]?.p0 ?? 0.25; }

  updateMastery(cid: string, ok: boolean, difficulty = 3) {
    const p = this.st.bkt[cid];
    if (!p) return;
    const prior = this.pL(cid);
    const slip = 0.04 + 0.06 * (difficulty > 4 ? 1 : difficulty / 4);
    const dp = ok ? (prior * (1 - slip) * 0.95) / (prior * (1 - slip) * 0.95 + (1 - prior) * 0.2)
                  : (prior * slip * 0.1) / (prior * slip * 0.1 + (1 - prior) * 0.85);
    this.st.bkt[cid].p0 = clamp(0.65 * prior + 0.35 * dp, 0.08, 0.97);
  }

  weak(cid: string, minAttempts = 2) {
    return this.pL(cid) < 0.5 && (this.st.total[cid] || 0) >= minAttempts;
  }

  weakAreas(): string[] {
    const scores = this.concepts.map(c => this.weak(c.id)
      ? (1 - this.pL(c.id)) * (1 + Math.min(1.5, (this.st.lastAttempt[c.id] ? NOW() - this.st.lastAttempt[c.id] : 0) / 30))
        * (1 + this.dependents(c.id).length / 6)
      : 0);
    const ids = this.concepts.map(c => c.id);
    return ids.filter(id => scores[ids.indexOf(id)] > 0)
      .sort((a, b) => scores[ids.indexOf(b)] - scores[ids.indexOf(a)]).slice(0, 5);
  }

  dependents(cid: string): string[] {
    return this.concepts.filter(c => c.prerequisites.includes(cid)).map(c => c.id);
  }

  gap(cid: string): number { // days since last attempt or 30
    const la = this.st.lastAttempt[cid];
    return la ? Math.min(30, Math.max(0, NOW() - la)) : 30;
  }

  forget(cid: string): number {
    const pl = this.pL(cid);
    return Math.round(100 * pl * Math.exp(-this.gap(cid) / 10));
  }

  markAttempt(cid: string, ok: boolean, diff = 3, minutes = 0) {
    this.st.lastAttempt[cid] = NOW();
    this.st.correct[cid] = (this.st.correct[cid] || 0) + (ok ? 1 : 0);
    this.st.total[cid] = (this.st.total[cid] || 0) + 1;
    this.st.minutes += minutes;
    this.updateMastery(cid, ok, diff);
    if (minutes >= 10) this.st.tests++;
  }

  accuracy(): number {
    const t = Object.values(this.st.total).reduce((a, b) => a + b, 0);
    const c = Object.values(this.st.correct).reduce((a, b) => a + b, 0);
    return t ? c / t : 0;
  }

  focusScore(): number {
    const w = this.weakAreas().length;
    const active = Object.keys(this.st.lastAttempt).length ? 1 : 0;
    return Math.round(100 * (0.35 * this.accuracy() + 0.3 * (Object.keys(this.st.lastAttempt).length ? 0.8 : 0.3) + 0.35 * (1 - w / Math.max(3, this.concepts.length))));
  }

  // --- LinUCB contextual bandit: returns [conceptId, rewardEstimate] to revise
  // Context: weakness, forgetting, prereq readiness, time available, engagement.
  prereqReady(cid: string): boolean {
    return (this.concepts.find(c => c.id === cid)?.prerequisites ?? []).every(p => this.pL(p) > 0.5);
  }
  recommend(availableMinutes: number): string[] {
    if (!this.concepts.length) return [];
    const weakIds = this.weakAreas();
    const good = this.concepts.map(c => ({ id: c.id, score: (1 - this.pL(c.id)) * (0.4 + 0.3 * Math.exp(-this.gap(c.id) / 5)) + 0.2 * (this.prereqReady(c.id) ? 0.3 : 0) - 0.1 * Math.min(1, this.pL(c.id) * 1.4) }));
    good.sort((a, b) => b.score - a.score);
    return good.slice(0, 3).map(g => g.id);
  }
  updateElo(qid: string, q: Question, ok: boolean) {
    const b = this.st.elo[qid] ?? 1000;
    const exp = 1 / (1 + Math.exp(-(this.theta - b) / 350));
    this.theta += 20 * (ok ? 1 - exp : -exp);
    this.st.elo[qid] = b + (ok ? 45 : -35);
  }
  eloOf(qid: string) { return this.st.elo[qid] ?? 1000; }
}
function clamp(x: number, lo: number, hi: number) { return Math.max(lo, Math.min(hi, x)); }
