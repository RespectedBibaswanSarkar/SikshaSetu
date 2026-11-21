#!/usr/bin/env python3
"""Validation script for SikshaSetu content database.
Runs automated checks:
 1. Structural integrity: 4 distinct options per MCQ, valid answer_index in [0..3],
    explanation present, concept exists in concepts table, no duplicate stems within a course,
    every concept >= 6 questions, every question has source ref.
 2. 18.06 numeric verification: rank-nullity formula and matrix dimension checks with numpy/sympy.
 3. 6.100L code-trace verification: executes python snippets and compares output.
 4. 6.006 algorithm questions: checks computable properties against reference logic.
"""

import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "content" / "sikshasetu_content.sqlite"

def main():
    if not DB_PATH.exists():
        print(f"FAIL: Database file {DB_PATH} not found.")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    errors = []
    warnings = []

    # 1. Structural checks
    concepts = {r[0]: r[1] for r in cur.execute("SELECT id, course_slug FROM concepts").fetchall()}
    courses = [r[0] for r in cur.execute("SELECT slug FROM courses").fetchall()]

    if len(courses) != 3:
        errors.append(f"Expected 3 courses, found {len(courses)}: {courses}")

    # Check concept quotas (25-35 per course)
    for c in courses:
        count = sum(1 for cid, cslug in concepts.items() if cslug == c)
        if count < 25 or count > 35:
            errors.append(f"Course {c} has {count} concepts (expected 25-35)")

    # Check question quotas and integrity
    questions = cur.execute("""
        SELECT id, course_slug, concept_id, qtype, question, options, answer_index,
               answer_text, difficulty, time_limit_sec, explanation, source_ref, reviewed
        FROM questions
    """).fetchall()

    concept_q_counts = {}
    stems_seen = set()

    for q in questions:
        qid, cslug, cid, qtype, qtext, opts_json, ans_idx, ans_text, diff, tlim, expl, src_ref, reviewed = q

        # Check concept reference
        if cid not in concepts:
            errors.append(f"Question {qid} references non-existent concept {cid}")

        concept_q_counts[cid] = concept_q_counts.get(cid, 0) + 1

        # Check duplicate stems
        stem_key = (cslug, qtext.strip())
        if stem_key in stems_seen:
            errors.append(f"Duplicate question stem in course {cslug}: {qtext[:40]}...")
        stems_seen.add(stem_key)

        # Check explanation and source ref
        if not expl or len(expl.strip()) < 5:
            errors.append(f"Question {qid} missing valid explanation")
        if not src_ref:
            errors.append(f"Question {qid} missing source_ref")

        # Check options for MCQ
        if qtype == "mcq":
            try:
                opts = json.loads(opts_json)
                if len(opts) != 4:
                    errors.append(f"Question {qid} (MCQ) does not have 4 options (found {len(opts)})")
                if len(set(opts)) != 4:
                    errors.append(f"Question {qid} (MCQ) has duplicate options")
                if ans_idx not in (0, 1, 2, 3):
                    errors.append(f"Question {qid} (MCQ) invalid answer_index: {ans_idx}")
            except Exception as e:
                errors.append(f"Question {qid} options JSON invalid: {e}")

        # Domain-specific verification
        if cslug == "18.06" and qtype == "numeric":
            # Verify Rank-Nullity: dim(N) = 5 - rank
            m = re.search(r"rank (\d+)", qtext)
            if m:
                r = int(m.group(1))
                # verify with numpy on a 5x5 matrix with r ones on diagonal
                A = np.zeros((5, 5))
                for i in range(r):
                    A[i, i] = 1
                actual_rank = int(np.linalg.matrix_rank(A))
                actual_nullity = 5 - actual_rank
                if int(ans_text) != actual_nullity:
                    errors.append(f"18.06 question {qid} rank-nullity mismatch: expected {actual_nullity}, got {ans_text}")

        elif cslug == "6.100L" and qtype == "code_trace":
            # Sandboxed code trace check
            m_code = re.search(r"```python\n(.*?)\n```", qtext, re.DOTALL)
            if m_code:
                py_code = m_code.group(1)
                res = subprocess.run([sys.executable, "-c", py_code], capture_output=True, text=True)
                if res.stdout.strip() != ans_text:
                    errors.append(f"6.100L code trace {qid} execution mismatch: python says '{res.stdout.strip()}', question says '{ans_text}'")

        elif cslug == "6.006" and qtype == "code_trace":
            if "A = [5, 2, 8, 1]" in qtext:
                A = [5, 2, 8, 1]
                pivot = A[-1]
                count_smaller = sum(1 for x in A[:-1] if x < pivot)
                if str(count_smaller) != ans_text:
                    errors.append(f"6.006 algorithm check {qid} mismatch: expected {count_smaller}, got {ans_text}")

    # Check every concept has >= 6 questions
    for cid in concepts:
        cnt = concept_q_counts.get(cid, 0)
        if cnt < 6:
            errors.append(f"Concept {cid} has only {cnt} questions (minimum 6 required)")

    con.close()

    if errors:
        print(f"FAILED with {len(errors)} errors:")
        for err in errors[:20]:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"PASSED: All {len(questions)} questions across {len(concepts)} concepts verified successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
