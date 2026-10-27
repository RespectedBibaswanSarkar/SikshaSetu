import numpy as np
from core.knowledge_graph import KnowledgeGraph
from core.bkt import BayesianKnowledgeTracing

class SikshaSetuEnv:
    """
    Gym-style environment built on the EduSim KSS idea (prerequisite-dependent learning).
    Simulated learners have hidden mastery, hidden learning speed, slip and guess,
    and FORGETTING during offline gaps (random 0-14 day disruptions between sessions).
    """
    def __init__(self, seed=42):
        self.rng = np.random.RandomState(seed)
        self.graph = KnowledgeGraph()
        self.concept_ids = self.graph.concept_ids
        self.n_concepts = self.graph.n_concepts
        self.reset()
    
    def reset(self, student_id=None):
        # Hidden learner parameters
        self.hidden_mastery = self.rng.beta(2, 5, self.n_concepts)
        self.learning_speed = self.rng.uniform(0.5, 1.5)
        self.slip = self.rng.uniform(0.05, 0.15)
        self.guess = self.rng.uniform(0.1, 0.25)
        self.days_offline = self.rng.randint(0, 15)
        # Apply forgetting
        if self.days_offline > 0:
            forget_rate = 0.01 * self.days_offline
            self.hidden_mastery = self.hidden_mastery * (1 - forget_rate) + 0.01 * forget_rate
        self.hidden_mastery = np.clip(self.hidden_mastery, 0.01, 0.99)
        # BKT tracking
        self.bkt = BayesianKnowledgeTracing(self.n_concepts)
        self.bkt.set_prerequisite_aware_priors(self.graph, self.concept_ids)
        # State tracking
        self.questions_done = 0
        self.recent_correct = []
        self.recent_times = []
        self.hint_used_count = 0
        self.streak = 0
        self.wrong_streak = 0
        self.last_session_days = self.days_offline
        return self._get_state()
    
    def _get_state(self):
        mastery = self.bkt.get_mastery()
        if len(self.recent_correct) > 0:
            ema_acc = np.mean(self.recent_correct[-10:])
        else:
            ema_acc = 0.5
        if len(self.recent_times) > 0:
            mean_t = np.mean(self.recent_times[-5:])
            z_time = (mean_t - 30) / 10.0
        else:
            z_time = 0.0
        hint_rate = self.hint_used_count / max(1, self.questions_done)
        fatigue = min(1.0, self.questions_done / 20.0)
        state = np.concatenate([
            mastery,
            [ema_acc, np.clip(z_time, -2, 2), hint_rate, fatigue, self.last_session_days / 14.0]
        ])
        return state
    
    def get_valid_actions(self):
        mastery = self.bkt.get_mastery()
        frontier = self.graph.get_frontier(mastery, 0.6, 0.9)
        actions = []
        # frontier actions
        for cid in frontier:
            for diff in [1, 2, 3]:
                actions.append((cid, diff))
        # review actions for forgotten
        for i, cid in enumerate(self.concept_ids):
            if mastery[i] < 0.5 and mastery[i] < self.hidden_mastery[i] - 0.1:
                for diff in [1, 2]:
                    actions.append((cid, diff))
        if not actions:
            # fallback to any not mastered
            for i, cid in enumerate(self.concept_ids):
                if mastery[i] < 0.9:
                    actions.append((cid, 1))
        # remove duplicates
        actions = list(set(actions))
        return actions
    
    def step(self, action):
        concept_id, difficulty = action
        if concept_id not in self.concept_ids:
            return self._get_state(), -0.1, False, {}
        cidx = self.concept_ids.index(concept_id)
        # Simulate response
        p_correct = self.bkt.predict_correct(cidx)
        # adjust by hidden params
        p_correct = p_correct * (1 - self.slip) + (1 - p_correct) * self.guess
        p_correct = np.clip(p_correct * (0.8 + 0.2 * self.learning_speed), 0.05, 0.95)
        correct = self.rng.random() < p_correct
        response_time = self.rng.normal(30 / self.learning_speed, 5)
        hint_used = self.rng.random() < 0.1
        # Update tracking
        self.questions_done += 1
        self.recent_correct.append(1.0 if correct else 0.0)
        self.recent_times.append(response_time)
        if hint_used:
            self.hint_used_count += 1
        if correct:
            self.streak += 1
            self.wrong_streak = 0
        else:
            self.streak = 0
            self.wrong_streak += 1
        # Update BKT
        mastery_before = self.bkt.mastery[cidx]
        self.bkt.update(cidx, correct, hint_used)
        mastery_after = self.bkt.mastery[cidx]
        mastery_gain = mastery_after - mastery_before
        # Reward
        reward = mastery_gain * 10.0
        reward -= 0.01  # per question
        if 0.55 <= p_correct <= 0.8:
            reward += 0.1  # ZPD bonus
        if self.wrong_streak >= 3:
            reward -= 0.2  # frustration penalty
        done = (np.mean(self.bkt.get_mastery()) >= 0.8) or (self.questions_done >= 50)
        info = {
            'correct': correct,
            'concept_id': concept_id,
            'mastery_gain': mastery_gain,
            'p_correct': p_correct
        }
        return self._get_state(), reward, done, info
