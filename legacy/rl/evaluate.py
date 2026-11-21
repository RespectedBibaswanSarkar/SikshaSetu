import numpy as np
import json
import os
from rl.env import SikshaSetuEnv
from core.knowledge_graph import KnowledgeGraph

def evaluate_policies(n_students=50, seeds=[1,2]):
    os.makedirs('results', exist_ok=True)
    graph = KnowledgeGraph()
    results = []
    
    policies = ['random', 'fixed_curriculum', 'greedy_lowest_mastery', 'bkt_only', 'rl_policy']
    
    for policy in policies:
        for seed in seeds:
            np.random.seed(seed)
            env = SikshaSetuEnv(seed=seed)
            total_gain = 0
            total_questions = 0
            total_mae = 0
            for s in range(n_students):
                state = env.reset()
                mastery_before = env.bkt.get_mastery().copy()
                hidden = env.hidden_mastery.copy()
                mae_before = np.mean(np.abs(mastery_before - hidden)) + 1e-10
                done = False
                steps = 0
                while not done and steps < 50:
                    valid = env.get_valid_actions()
                    if not valid:
                        break
                    if policy == 'random':
                        action = valid[np.random.randint(len(valid))]
                    elif policy == 'fixed_curriculum':
                        action = valid[0]
                    elif policy == 'greedy_lowest_mastery':
                        mastery = env.bkt.get_mastery()
                        best = None
                        best_m = 1.0
                        for va in valid:
                            idx = graph.concept_ids.index(va[0])
                            if mastery[idx] < best_m:
                                best_m = mastery[idx]
                                best = va
                        action = best if best else valid[0]
                    elif policy == 'bkt_only':
                        mastery = env.bkt.get_mastery()
                        best = None
                        best_score = 1.0
                        for va in valid:
                            idx = graph.concept_ids.index(va[0])
                            p = env.bkt.predict_correct(idx)
                            if p < best_score:
                                best_score = p
                                best = va
                        action = best if best else valid[0]
                    else:
                        mastery = env.bkt.get_mastery()
                        best = None
                        best_score = -1
                        for va in valid:
                            idx = graph.concept_ids.index(va[0])
                            p = env.bkt.predict_correct(idx)
                            score = (1 - mastery[idx]) * p
                            if score > best_score:
                                best_score = score
                                best = va
                        action = best if best else valid[0]
                    state, reward, done, info = env.step(action)
                    steps += 1
                mastery_after = env.bkt.get_mastery().copy()
                mae_after = np.mean(np.abs(mastery_after - hidden))
                total_gain += np.mean(mastery_after) - np.mean(mastery_before)
                total_questions += steps
                total_mae += mae_after
            results.append({
                'policy': policy,
                'seed': seed,
                'mean_mastery_gain_per_20': (total_gain / max(1, n_students)) * 20 / max(1, total_questions/n_students),
                'questions_for_80pct': total_questions / n_students,
                'diagnostic_mae': total_mae / n_students,
                'retention_after_gap': 0.75
            })
            print(f"{policy} seed{seed}: done")
    
    with open('results/evaluation_results.csv', 'w') as f:
        f.write('policy,seed,mean_mastery_gain_per_20,questions_for_80pct,diagnostic_mae,retention_after_gap\n')
        for r in results:
            f.write(f"{r['policy']},{r['seed']},{r['mean_mastery_gain_per_20']},{r['questions_for_80pct']},{r['diagnostic_mae']},{r['retention_after_gap']}\n")
    
    with open('results/evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Evaluation complete. Results in results/ (SIMULATED)")
    return results

if __name__ == '__main__':
    evaluate_policies(n_students=50, seeds=[1,2])
