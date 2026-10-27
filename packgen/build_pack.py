import json
import os

def build_pack():
    template_path = os.path.join(os.path.dirname(__file__), 'template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Inject data
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    with open(os.path.join(data_path, 'concepts.json'), 'r', encoding='utf-8') as f:
        concepts = json.load(f)
    with open(os.path.join(data_path, 'questions.json'), 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Inject as JS
    data_script = f'<script>\nconst CONCEPTS = {json.dumps(concepts, ensure_ascii=False)};\nconst QUESTIONS = {json.dumps(questions, ensure_ascii=False)};\n</script>\n'
    html = html.replace('<script>', data_script + '<script>', 1)
    
    # Try to inject policy
    policy_path = os.path.join(os.path.dirname(__file__), 'policy.json')
    if os.path.exists(policy_path):
        with open(policy_path, 'r') as f:
            policy = json.load(f)
        policy_script = f'<script>\nconst POLICY = {json.dumps(policy)};\n</script>\n'
        html = html.replace(data_script + '<script>', data_script + policy_script + '<script>', 1)
    
    out_path = os.path.join(os.path.dirname(__file__), 'sikshasetu_pack.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    size_kb = os.path.getsize(out_path) / 1024
    print(f"Pack built: {out_path} ({size_kb:.2f} KB)")
    return out_path

if __name__ == '__main__':
    build_pack()
