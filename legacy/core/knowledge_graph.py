import json
import os
import networkx as nx

class KnowledgeGraph:
    def __init__(self, data_path=None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'concepts.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            self.concepts_data = json.load(f)
        self.graph = nx.DiGraph()
        self.concepts = {}
        for c in self.concepts_data:
            self.concepts[c['id']] = c
            self.graph.add_node(c['id'])
        for c in self.concepts_data:
            for p in c.get('prerequisites', []):
                self.graph.add_edge(p, c['id'])
        self.concept_ids = [c['id'] for c in self.concepts_data]
        self.n_concepts = len(self.concept_ids)
        self._validate_acyclic()
    
    def _validate_acyclic(self):
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Concept graph must be a DAG")
    
    def get_prerequisites(self, concept_id):
        return list(self.graph.predecessors(concept_id))
    
    def get_dependants(self, concept_id):
        return list(self.graph.successors(concept_id))
    
    def get_frontier(self, mastery_vector, threshold=0.6, own_threshold=0.9):
        frontier = []
        for cid in self.concept_ids:
            idx = self.concept_ids.index(cid)
            if mastery_vector[idx] >= own_threshold:
                continue
            prereqs = self.get_prerequisites(cid)
            if not prereqs:
                frontier.append(cid)
                continue
            all_ok = True
            for p in prereqs:
                pidx = self.concept_ids.index(p)
                if mastery_vector[pidx] < threshold:
                    all_ok = False
                    break
            if all_ok:
                frontier.append(cid)
        return frontier
    
    def get_topo_order(self):
        return list(nx.topological_sort(self.graph))
    
    def to_dict(self):
        return {
            'concepts': self.concepts_data,
            'edges': [(u, v) for u, v in self.graph.edges()]
        }
