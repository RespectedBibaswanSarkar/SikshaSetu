import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bkt import BayesianKnowledgeTracing
from core.knowledge_graph import KnowledgeGraph

def test_bkt_init():
    bkt = BayesianKnowledgeTracing(30)
    assert len(bkt.mastery) == 30

def test_prerequisite_aware_priors():
    g = KnowledgeGraph()
    bkt = BayesianKnowledgeTracing(30)
    mastery = bkt.set_prerequisite_aware_priors(g, g.concept_ids)
    assert mastery[g.concept_ids.index('NUM_01')] > mastery[g.concept_ids.index('FRAC_02')]

def test_update():
    bkt = BayesianKnowledgeTracing(30)
    before = bkt.mastery[0]
    bkt.update(0, True)
    after = bkt.mastery[0]
    assert after >= before
