from fastapi.testclient import TestClient

from backend.app import app, answers_match

client = TestClient(app)


def test_health_and_question_count():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["question_count"] >= 100


def test_public_question_never_exposes_answer():
    response = client.get("/questions/JEE-MAIN-PHY-2026-000002")
    assert response.status_code == 200
    assert "correct_answer" not in response.json()


def test_solution_matches_question_id():
    response = client.get("/questions/JEE-MAIN-PHY-2026-000002/solution")
    assert response.status_code == 200
    body = response.json()
    assert body["question"]["question_id"] == "JEE-MAIN-PHY-2026-000002"
    assert body["solution"]["question_id"] == "JEE-MAIN-PHY-2026-000002"


def test_numeric_answer_matching():
    q = {"question_type": "Numerical"}
    assert answers_match("10", "10.0", q)
    assert answers_match(" 1e-2 ", "0.01", q)
    assert not answers_match("10", "11", q)


def test_unknown_question_returns_404():
    response = client.get("/questions/DOES-NOT-EXIST-2026-000001")
    assert response.status_code == 404
