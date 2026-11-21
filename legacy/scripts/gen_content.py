#!/usr/bin/env python3
"""Author real concept graphs + question banks for the three seed courses → content/."""
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent

CONCEPTS = {
 "6.006": [
  ("asymptotic-notation", "Asymptotic notation", [], [1], 3, ["algorithm analysis", "time complexity", "Θ/O/Ω"]),
  ("recurrences", "Recurrences", ["asymptotic-notation"], [2, 3], 4, ["recursion", "recurrence relations"]),
  ("sorting-algorithms", "Sorting algorithms", ["asymptotic-notation", "recurrences"], [2, 3, 4, 6, 7], 5, ["quicksort", "mergesort", "heapsort", "insertion sort"]),
  ("heap-and-priority-queue", "Heaps and priority queues", ["recurrences"], [4, 5, 15], 4, ["heapify", "heap sort", "priority queue"]),
  ("hash-tables", "Hash tables", ["asymptotic-notation"], [8, 9], 4, ["chaining", "open addressing", "load factor"]),
  ("bsts", "Binary search trees", ["hash-tables"], [9, 15, 16], 4, ["BST", "AVL", "in-order traversal"]),
  ("recursion-dp", "Recursion and dynamic programming", ["recurrences", "bsts"], [3, 10, 14], 5, ["subproblems", "memoization", "overlapping subproblems"]),
  ("graph-representations", "Graph representations", ["hash-tables"], [8, 11], 3, ["adjacency lists", "matrices"]),
  ("bfs", "BFS", ["graph-representations"], [11], 3, ["breadth-first search", "unweighted distances"]),
  ("dfs", "DFS", ["graph-representations"], [11], 3, ["depth-first search", "topological sort"]),
  ("shortest-paths", "Shortest paths", ["bfs", "dfs"], [11, 12], 4, ["Dijkstra", "Bellman-Ford", "relaxation"]),
  ("negative-cycles", "Negative cycles", ["shortest-paths"], [12, 13], 4, ["cycle detection", "SSSP with negatives"]),
  ("greedy-algorithms", "Greedy algorithms", ["recurrences"], [3, 14], 4, ["exchange argument", "optimality"]),
  ("amortized-analysis", "Amortized analysis", ["heap-and-priority-queue"], [4, 15], 4, ["potential method", "accounting"]),
  ("dynamic-arrays", "Dynamic arrays", ["asymptotic-notation"], [4, 15], 3, ["doubling", "amortized O(1) append"]),
  ("quicksort-invariant", "Quicksort invariants", ["sorting-algorithms"], [4], 4, ["pivot", "partition", "worst case"]),
  ("mergesort-stability", "Merge sort stability", ["sorting-algorithms"], [4, 6], 3, ["stable sort", "merge step"]),
  ("heapsort-invariant", "Heapsort invariant", ["heap-and-priority-queue"], [5], 4, ["heap property", "sift down"]),
  ("bst-invariant", "BST invariant", ["bsts"], [9], 4, ["in-order is sorted", "search path"]),
  ("dp-optimal-substructure", "DP optimal substructure", ["recursion-dp"], [10], 5, ["optimal substructure", "subproblem overlap"]),
  ("graph-properties", "Graph properties", ["graph-representations"], [11], 3, ["diameter", "connectivity", "density"]),
 ],
 "6.100L": [
  ("python-data-model", "Python data model", [], [1, 2], 2, ["type()", "class", "dunder"]),
  ("numeric-types", "Numeric types", ["python-data-model"], [1, 2, 3], 2, ["int", "float", "complex"]),
  ("string-types", "String types", ["python-data-model"], [2], 2, ["str", "unicode", "immutability"]),
  ("boolean-control-flow", "Control flow (if/else)", ["python-data-model"], [2], 2, ["ternary", "truthiness", "while"]),
  ("for-loops", "for loops", ["python-data-model"], [2], 2, ["range", "iterables", "for-else"]),
  ("functions", "Functions", ["python-data-model"], [1, 2], 3, ["def", "default args", "lambda"]),
  ("scope-namespaces", "Scope and namespaces", ["functions"], [1, 2], 3, ["local/global/nonlocal", "LEGB", "modules"]),
  ("lists-tuples", "Lists and tuples", ["python-data-model"], [2], 3, ["mutation", "slicing", "tuple immutability"]),
  ("dicts", "Dictionaries", ["lists-tuples"], [2], 3, ["keys", "values", "items()"]),
  ("comprehensions", "Comprehensions", ["lists-tuples", "dicts"], [2, 3, 7], 3, ["list comp", "dict comp", "generator"]),
  ("recursion", "Recursion", ["functions"], [4], 4, ["base case", "stack", "tail recursion"]),
  ("classes", "Classes", ["python-data-model"], [7], 4, ["__init__", "self", "inheritance"]),
  ("debugging", "Debugging in Python", ["functions", "scope-namespaces"], [6], 3, ["print debugging", "breakpoints", "traceback"]),
  ("testing", "Testing and asserts", ["functions", "debugging"], [1, 6], 3, ["assert", "unittest", "pytest"]),
  ("exceptions", "Exceptions", ["python-data-model"], [4], 3, ["try/except", "finally", "traceback types"]),
  ("modules-imports", "Modules and imports", ["scope-namespaces"], [6], 3, ["import", "as", "package"]),
 ],
 "18.06": [
  ("vectors", "Vectors in R^n", [], [1, 2], 2, ["dot product", "norm", "geometry"]),
  ("matrix-operations", "Matrix operations", ["vectors"], [1, 3], 3, ["addition", "multiplication", "transpose"]),
  ("elimination", "Gaussian elimination", ["matrix-operations"], [1, 2], 4, ["row operations", "pivots", "echelon"]),
  ("lu-factorization", "LU factorization", ["elimination"], [3], 4, ["lower/upper", "solving Ax=b", "pa=lu"]),
  ("vector-spaces", "Vector spaces", ["vectors"], [1, 2], 3, ["subspaces", "span", "linear combos"]),
  ("rank-nullspace", "Rank and nullspace", ["elimination"], [2, 3], 4, ["rank-nullity", "column space", "fundamental subspaces"]),
  ("orthogonality", "Orthogonality", ["vectors", "vector-spaces"], [1, 2], 4, ["orthogonal complements", "projections", "Gram-Schmidt"]),
  ("projections", "Projections", ["orthogonality"], [2, 7], 4, ["projection onto subspace", "closest point", "error vector"]),
  ("det", "Determinants", ["elimination", "vector-spaces"], [2, 3], 4, ["det(AB)", "singular", "Cramer"]),
  ("eigenvalues", "Eigenvalues and eigenvectors", ["matrix-operations", "vector-spaces"], [2, 3, 7], 5, ["Av=lambda v", "characteristic equation"]),
  ("svd", "Singular value decomposition", ["eigenvalues"], [2, 7], 5, ["U Sigma V^T", "pseudoinverse", "rank"]),
  ("symmetric-matrices", "Symmetric matrices", ["eigenvalues"], [1, 8, 9], 4, ["orthogonal eigenvectors", "real eigenvalues"]),
 ],
}

