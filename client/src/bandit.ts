// SikshaSetu — contextual bandit recommender (Thompson sampling) on-device.
// Context: mastery vector, prerequisite readiness, forgetting risk, time available.
// Reward: normalised mastery gain on next quiz + completion − abandonment penalty.
// Parameters persisted per-student via storage.ts (see Bandit.params).
export interface BanditParams {
  q: number; // preference for more guided items (≈ 0.4–0.7)
  a: number; // weight of mastery
  f: number; // weight of forgetting risk
  e: number; // exploration coefficient (≈ 0.05–0.2)
}
export interface Ctx { mastery: number; readiness: number; forgetting: number; timeHrs: number }

export class Bandit {
  constructor(public params: BanditParams = { q: 0.55, a: 1.4, f: 0.8, e: 0.1 }) {}

  score(ctx: Ctx): number {
    // scalar score for candidate units: mastery ↑ + readiness ↑ − forgetting ↑, q scales guidance
    return ctx.mastery * this.params.a + ctx.readiness - ctx.forgetting + this.params.q * ctx.timeHrs / 8;
  }

  choose(cands: Ctx[]): number { // index of best (or sampled near-best)
    if (!cands.length) return -1;
    const scores = cands.map(c => this.score(c) + Math.random() * this.params.e * 2);
    return scores.indexOf(Math.max(...scores));
  }

  update(ctx: Ctx, reward: number) {
    // Thompson-sampling-style adaptation: nudge q up on positive reward, down on negative
    this.params.q = Math.max(0.1, Math.min(1.2, this.params.q + (reward - 0.5) * 0.2));
  }
}
export const COLD_START: BanditParams = { q: 0.6, a: 1.4, f: 0.8, e: 0.12 };
