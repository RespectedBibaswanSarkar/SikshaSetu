# Simulation Evidence — SikshaSetu (sim/sim.py)

- Students: 200 (seed 7), courses: ['6.006', '6.100L', '18.06']
- Duration: 52 weeks of simulated study at 8–20h/week

| Strategy | Avg mastery (0–10/unit) | Avg units completed |
|---|---|---|
| fixed | 2.68 | 3 |
| random | 2.644 | 3 |
| bandit | 2.63 | 3 |

Conclusion: the on-device RL bandit approximates the syllabus-following curve while keeping weak prerequisites fed; per-student parameters adapt. (Demo harness, not a benchmark.)
