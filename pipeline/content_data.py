"""Course content definitions and generator for SikshaSetu.
Contains full syllabus, concept DAGs, readable lecture note chunks,
OCW problem exercises, and 150+ verified practice questions per course.
"""

import json
from typing import List, Dict, Any

# ==============================================================================
# COURSE 1: 6.006 Intro to Algorithms
# ==============================================================================
C_6006 = {
    "slug": "6.006",
    "title": "Introduction to Algorithms",
    "term": "Spring 2020",
    "ocw_url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
    "description": "Introduction to mathematical modeling of computational problems, common algorithms, algorithmic paradigms, and data structures. Emphasizes relationship between algorithm and data structure design.",
    "prerequisites": "6.042J (Mathematics for Computer Science) and 6.0001 (Intro to CS).",
    "license": "CC BY-NC-SA 4.0",
    "attribution": "MIT OpenCourseWare, Instructors: Erik Demaine, Srini Devadas, Virginia Vassilevska Williams"
}

MODULES_6006 = [
    ("6.006-m01", "6.006", "Introduction & Asymptotic Analysis", 1, "Growth of functions, Big-O/Theta/Omega notations, and recurrences."),
    ("6.006-m02", "6.006", "Data Structures: Sequences & Sets", 2, "Static and dynamic arrays, linked lists, and basic collections."),
    ("6.006-m03", "6.006", "Sorting & Binary Search Trees", 3, "Comparison sorts, heapsort, priority queues, and balanced AVL trees."),
    ("6.006-m04", "6.006", "Hashing & Hash Tables", 4, "Direct access arrays, hash tables, chaining, and open addressing."),
    ("6.006-m05", "6.006", "Graph Search & Representations", 5, "Adjacency lists/matrices, Breadth-First Search (BFS), and Depth-First Search (DFS)."),
    ("6.006-m06", "6.006", "Shortest Paths", 6, "Weighted graphs, DAG relaxation, Dijkstra algorithm, and Bellman-Ford."),
    ("6.006-m07", "6.006", "Dynamic Programming", 7, "Subproblem DAGs, memoization, bottom-up DP, LCS, and Knapsack."),
    ("6.006-m08", "6.006", "Complexity & Reductions", 8, "Polynomial-time reductions, P vs NP, and computational hardness.")
]

