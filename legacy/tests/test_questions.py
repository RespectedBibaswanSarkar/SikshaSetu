import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

def test_questions_exist():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'questions.json')
    with open(path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    assert len(questions) == 30

def test_min_questions():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'questions.json')
    with open(path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    for cid, qs in questions.items():
        assert len(qs) >= 8
