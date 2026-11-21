import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.code import encode_mastery, decode_mastery
import numpy as np

def test_code_roundtrip():
    mastery = np.random.RandomState(42).random(30).tolist()
    code = encode_mastery(mastery)
    decoded = decode_mastery(code)
    assert decoded['valid'] == True
    diff = np.mean(np.abs(np.array(mastery) - np.array(decoded['mastery'])))
    assert diff < 0.15

def test_code_checksum():
    mastery = [0.5] * 30
    code = encode_mastery(mastery)
    bad_code = code[:-2] + 'XX'
    decoded = decode_mastery(bad_code)
    assert decoded['valid'] == False