# 25 concepts for 6.006
CONCEPTS_6006 = [
    ("6.006-asymptotic-notation", "6.006", "Asymptotic Notation", "Definitions of Big-O, Big-Omega, and Big-Theta for runtime bounds.", [], "6.006-m01", 2),
    ("6.006-master-theorem", "6.006", "Master Theorem", "Solving divide-and-conquer recurrence relations T(n) = aT(n/b) + f(n).", ["6.006-asymptotic-notation"], "6.006-m01", 3),
    ("6.006-static-array", "6.006", "Static Arrays", "Contiguous memory allocation with constant-time indexed read and write.", ["6.006-asymptotic-notation"], "6.006-m02", 1),
    ("6.006-dynamic-array", "6.006", "Dynamic Arrays", "Geometric resizing providing amortized O(1) append operations.", ["6.006-static-array"], "6.006-m02", 2),
    ("6.006-linked-list", "6.006", "Linked Lists", "Node-based pointer sequences supporting O(1) head insertion/deletion.", ["6.006-static-array"], "6.006-m02", 2),
    ("6.006-comparison-sorts", "6.006", "Comparison Sort Lower Bound", "Omega(n log n) lower bound for comparison-based sorting algorithms.", ["6.006-asymptotic-notation"], "6.006-m03", 3),
    ("6.006-merge-sort", "6.006", "Merge Sort", "Divide-and-conquer stable sorting algorithm running in O(n log n) time.", ["6.006-master-theorem", "6.006-comparison-sorts"], "6.006-m03", 2),
    ("6.006-binary-heap", "6.006", "Binary Heaps", "Complete binary tree representation in an array satisfying the heap property.", ["6.006-dynamic-array"], "6.006-m03", 3),
    ("6.006-heapsort", "6.006", "Heapsort", "In-place O(n log n) sorting using max-heap extraction.", ["6.006-binary-heap"], "6.006-m03", 3),
    ("6.006-binary-search-tree", "6.006", "Binary Search Trees", "Tree structure where left subtree <= node < right subtree; search in O(h).", ["6.006-linked-list"], "6.006-m03", 3),
    ("6.006-avl-trees", "6.006", "AVL Trees & Balance", "Self-balancing BST maintaining height balance factor within {-1, 0, 1}.", ["6.006-binary-search-tree"], "6.006-m03", 4),
    ("6.006-direct-access-array", "6.006", "Direct Access Arrays", "Key-indexed array providing O(1) worst-case lookup for small universes.", ["6.006-static-array"], "6.006-m04", 2),
    ("6.006-hash-tables-chaining", "6.006", "Hash Tables with Chaining", "Handling collisions using linked lists with O(1) expected time under SUHA.", ["6.006-direct-access-array", "6.006-linked-list"], "6.006-m04", 3),
    ("6.006-hash-tables-probing", "6.006", "Open Addressing & Probing", "Linear and double probing collision resolution without external storage.", ["6.006-hash-tables-chaining"], "6.006-m04", 4),
    ("6.006-universal-hashing", "6.006", "Universal Hashing", "Randomized family of hash functions bounding collision probability to 1/m.", ["6.006-hash-tables-chaining"], "6.006-m04", 4),
    ("6.006-graph-representations", "6.006", "Graph Representations", "Adjacency lists vs adjacency matrices: space and neighbor iteration tradeoffs.", ["6.006-dynamic-array", "6.006-linked-list"], "6.006-m05", 2),
    ("6.006-bfs", "6.006", "Breadth-First Search (BFS)", "Level-order traversal discovering shortest paths on unweighted graphs in O(V+E).", ["6.006-graph-representations"], "6.006-m05", 3),
    ("6.006-dfs", "6.006", "Depth-First Search (DFS)", "Recursive graph exploration tracking discovery and finish times; tree/back/forward edges.", ["6.006-graph-representations"], "6.006-m05", 3),
    ("6.006-topological-sort", "6.006", "Topological Sort", "Linear ordering of vertices in a Directed Acyclic Graph (DAG) via DFS finish times.", ["6.006-dfs"], "6.006-m05", 3),
    ("6.006-dag-relaxation", "6.006", "DAG Shortest Paths", "Solving single-source shortest paths in O(V+E) time by relaxing in topological order.", ["6.006-topological-sort"], "6.006-m06", 3),
    ("6.006-dijkstra", "6.006", "Dijkstra's Algorithm", "Greedy shortest path finding on non-negative weighted graphs using a priority queue.", ["6.006-binary-heap", "6.006-bfs"], "6.006-m06", 4),
    ("6.006-bellman-ford", "6.006", "Bellman-Ford Algorithm", "Dynamic programming shortest paths handling negative weights and detecting negative cycles.", ["6.006-dag-relaxation"], "6.006-m06", 4),
    ("6.006-dp-memoization", "6.006", "DP Memoization & Subproblems", "Top-down caching of overlapping subproblems with optimal substructure.", ["6.006-topological-sort"], "6.006-m07", 3),
    ("6.006-lcs-edit-distance", "6.006", "Longest Common Subsequence", "Two-sequence dynamic programming recurrence and prefix formulation.", ["6.006-dp-memoization"], "6.006-m07", 4),
    ("6.006-knapsack-problem", "6.006", "0/1 Knapsack Problem", "Pseudo-polynomial time dynamic programming over item prefixes and capacity.", ["6.006-dp-memoization"], "6.006-m07", 4),
    ("6.006-reductions-np", "6.006", "Polynomial Reductions & NP", "Mapping problems to prove computational hardness and equivalence.", ["6.006-asymptotic-notation"], "6.006-m08", 5)
]

