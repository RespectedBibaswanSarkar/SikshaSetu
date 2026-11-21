import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge_graph import KnowledgeGraph
import networkx as nx

def test_graph_acyclic():
    g = KnowledgeGraph()
    assert nx.is_directed_acyclic_graph(g.graph)

def test_concept_count():
    g = KnowledgeGraph()
    assert len(g.concept_ids) == 30

def test_prerequisites():
    g = KnowledgeGraph()
    prereqs = g.get_prerequisites('NUM_02')
    assert 'NUM_01' in prereqs