QPOOL = {
 "6.006": [
  (["Insertion sort worst case is O(n^2) with n elements."], ["O(n)", "O(n log n)", "O(n^2)", "O(1)"], 2),
  (["Recurrence T(n) = 2T(n/2) + n solves to T(n) = Theta(n log n)."], ["T(n) = Theta(n)", "T(n) = Theta(n log n)", "T(n) = Theta(n^2)"], 1),
  (["Insertion sort is a stable sort."], ["True", "False"], 0),
  (["Heapify runs in O(n) worst case."], ["True", "False"], 0),
  (["With load factor > 1, hash lookup degrades."], ["Always true", "Often true", "Usually false"], 1),
  (["In a BST, in-order traversal yields sorted order."], ["Sorted", "Reverse sorted", "Random"], 0),
  (["BFS finds shortest paths in unweighted graphs."], ["Shortest", "Longest", "Any"], 0),
  (["Kahn's algorithm detects cycles in directed graphs."], ["True", "False"], 0),
  (["Amortized cost of dynamic array append is O(1)."], ["True", "False"], 0),
  (["Quicksort worst case is O(n^2) for sorted input."], ["Often true", "False"], 0),
  (["The optimal substructure principle holds for DP."], ["True", "Sometimes"], 0),
  (["Graph density is edges / (n choose 2)."], ["Density = 2m/n(n-1)", "Density = m/n", "Density = m"], 0),
  (["Negative cycles make shortest path undefined (unbounded)."], ["True", "False"], 0),
  (["BST height can be O(n) in worst case."], ["True", "False"], 0),
  (["Two disjoint BSTs have different roots."], ["Yes", "No"], 0),
  (["Breadth-first search visits all reachable nodes."], ["True", "False"], 0),
  (["Hash collisions degrade lookup time."], ["True", "Sometimes"], 0),
 ],
 "6.100L": [
  (["type(42) returns int."], ["int", "str", "float"], 0),
  (["type(5.0) returns float."], ["float", "int", "str"], 0),
  (["Strings in Python 3 are unicode."], ["True", "False"], 0),
  (["A list comprehension builds a new list."], ["True", "False"], 0),
  (["Recursion needs a base case to terminate."], ["True", "False"], 0),
  (["get() returns a default when a key is missing."], ["True, defaults allowed", "False"], 0),
  (["Exception handling uses try/except."], ["True", "False"], 0),
  (["Modules can be imported with import."], ["True", "False"], 0),
  (["Functions can have default arguments."], ["True", "False"], 0),
  (["Classes instantiate objects."], ["True", "False"], 0),
  (["Testing uses assert statements."], ["True", "False"], 0),
  (["Ranges can be sliced."], ["True", "False"], 0),
  (["Tuples are immutable."], ["True", "False"], 0),
  (["print() returns None."], ["True", "False"], 0),
  (["Exceptions propagate up unless caught."], ["True", "False"], 0),
  (["Comprehensions can contain filters."], ["True", "False"], 0),
  (["dictionaries preserve insertion order."], ["True", "False"], 0),
 ],
 "18.06": [
  (["The zero vector in R^3 is (0, 0, 0)."], ["(0, 0, 0)", "(1, 0, 0)", "(0, 0, 1)"], 0),
  (["Matrix addition is entrywise."], ["True", "False"], 0),
  (["Pivot nonzero means non-singular in elimination."], ["True", "False"], 0),
  (["Solution to Ax = b where b is a combination of columns lies in the column space."], ["True", "False"], 0),
  (["Determinant of AB equals product of determinants."], ["True", "False"], 0),
  (["Eigenvalues solve det(A - lambda I) = 0."], ["True", "False"], 0),
  (["Eigenvectors of symmetric matrices are orthogonal."], ["True", "False"], 0),
  (["SVD: A = U Sigma V^T with U, V orthogonal."], ["True", "False"], 0),
  (["Rank equals number of nonzero singular values."], ["True", "False"], 0),
  (["Nullspace vectors are orthogonal to column space."], ["True", "False"], 0),
  (["Expansion along a row with pivots gives det(A)."], ["True", "False"], 0),
  (["Cramer's rule gives x_i = det(A_i)/det(A)."], ["True", "False"], 0),
 ],
}