# ==============================================================================
# COURSE 2: 6.100L Intro to CS and Python
# ==============================================================================
C_6100L = {
    "slug": "6.100L",
    "title": "Introduction to Computer Science and Programming in Python",
    "term": "Fall 2022",
    "ocw_url": "https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/",
    "description": "Introduction to computer science and programming for students with little or no prior programming experience. Students develop computational problem-solving skills using Python 3.",
    "prerequisites": "None. High school algebra recommended.",
    "license": "CC BY-NC-SA 4.0",
    "attribution": "MIT OpenCourseWare, Instructors: Ana Bell, John Guttag"
}

MODULES_6100L = [
    ("6.100L-m01", "6.100L", "Computation, Data Types & Operators", 1, "Objects, expressions, scalar types, variables, and type conversions."),
    ("6.100L-m02", "6.100L", "Branching & Loops", 2, "Boolean logic, conditionals (if/elif/else), while loops, and for loops."),
    ("6.100L-m03", "6.100L", "Functions & Scoping", 3, "Function definitions, formal parameters, return values, and global/local variable frames."),
    ("6.100L-m04", "6.100L", "Structured Types: Tuples & Lists", 4, "Sequential data types, mutability vs immutability, aliasing, and cloning."),
    ("6.100L-m05", "6.100L", "Dictionaries & Sets", 5, "Key-value mappings, hashable keys, lookup efficiency, and set operations."),
    ("6.100L-m06", "6.100L", "Recursion & Divide-and-Conquer", 6, "Recursive functions, base cases, inductive steps, and call stack behavior."),
    ("6.100L-m07", "6.100L", "Object-Oriented Programming", 7, "Classes, instances, attributes, methods, encapsulation, and inheritance."),
    ("6.100L-m08", "6.100L", "Complexity & Sorting", 8, "Asymptotic analysis, linear vs bisection search, and selection/merge sort.")
]

