import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl.env import SikshaSetuEnv

def test_env_reset():
    env = SikshaSetuEnv(seed=42)
    state = env.reset()
    assert len(state) == 35

def test_env_step():
    env = SikshaSetuEnv(seed=42)
    env.reset()
    valid = env.get_valid_actions()
    assert len(valid) > 0
    action = valid[0]
    state, reward, done, info = env.step(action)
    assert 'correct' in info
