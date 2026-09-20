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


def test_question_list_filters_and_pagination():
    response = client.get("/questions", params={"exam": "JEE Main", "limit": 2, "offset": 0})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert len(body["questions"]) <= 2
    assert all(q["exam"] == "JEE Main" for q in body["questions"])
    assert all("correct_answer" not in q for q in body["questions"])


def test_chapter_filter():
    chapters = client.get("/chapters", params={"exam": "JEE Main", "subject": "Physics"}).json()["chapters"]
    assert chapters
    response = client.get("/questions", params={"exam": "JEE Main", "subject": "Physics", "chapter": chapters[0], "limit": 100})
    assert response.status_code == 200
    assert all(q["chapter"] == chapters[0] for q in response.json()["questions"])


def test_test_creation_hides_answers_and_submission_is_one_time():
    created = client.post("/tests", json={"exam": "JEE Main", "question_count": 1, "duration_minutes": 5})
    assert created.status_code == 200
    body = created.json()
    assert body["question_count"] == 1
    assert "correct_answer" not in body["questions"][0]

    qid = body["questions"][0]["question_id"]
    submitted = client.post(f"/tests/{body['test_id']}/submit", json={"answers": {qid: ""}})
    assert submitted.status_code == 200
    assert submitted.json()["unanswered"] == 1

    again = client.post(f"/tests/{body['test_id']}/submit", json={"answers": {}})
    assert again.status_code == 409


def test_missing_solution_returns_404():
    response = client.get("/solutions/DOES-NOT-EXIST-2026-000001")
    assert response.status_code == 404

def test_topics_are_scoped_to_selected_chapter():
    chapters = client.get("/chapters", params={"exam": "JEE Main", "subject": "Physics"}).json()["chapters"]
    assert chapters
    topics = client.get(
        "/topics",
        params={"exam": "JEE Main", "subject": "Physics", "chapter": chapters[0]},
    )
    assert topics.status_code == 200
    values = topics.json()["topics"]
    assert values
    filtered = client.get(
        "/questions",
        params={
            "exam": "JEE Main",
            "subject": "Physics",
            "chapter": chapters[0],
            "topic": values[0],
            "limit": 100,
        },
    )
    assert filtered.status_code == 200
    assert all(q["topic"] == values[0] for q in filtered.json()["questions"])


def test_test_creation_honors_topic_and_question_type():
    chapters = client.get("/chapters", params={"exam": "JEE Main", "subject": "Physics"}).json()["chapters"]
    assert chapters
    topics = client.get(
        "/topics",
        params={"exam": "JEE Main", "subject": "Physics", "chapter": chapters[0]},
    ).json()["topics"]
    assert topics

    created = client.post(
        "/tests",
        json={
            "exam": "JEE Main",
            "subject": "Physics",
            "chapter": chapters[0],
            "topic": topics[0],
            "question_count": 1,
            "duration_minutes": 5,
        },
    )
    assert created.status_code == 200
    assert created.json()["question_count"] == 1
    assert created.json()["questions"][0]["topic"] == topics[0]
