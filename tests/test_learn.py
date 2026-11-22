"""Backend acceptance tests: the dashboard must be derived from real answers."""
import itertools
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    import hub.db as hubdb
    monkeypatch.setattr(hubdb, "DB", tmp_path / "hub.db")
    from hub.main import app
    return TestClient(app)


def new_student(c, name="Test"):
    return c.post("/api/learn/students", json={"name": name}).json()["student_id"]


def answer(c, sid, qid, right):
    from hub.learn import content
    q = content()["questions"][qid]
    correct = q["options"][q["answer_index"]]
    wrong = next((o for o in q["options"] if o != correct), "zzz-wrong")
    return c.post(f"/api/learn/students/{sid}/answer",
                  json={"question_id": qid, "choice": correct if right else wrong, "seconds": 20}).json()


def concept_with_prereq():
    from hub.learn import content
    C = content()
    for cid, d in C["concepts"].items():
        if d["prerequisites"] and len(C["by_concept"][cid]) >= 4:
            p = d["prerequisites"][0]
            if len(C["by_concept"].get(p, [])) >= 4:
                return p, cid
    raise AssertionError("no concept with prerequisite")


def test_health_and_static_routes(client):
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/learn/courses").json()


def test_zero_state_is_really_zero(client):
    d = client.get(f"/api/learn/students/{new_student(client)}/dashboard").json()
    s = d["stats"]
    assert s["overall_progress"] == 0 and s["tests_taken"] == 0 and s["streak"] == 0
    assert s["accuracy"] is None and s["focus_score"] is None and s["study_hours"] == 0
    assert d["weak_areas"] == [] and d["learning_path"][0]["action"] == "diagnostic"
    assert all(c["progress"] == 0 for c in d["courses"])
    assert d["notifications"][0]["kind"] == "test_due"


def test_answers_change_everything_live(client):
    from hub.learn import content
    sid = new_student(client)
    A, B = concept_with_prereq()
    qa = itertools.cycle(content()["by_concept"][A])
    qb = itertools.cycle(content()["by_concept"][B])
    before = client.get(f"/api/learn/students/{sid}/dashboard").json()
    for _ in range(10):
        r = answer(client, sid, next(qa), True)
    mastery_a = r["concept"]["mastery_after"]
    assert mastery_a > 0.8
    for _ in range(6):
        r = answer(client, sid, next(qb), False)
    d = r["live"]
    assert d["stats"]["accuracy"] == 62  # 10/16
    assert d["stats"]["answered"] == 16 and d["stats"]["tests_taken"] == 0
    assert d["stats"]["overall_progress"] > before["stats"]["overall_progress"]
    assert d["stats"]["focus_score"] is not None
    weak_ids = [w["concept_id"] for w in d["weak_areas"]]
    assert B in weak_ids and A not in weak_ids
    assert d["learning_path"][0]["concept_id"] in (B, A) or d["learning_path"][0]["concept_id"]
    # recommendation should target the weak concept, not the one just mastered
    assert d["learning_path"][0]["concept_id"] != A
    # recover
    for _ in range(8):
        r = answer(client, sid, next(qb), True)
    d = client.get(f"/api/learn/students/{sid}/dashboard").json()
    assert B not in [w["concept_id"] for w in d["weak_areas"]]


def test_persistence_and_idempotency(client):
    from hub.learn import content
    sid = new_student(client)
    qid = next(iter(content()["questions"]))
    q = content()["questions"][qid]
    body = {"question_id": qid, "choice": q["options"][q["answer_index"]], "seconds": 5, "event_id": "dup-1"}
    client.post(f"/api/learn/students/{sid}/answer", json=body)
    r = client.post(f"/api/learn/students/{sid}/answer", json=body).json()
    assert r["duplicate"] is True
    assert client.get(f"/api/learn/students/{sid}/dashboard").json()["stats"]["answered"] == 1


def test_options_shuffled_and_answer_not_leaked(client):
    sid = new_student(client)
    q = client.get(f"/api/learn/students/{sid}/next").json()
    assert "answer_index" not in q and "correct_answer" not in q and len(q["options"]) >= 2


def test_diagnostic_finishes_after_12(client):
    sid = new_student(client)
    for i in range(12):
        q = client.get(f"/api/learn/students/{sid}/next?mode=diagnostic&course=6.006").json()
        assert not q.get("done")
        client.post(f"/api/learn/students/{sid}/answer",
                    json={"question_id": q["question_id"], "choice": q["options"][0], "seconds": 10, "ctx": "diagnostic"})
    assert client.get(f"/api/learn/students/{sid}/next?mode=diagnostic&course=6.006").json()["done"] is True


def test_mock_test_flow_counts_and_is_idempotent(client):
    sid = new_student(client)
    t = client.post(f"/api/learn/students/{sid}/tests?course=6.006").json()
    assert len(t["questions"]) == 15 and len({q["question_id"] for q in t["questions"]}) == 15
    answers = [{"question_id": q["question_id"], "choice": q["options"][0], "seconds": 15} for q in t["questions"]]
    r = client.post(f"/api/learn/students/{sid}/tests/{t['test_id']}/submit", json={"answers": answers}).json()
    assert r["total"] == 15 and r["dashboard"]["stats"]["tests_taken"] == 1
    r2 = client.post(f"/api/learn/students/{sid}/tests/{t['test_id']}/submit", json={"answers": answers}).json()
    assert r2["dashboard"]["stats"]["tests_taken"] == 1
    assert client.get(f"/api/learn/students/{sid}/tests").json()[0]["score_pct"] == r["score_pct"]


def test_analytics_and_reset(client):
    sid = new_student(client)
    q = client.get(f"/api/learn/students/{sid}/next").json()
    client.post(f"/api/learn/students/{sid}/answer", json={"question_id": q["question_id"], "choice": q["options"][0], "seconds": 8})
    a = client.get(f"/api/learn/students/{sid}/analytics").json()
    assert a["bandit_arms"] and a["theta_history"] and a["reward_history"] and a["by_day"]
    client.post(f"/api/learn/students/{sid}/reset")
    assert client.get(f"/api/learn/students/{sid}/dashboard").json()["stats"]["answered"] == 0


def test_admin_numbers_are_real_not_mockup(client):
    s = client.get("/api/admin/stats").json()
    assert s["students"] == 0 and s["active_users"] == 0
    sid = new_student(client)
    q = client.get(f"/api/learn/students/{sid}/next").json()
    client.post(f"/api/learn/students/{sid}/answer", json={"question_id": q["question_id"], "choice": q["options"][0], "seconds": 5})
    s = client.get("/api/admin/stats").json()
    assert s["students"] == 1 and s["active_users"] == 1
    assert client.get("/api/admin/analytics").json()[0]["answers"] == 1


def test_search_and_concept_page(client):
    from hub.learn import content
    cid = next(iter(content()["concepts"]))
    assert client.get(f"/api/learn/concepts/{cid}").json()["concept"]["id"] == cid
    assert isinstance(client.get("/api/learn/search?q=sorting").json(), list)
