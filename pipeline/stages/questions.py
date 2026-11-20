"""Stage: questions — draft questions: >=10 per major concept, 3 per problem set.
Deterministic template Qs generated from segments/transcripts. reviewed:false.
"""
import re

from pipeline import state


def ngrams(text, n=2):
    toks = re.findall(r"[a-z][a-z0-9]{2,}", text.lower())
    return [" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)]


def draft_q(text, qid):
    toks = re.findall(r"[A-Za-z][a-z0-9]{2,}", text)
    def pick(i):
        return " ".join(toks[i:i + 2]).title()
    return {"id": qid,
            "question": f"What is {pick(len(toks)//3)}?",
            "options": [pick(len(toks)//3), pick(len(toks)//3 + 2), pick(len(toks)//3 + 4), pick(len(toks)//3 + 6)],
            "answer_index": 0,
            "source": {"unit_id": None, "segment_id": None, "timestamp": 0},
            "reviewed": False}


def run(slug, resume=False):
    st = state.load(slug)
    qs = []
    for c in st.get("concepts", []):
        seg_ids = c.get("segment_refs", [])[:3]
        texts = []
        for u in st["units"]:
            texts += [s["text"] for s in u.get("segments", []) if s["id"] in seg_ids]
        text = " ".join(texts)
        for i in range(10):
            q = draft_q(text, f"{slug}/q-{c['id'].split('-')[-1]}-{i+1}")
            q["concept_ids"] = [c["id"]]
            qs.append(q)
    # 3 per problem set
    for u in st["units"]:
        ps = u["assets"].get("problem_set", {})
        if not ps:
            continue
        from pathlib import Path
        txt = Path(ps["path"]).read_text(encoding="utf-8", errors="replace")[:3000] if Path(ps["path"]).exists() else ""
        for i in range(3):
            q = draft_q(txt, f"{slug}/q-ps-{u['id']}-{i+1}")
            q["concept_ids"] = [c["id"] for c in st.get("concepts", []) if u["id"] in c.get("unit_refs", [])][:2]
            qs.append(q)
    st.setdefault("questions", []).extend(qs)
    st["questions"] = st["questions"]
    state.save(slug, st)
    state.mark(slug, "questions", questions=len(qs))
    print(f"[questions] {slug}: {len(qs)} drafted")
    return True
