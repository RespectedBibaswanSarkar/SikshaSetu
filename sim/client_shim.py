# Python port of the on-device bandit (client/src/bandit.ts) for comparison runs.
import random


class Bandit:
    def __init__(self, q=0.6, a=1.4, f=0.8, e=0.12):
        self.q, self.a, self.f, self.e = q, a, f, e

    def score(self, ctx):
        return ctx["mastery"] * self.a + ctx["readiness"] - ctx["forgetting"] + self.q * ctx["time_hrs"] / 8

    def choose(self, cands):
        if not cands:
            return -1
        scores = [self.score(c) + random.random() * self.e * 2 for c in cands]
        return scores.index(max(scores))

    def update(self, ctx, reward):
        self.q = max(0.1, min(1.2, self.q + (reward - 0.5) * 0.2))


class Ctx(dict):
    pass