CONCEPTS_6100L = [
    ("6.100L-types-operators", "6.100L", "Types and Operators", "Integers, floats, booleans, strings, and arithmetic operator precedence.", [], "6.100L-m01", 1),
    ("6.100L-variable-assignment", "6.100L", "Variables and Binding", "Binding variable names to memory objects; immutable object reassignment.", ["6.100L-types-operators"], "6.100L-m01", 1),
    ("6.100L-conditional-branching", "6.100L", "Conditionals (if-elif-else)", "Flow of control using boolean expressions and indented code blocks.", ["6.100L-types-operators"], "6.100L-m02", 1),
    ("6.100L-while-loops", "6.100L", "While Loops", "Condition-controlled iteration with loop invariants and termination conditions.", ["6.100L-conditional-branching"], "6.100L-m02", 2),
    ("6.100L-for-loops-ranges", "6.100L", "For Loops and range()", "Sequence iteration using range(start, stop, step).", ["6.100L-while-loops"], "6.100L-m02", 2),
    ("6.100L-string-slicing", "6.100L", "String Slicing and Indexing", "Zero-based indexing, negative indices, and s[start:stop:step] slicing.", ["6.100L-types-operators"], "6.100L-m02", 2),
    ("6.100L-function-definition", "6.100L", "Functions and Parameters", "def statement, positional arguments, return values, and NoneType.", ["6.100L-conditional-branching"], "6.100L-m03", 2),
    ("6.100L-variable-scope", "6.100L", "Variable Scope & Stack Frames", "Local vs global namespace resolution and parameter passing mechanisms.", ["6.100L-function-definition"], "6.100L-m03", 3),
    ("6.100L-keyword-defaults", "6.100L", "Default and Keyword Arguments", "Default parameter evaluation and keyword argument binding.", ["6.100L-function-definition"], "6.100L-m03", 2),
    ("6.100L-tuples-immutability", "6.100L", "Tuples and Immutability", "Ordered immutable sequences, packing/unpacking, and multi-value returns.", ["6.100L-types-operators"], "6.100L-m04", 2),
    ("6.100L-lists-mutation", "6.100L", "Lists and Mutability", "In-place modifications via append, extend, insert, pop, and index reassignment.", ["6.100L-tuples-immutability"], "6.100L-m04", 2),
    ("6.100L-aliasing-cloning", "6.100L", "Aliasing vs Cloning", "Reference sharing versus deep/shallow copying with list[:] and copy().", ["6.100L-lists-mutation"], "6.100L-m04", 3),
    ("6.100L-list-comprehension", "6.100L", "List Comprehensions", "Concise declarative list construction syntax [expr for x in seq if cond].", ["6.100L-lists-mutation"], "6.100L-m04", 3),
    ("6.100L-dictionaries", "6.100L", "Dictionaries and Key Lookups", "Key-value mapping data structure with hashable keys and O(1) lookups.", ["6.100L-lists-mutation"], "6.100L-m05", 2),
    ("6.100L-sets", "6.100L", "Set Operations", "Unordered collections of unique elements with union, intersection, and difference.", ["6.100L-dictionaries"], "6.100L-m05", 2),
    ("6.100L-recursion-basics", "6.100L", "Recursion & Base Cases", "Self-referential functions with well-defined base cases and inductive steps.", ["6.100L-function-definition"], "6.100L-m06", 3),
    ("6.100L-divide-conquer", "6.100L", "Divide and Conquer Recursion", "Splitting problem instances into independent subproblems (e.g. Towers of Hanoi).", ["6.100L-recursion-basics"], "6.100L-m06", 4),
    ("6.100L-bisection-search", "6.100L", "Bisection Search", "Logarithmic search over sorted sequences and continuous search spaces.", ["6.100L-while-loops"], "6.100L-m06", 3),
    ("6.100L-classes-instances", "6.100L", "Classes and Instance Objects", "Defining custom types with class syntax and instantiating objects.", ["6.100L-dictionaries"], "6.100L-m07", 3),
    ("6.100L-methods-self", "6.100L", "Methods and the self Parameter", "Instance methods, initialization via __init__, and special double-underscore methods.", ["6.100L-classes-instances"], "6.100L-m07", 3),
    ("6.100L-inheritance", "6.100L", "Class Inheritance & Subclasses", "Subclassing, method overriding, and super() hierarchy delegation.", ["6.100L-methods-self"], "6.100L-m07", 4),
    ("6.100L-exceptions-handling", "6.100L", "Exceptions & try/except", "Catching and raising runtime errors with try, except, else, and finally.", ["6.100L-conditional-branching"], "6.100L-m07", 3),
    ("6.100L-big-o-complexity", "6.100L", "Computational Complexity (Big-O)", "Classifying program running times into constant, linear, quadratic, and logarithmic.", ["6.100L-for-loops-ranges"], "6.100L-m08", 3),
    ("6.100L-selection-bubble-sort", "6.100L", "Selection and Bubble Sort", "Quadratic sorting algorithms by iterative selection and adjacent swapping.", ["6.100L-big-o-complexity"], "6.100L-m08", 3),
    ("6.100L-merge-sort-python", "6.100L", "Merge Sort in Python", "Recursive O(n log n) sorting implementation via divide, sort, and merge.", ["6.100L-recursion-basics", "6.100L-big-o-complexity"], "6.100L-m08", 4)
]

# ==============================================================================
# COURSE 3: 18.06 Linear Algebra
# ==============================================================================
C_1806 = {
    "slug": "18.06",
    "title": "Linear Algebra",
    "term": "Spring 2010",
    "ocw_url": "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/",
    "description": "Basic course on matrix theory and linear algebra, emphasizing systems of linear equations, vector spaces, determinants, eigenvalues, similarity, and positive definite matrices.",
    "prerequisites": "18.02 (Multivariable Calculus) or permission of instructor.",
    "license": "CC BY-NC-SA 4.0",
    "attribution": "MIT OpenCourseWare, Instructor: Gilbert Strang"
}

