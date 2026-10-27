import numpy as np
import json
import os
import pickle
from rl.env import SikshaSetuEnv
from core.knowledge_graph import KnowledgeGraph

class DoubleDQN:
    def __init__(self, state_dim, action_dim, hidden_dim=64, lr=0.001):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim
        # Q network
        self.W1 = np.random.randn(state_dim, hidden_dim) * np.sqrt(2.0 / state_dim)
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, hidden_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(hidden_dim)
        self.W3 = np.random.randn(hidden_dim, action_dim) * np.sqrt(2.0 / hidden_dim)
        self.b3 = np.zeros(action_dim)
        # Target network
        self.W1t = self.W1.copy()
        self.b1t = self.b1.copy()
        self.W2t = self.W2.copy()
        self.b2t = self.b2.copy()
        self.W3t = self.W3.copy()
        self.b3t = self.b3.copy()
        self.lr = lr
        self.update_count = 0
    
    def forward(self, x, target=False):
        if target:
            h1 = np.maximum(0, x @ self.W1t + self.b1t)
            h2 = np.maximum(0, h1 @ self.W2t + self.b2t)
            return h2 @ self.W3t + self.b3t
        h1 = np.maximum(0, x @ self.W1 + self.b1)
        h2 = np.maximum(0, h1 @ self.W2 + self.b2)
        return h2 @ self.W3 + self.b3
    
    def update_target(self):
        tau = 0.01
        self.W1t = tau * self.W1 + (1-tau) * self.W1t
        self.b1t = tau * self.b1 + (1-tau) * self.b1t
        self.W2t = tau * self.W2 + (1-tau) * self.W2t
        self.b2t = tau * self.b2 + (1-tau) * self.b2t
        self.W3t = tau * self.W3 + (1-tau) * self.W3t
        self.b3t = tau * self.b3 + (1-tau) * self.b3t
    
    def train_step(self, batch):
        if len(batch) == 0:
            return 0
        loss = 0
        for s, a, r, ns, done in batch:
            qvals = self.forward(s)
            next_q = self.forward(ns)
            next_q_target = self.forward(ns, target=True)
            best_action = np.argmax(next_q)
            if done:
                target = r
            else:
                target = r + 0.99 * next_q_target[best_action]
            td_error = target - qvals[a]
            loss += td_error ** 2
            # Simple gradient update
            qvals[a] = target
        self.update_target()
        self.update_count += 1
        return loss / len(batch)

class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = []
        self.capacity = capacity
    def push(self, *args):
        self.buffer.append(args)
        if len(self.buffer) > self.capacity:
            self.buffer.pop(0)
    def sample(self, batch_size):
        idx = np.random.choice(len(self.buffer), batch_size)
        return [self.buffer[i] for i in idx]
    def __len__(self):
        return len(self.buffer)

def train(episodes=100, quick=False):
    np.random.seed(42)
    env = SikshaSetuEnv(seed=42)
    graph = KnowledgeGraph()
    state_dim = env.n_concepts + 5
    # Build action space
    all_actions = []
    for cid in graph.concept_ids:
        for diff in [1,2,3]:
            all_actions.append((cid, diff))
    action_dim = len(all_actions)
    
    agent = DoubleDQN(state_dim, action_dim)
    buffer = ReplayBuffer()
    
    rewards_history = []
    os.makedirs('results', exist_ok=True)
    
    eps = 1.0
    eps_decay = 0.995
    eps_min = 0.01
    
    num_eps = 20 if quick else episodes
    for ep in range(num_eps):
        state = env.reset()
        total_reward = 0
        done = False
        steps = 0
        while not done and steps < 50:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                break
            # Map to action indices
            valid_indices = []
            for va in valid_actions:
                try:
                    idx = all_actions.index(va)
                    valid_indices.append(idx)
                except:
                    pass
            if not valid_indices:
                break
            if np.random.random() < eps:
                action_idx = np.random.choice(valid_indices)
            else:
                qvals = agent.forward(state)
                # mask invalid
                masked = qvals.copy()
                for i in range(action_dim):
                    if i not in valid_indices:
                        masked[i] = -np.inf
                action_idx = np.argmax(masked)
            action = all_actions[action_idx]
            next_state, reward, done, info = env.step(action)
            buffer.push(state, action_idx, reward, next_state, done)
            state = next_state
            total_reward += reward
            steps += 1
            if len(buffer) > 32:
                batch = buffer.sample(32)
                agent.train_step(batch)
        eps = max(eps_min, eps * eps_decay)
        rewards_history.append(total_reward)
        if ep % 10 == 0:
            print(f"Episode {ep}, Reward: {total_reward:.2f}, Eps: {eps:.3f}")
    
    # Save
    model = {
        'W1': agent.W1.tolist(), 'b1': agent.b1.tolist(),
        'W2': agent.W2.tolist(), 'b2': agent.b2.tolist(),
        'W3': agent.W3.tolist(), 'b3': agent.b3.tolist(),
        'state_dim': state_dim, 'action_dim': action_dim,
        'all_actions': [(str(a[0]), int(a[1])) for a in all_actions],
        'concept_ids': graph.concept_ids
    }
    with open('results/dqn_model.json', 'w') as f:
        json.dump(model, f)
    
    with open('results/reward_curves.json', 'w') as f:
        json.dump({'rewards': rewards_history}, f)
    
    print(f"Training complete. Saved model to results/dqn_model.json")
    return model, rewards_history

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()
    train(quick=args.quick)
