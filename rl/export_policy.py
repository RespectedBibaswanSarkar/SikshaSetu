import json
import os

def export_policy():
    # Load trained model
    model_path = 'results/dqn_model.json'
    if not os.path.exists(model_path):
        print("No trained model found, creating a simple policy")
        policy = {
            'type': 'dqn',
            'weights': {
                'W1': [[0.1]*64 for _ in range(35)],
                'b1': [0]*64,
                'W2': [[0.1]*64 for _ in range(64)],
                'b2': [0]*64,
                'W3': [[0.1]*90 for _ in range(64)],
                'b3': [0]*90
            },
            'state_dim': 35,
            'action_dim': 90,
            'all_actions': [],
            'rounded': True,
            'concept_ids': []
        }
    else:
        with open(model_path, 'r') as f:
            model = json.load(f)
        policy = {
            'type': 'double_dqn',
            'weights': {
                'W1': [[round(x, 4) for x in row] for row in model['W1']],
                'b1': [round(x, 4) for x in model['b1']],
                'W2': [[round(x, 4) for x in row] for row in model['W2']],
                'b2': [round(x, 4) for x in model['b2']],
                'W3': [[round(x, 4) for x in row] for row in model['W3']],
                'b3': [round(x, 4) for x in model['b3']]
            },
            'state_dim': model['state_dim'],
            'action_dim': model['action_dim'],
            'all_actions': model['all_actions'],
            'concept_ids': model['concept_ids']
        }
    
    os.makedirs('packgen', exist_ok=True)
    out_path = 'packgen/policy.json'
    with open(out_path, 'w') as f:
        json.dump(policy, f)
    
    size_kb = os.path.getsize(out_path) / 1024
    print(f"Policy exported to {out_path} ({size_kb:.2f} KB)")
    return policy

if __name__ == '__main__':
    export_policy()