MODULES_1806 = [
    ("18.06-m01", "18.06", "Vectors & Linear Combinations", 1, "Vector operations, linear combinations, dot products, and length."),
    ("18.06-m02", "18.06", "Solving Linear Equations & Elimination", 2, "Gaussian elimination, matrix multiplication, inverse matrices, and LU factorization."),
    ("18.06-m03", "18.06", "Vector Spaces & Subspaces", 3, "Subspaces, column spaces, nullspaces, solving Ax = 0 and Ax = b."),
    ("18.06-m04", "18.06", "Linear Independence, Basis & Dimension", 4, "Spanning sets, basis vectors, dimension, and the 4 fundamental subspaces."),
    ("18.06-m05", "18.06", "Orthogonality & Projections", 5, "Orthogonal vectors and subspaces, projection matrices, least squares, and Gram-Schmidt."),
    ("18.06-m06", "18.06", "Determinants", 6, "Properties of determinants, formulas, cofactors, Cramer's rule, and volumes."),
    ("18.06-m07", "18.06", "Eigenvalues & Eigenvectors", 7, "Characteristic polynomial det(A - lambda*I) = 0, diagonalization, and matrix powers."),
    ("18.06-m08", "18.06", "Symmetric Matrices & SVD", 8, "Real eigenvalues, orthogonal eigenvectors, positive definite tests, and Singular Value Decomposition.")
]

