import numpy as np

class BayesianKnowledgeTracing:
    def __init__(self, n_concepts, p_init=0.1, p_transit=0.1, p_slip=0.1, p_guess=0.2):
        self.n_concepts = n_concepts
        self.p_init = p_init
        self.p_transit = p_transit
        self.p_slip = p_slip
        self.p_guess = p_guess
        self.mastery = np.ones(n_concepts) * p_init
    
    def set_prerequisite_aware_priors(self, graph, concept_ids):
        topo = graph.get_topo_order()
        mastery = np.ones(self.n_concepts) * 0.05
        for cid in topo:
            idx = concept_ids.index(cid)
            prereqs = graph.get_prerequisites(cid)
            if not prereqs:
                mastery[idx] = 0.1
            else:
                # weak prerequisite lowers prior
                min_prereq = float('inf')
                for p in prereqs:
                    pidx = concept_ids.index(p)
                    if mastery[pidx] < min_prereq:
                        min_prereq = mastery[pidx]
                mastery[idx] = max(0.05, min_prereq * 0.3)
        self.mastery = mastery
        return self.mastery
    
    def update(self, concept_idx, correct, hint_used=False):
        p_learned = self.mastery[concept_idx]
        if correct:
            p_correct_given_learned = 1 - self.p_slip
            p_correct_given_not_learned = self.p_guess
            p_correct = p_learned * p_correct_given_learned + (1 - p_learned) * p_correct_given_not_learned
            p_learned_given_correct = (p_learned * p_correct_given_learned) / p_correct if p_correct > 0 else p_learned
            p_learned_new = p_learned_given_correct + (1 - p_learned_given_correct) * self.p_transit
        else:
            p_incorrect_given_learned = self.p_slip
            p_incorrect_given_not_learned = 1 - self.p_guess
            p_incorrect = p_learned * p_incorrect_given_learned + (1 - p_learned) * p_incorrect_given_not_learned
            p_learned_given_incorrect = (p_learned * p_incorrect_given_learned) / p_incorrect if p_incorrect > 0 else p_learned
            p_learned_new = p_learned_given_incorrect + (1 - p_learned_given_incorrect) * self.p_transit
        if hint_used:
            p_learned_new = min(0.99, p_learned_new * 1.05)
        self.mastery[concept_idx] = np.clip(p_learned_new, 0.0, 0.99)
        return self.mastery[concept_idx]
    
    def get_mastery(self):
        return self.mastery.copy()
    
    def predict_correct(self, concept_idx):
        p_learned = self.mastery[concept_idx]
        return p_learned * (1 - self.p_slip) + (1 - p_learned) * self.p_guess