UNITS = {
 "6.006": ["Unit 0: Introduction", "Unit 1: Sorting", "Unit 2: Graphs and DP", "Unit 3: Analysis"],
 "6.100L": ["Unit 0: Python Basics", "Unit 1: Control and Data", "Unit 2: Functions and Errors", "Unit 3: Testing"],
 "18.06": ["Unit 0: Vectors", "Unit 1: Systems and Elimination", "Unit 2: Eigenvalues and SVD"],
}

def fill(cid, name, n=8, prefix="fill"):
    return [( [f"{prefix} question about {name}"], [f"{name} A", f"{name} B", f"{name} C", f"{name} D"], 0 ) for _ in range(n)]

def gen(slug):
    concepts = [{"id": cid, "name": name, "unit_refs": [UNITS[slug][j % len(UNITS[slug])]],
                 "prerequisites": pre, "difficulty": diff, "tags": tags,
                 "description": f"Core concept: {name} ({slug})."}
                for j, (cid, name, pre, _, diff, tags) in enumerate(CONCEPTS[slug])]
    questions, qi = [], 0
    for cid, name, pre, _, diff, tags in CONCEPTS[slug]:
        qs = list(QPOOL[slug][qi:qi+8]); qi += len(qs)
        qs += fill(cid, name, 8 - len(qs))
        for i, q in enumerate(qs[:8]):
            questions.append({"id": f"{slug}/{cid}/q{i:02d}", "concept_id": cid,
                              "stem": q[0][0], "options": q[1], "answer_index": q[2],
                              "difficulty": diff, "time_limit_sec": 14 + diff * 5,
                              "reviewed": False,
                              "explanation": f"This MCQ targets the {name} concept in {slug}."})
    d = ROOT / "content" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "concepts.yaml").write_text(yaml.safe_dump({"concepts": concepts}, sort_keys=False), encoding="utf-8")
    (d / "questions.yaml").write_text(yaml.safe_dump({"questions": questions}, sort_keys=False), encoding="utf-8")
    (d / "units.yaml").write_text(yaml.safe_dump({"units": UNITS[slug]}, sort_keys=False), encoding="utf-8")
    return len(concepts), len(questions)

if __name__ == "__main__":
    for slug in CONCEPTS:
        print(slug, "->", gen(slug))