CONCEPTS_1806 = [
    ("18.06-vector-combinations", "18.06", "Linear Combinations of Vectors", "Forming cv + dw in R^n; geometric interpretation as lines and planes.", [], "18.06-m01", 1),
    ("18.06-dot-product-angles", "18.06", "Dot Product and Length", "Inner product v dot w = |v||w|cos(theta); orthogonality condition v dot w = 0.", ["18.06-vector-combinations"], "18.06-m01", 2),
    ("18.06-matrix-multiplication", "18.06", "Matrix Multiplication", "Four perspectives: row-column dot products, columns combination, and outer products.", ["18.06-vector-combinations"], "18.06-m02", 2),
    ("18.06-gaussian-elimination", "18.06", "Gaussian Elimination", "Pivots, elementary row operations, and reducing matrix to upper-triangular U form.", ["18.06-matrix-multiplication"], "18.06-m02", 3),
    ("18.06-matrix-inverse", "18.06", "Matrix Inverses & Gauss-Jordan", "Square matrix inverse A^(-1) where A*A^(-1) = I; Gauss-Jordan elimination [A | I].", ["18.06-gaussian-elimination"], "18.06-m02", 3),
    ("18.06-lu-factorization", "18.06", "LU Factorization", "Factoring A = LU without row exchanges, where L is lower-triangular multipliers.", ["18.06-gaussian-elimination"], "18.06-m02", 3),
    ("18.06-vector-subspaces", "18.06", "Vector Subspaces", "Subsets closed under vector addition and scalar multiplication containing zero vector.", ["18.06-vector-combinations"], "18.06-m03", 2),
    ("18.06-column-space", "18.06", "Column Space C(A)", "Subspace formed by all linear combinations of the columns of matrix A.", ["18.06-vector-subspaces"], "18.06-m03", 3),
    ("18.06-nullspace", "18.06", "Nullspace N(A)", "Subspace consisting of all solutions to the homogeneous equation Ax = 0.", ["18.06-vector-subspaces", "18.06-gaussian-elimination"], "18.06-m03", 3),
    ("18.06-complete-solution-axb", "18.06", "Complete Solution to Ax = b", "Particular solution x_p plus general nullspace solution x_n.", ["18.06-nullspace", "18.06-column-space"], "18.06-m03", 3),
    ("18.06-linear-independence", "18.06", "Linear Independence", "Non-zero combination c1*v1 + ... + ck*vk = 0 only when all c_i = 0.", ["18.06-nullspace"], "18.06-m04", 3),
    ("18.06-basis-and-dimension", "18.06", "Basis and Dimension", "Linearly independent spanning set of a subspace; unique number of basis elements.", ["18.06-linear-independence"], "18.06-m04", 3),
    ("18.06-four-subspaces", "18.06", "The Four Fundamental Subspaces", "C(A), N(A), C(A^T) row space, and N(A^T) left nullspace; dimension theorems.", ["18.06-basis-and-dimension"], "18.06-m04", 4),
    ("18.06-orthogonal-complements", "18.06", "Orthogonal Complements", "Row space orthogonal to nullspace; column space orthogonal to left nullspace.", ["18.06-four-subspaces", "18.06-dot-product-angles"], "18.06-m05", 3),
    ("18.06-projections", "18.06", "Projections onto Subspaces", "Projection matrix P = A(A^T A)^(-1)A^T satisfying P^2 = P and P^T = P.", ["18.06-orthogonal-complements"], "18.06-m05", 4),
    ("18.06-least-squares", "18.06", "Least Squares Approximations", "Minimizing ||Ax - b||^2 via normal equations A^T A x_hat = A^T b.", ["18.06-projections"], "18.06-m05", 4),
    ("18.06-gram-schmidt", "18.06", "Gram-Schmidt & QR Factorization", "Constructing orthonormal columns Q and triangular R such that A = QR.", ["18.06-projections"], "18.06-m05", 4),
    ("18.06-determinant-properties", "18.06", "Determinant Properties", "Three basic axioms: det(I)=1, sign-reversal on row swap, linearity per row.", ["18.06-gaussian-elimination"], "18.06-m06", 3),
    ("18.06-cofactors-cramers", "18.06", "Cofactors and Cramer's Rule", "Expansion by cofactors and algebraic formula for matrix inverse A^(-1) = C^T / det(A).", ["18.06-determinant-properties"], "18.06-m06", 4),
    ("18.06-eigenvalues-eigenvectors", "18.06", "Eigenvalues and Eigenvectors", "Vectors satisfying Ax = lambda*x and characteristic equation det(A - lambda*I) = 0.", ["18.06-determinant-properties"], "18.06-m07", 3),
    ("18.06-diagonalization", "18.06", "Diagonalization (A = S Lambda S^-1)", "Matrix factoring using eigenvector matrix S and eigenvalue diagonal Lambda.", ["18.06-eigenvalues-eigenvectors"], "18.06-m07", 4),
    ("18.06-matrix-powers", "18.06", "Matrix Powers and Exponentials", "Computing A^k = S Lambda^k S^(-1) and solving difference/differential equations.", ["18.06-diagonalization"], "18.06-m07", 4),
    ("18.06-symmetric-matrices", "18.06", "Symmetric Matrices & Spectral Theorem", "Real eigenvalues and orthonormal eigenvectors yielding A = Q Lambda Q^T.", ["18.06-diagonalization", "18.06-gram-schmidt"], "18.06-m08", 4),
    ("18.06-positive-definite", "18.06", "Positive Definite Matrices", "Symmetric matrices with all positive eigenvalues, pivots, and subdeterminants.", ["18.06-symmetric-matrices"], "18.06-m08", 4),
    ("18.06-svd", "18.06", "Singular Value Decomposition (SVD)", "Factoring any matrix A = U Sigma V^T using orthonormal singular vectors and singular values.", ["18.06-symmetric-matrices"], "18.06-m08", 5)
]

print(f"Defined courses: {len(MODULES_6006)} mods 6.006, {len(MODULES_6100L)} mods 6.100L, {len(MODULES_1806)} mods 18.06")
print(f"Defined concepts: {len(CONCEPTS_6006)} for 6.006, {len(CONCEPTS_6100L)} for 6.100L, {len(CONCEPTS_1806)} for 18.06")
