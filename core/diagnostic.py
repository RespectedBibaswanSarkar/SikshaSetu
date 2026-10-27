import numpy as np
from .knowledge_graph import KnowledgeGraph
from .bkt import BayesianKnowledgeTracing

class AdaptiveDiagnostic:
    def __init__(self, graph, question_bank, n_questions=10):
        self.graph = graph
        self.question_bank = question_bank
        self.n_questions = n_questions
        self.concept_ids = graph.concept_ids
        self.n_concepts = graph.n_concepts
    
    def select_questions(self, bkt):
        selected = []
        used_concepts = set()
        # Start with concepts having highest uncertainty
        for _ in range(self.n_questions):
            best_concept = None
            best_info = -1
            for i, cid in enumerate(self.concept_ids):
                if cid in used_concepts:
                    continue
                p = bkt.mastery[i]
                # information gain approximation
                info = -p * np.log2(p + 1e-10) - (1-p) * np.log2(1-p + 1e-10)
                if info > best_info:
                    best_info = info
                    best_concept = cid
            if best_concept is None:
                break
            used_concepts.add(best_concept)
            # pick a question
            if best_concept in self.question_bank:
                qlist = self.question_bank[best_concept]
                if qlist:
                    # pick medium difficulty
                    med = [q for q in qlist if q.get('difficulty', 2) == 2]
                    if not med:
                        med = qlist
                    q = np.random.choice(med)
                    selected.append({
                        'concept_id': best_concept,
                        'question': q
                    })
        return selected
    
    def run_diagnostic(self, answers):
        bkt = BayesianKnowledgeTracing(self.n_concepts)
        bkt.set_prerequisite_aware_priors(self.graph, self.concept_ids)
        # propagate evidence
        for ans in answers:
            cid = ans['concept_id']
            correct = ans['correct']
            if cid in self.concept_ids:
                idx = self.concept_ids.index(cid)
                bkt.update(idx, correct)
                # propagate to prerequisites (update them too based on evidence)
                for p in self.graph.get_prerequisites(cid):
                    pidx = self.concept_ids.index(p)
                    # small propagation
                    if correct:
                        bkt.mastery[pidx] = min(0.99, bkt.mastery[pidx] + 0.02)
                    else:
                        bkt.mastery[pidx] = max(0.01, bkt.mastery[pidx] - 0.01)
                # propagate to dependants
                for d in self.graph.get_dependants(cid):
                    didx = self.concept_ids.index(d)
                    if not correct:
                        bkt.mastery[didx] = max(0.01, bkt.mastery[didx] - 0.015)
        return bkt.get_mastery()
