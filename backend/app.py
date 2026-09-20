from __future__ import annotations

import json
import random
import re
import uuid
import math
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = ROOT / "data" / "questions"
SOLUTIONS_DIR = ROOT / "data" / "solutions"

app = FastAPI(title="Study Buddy API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEST_SESSIONS: dict[str, dict[str, Any]] = {}


def load_json(path: Path) -> Any:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "questions" in data:
        return data["questions"]
    return data


def load_questions() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for path in sorted(QUESTIONS_DIR.rglob("*.json")):
        if path.name in {"taxonomy.json", "question_index.json"}:
            continue
        data = load_json(path)
        if isinstance(data, list):
            questions.extend(q for q in data if isinstance(q, dict))
    return questions


def load_solutions() -> dict[str, dict[str, Any]]:
    solutions: dict[str, dict[str, Any]] = {}
    for path in sorted(SOLUTIONS_DIR.rglob("*.json")):
        data = load_json(path)
        if isinstance(data, list):
            for solution in data:
                if isinstance(solution, dict) and solution.get("question_id"):
                    solutions[solution["question_id"]] = solution
    return solutions


def normalize_answer(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("−", "-").replace("–", "-").replace("×", "*")
    text = re.sub(r"\\s+", "", text)
    text = re.sub(r"\\boption[-_ ]?([a-d])\\b", r"\\1", text)
    return text


def answers_match(submitted: Any, expected: Any, question: dict[str, Any]) -> bool:
    a = normalize_answer(submitted)
    b = normalize_answer(expected)
    if not a or not b:
        return False
    if a == b:
        return True

    # Numerical/integer answers commonly arrive with harmless formatting differences.
    if question.get("question_type") in {"Numerical", "Integer", "Grid-In"}:
        try:
            av = float(a)
            bv = float(b)
            return math.isclose(av, bv, rel_tol=1e-9, abs_tol=1e-9)
        except ValueError:
            pass
    return False


def public_question(question: dict[str, Any]) -> dict[str, Any]:
    # Never expose the answer key through normal practice/test question APIs.
    result = dict(question)
    result.pop("correct_answer", None)
    return result


def filter_questions(
    items: list[dict[str, Any]],
    exam: str | None = None,
    subject: str | None = None,
    chapter: str | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    question_type: str | None = None,
) -> list[dict[str, Any]]:
    filters = {
        "exam": exam,
        "subject": subject,
        "chapter": chapter,
        "topic": topic,
        "difficulty": difficulty,
        "question_type": question_type,
    }
    for key, value in filters.items():
        if value:
            items = [q for q in items if str(q.get(key, "")).lower() == value.lower()]
    return items


@app.get("/health")
def health() -> dict[str, Any]:
    questions = load_questions()
    return {"status": "ok", "question_count": len(questions), "api_version": "0.3.0"}


@app.get("/exams")
def exams() -> dict[str, list[str]]:
    values = sorted({q.get("exam", "") for q in load_questions() if q.get("exam")})
    return {"exams": values}


@app.get("/subjects")
def subjects(exam: str | None = None) -> dict[str, list[str]]:
    questions = load_questions()
    if exam:
        questions = [q for q in questions if q.get("exam", "").lower() == exam.lower()]
    values = sorted({q.get("subject", "") for q in questions if q.get("subject")})
    return {"subjects": values}


@app.get("/chapters")
def chapters(exam: str | None = None, subject: str | None = None) -> dict[str, list[str]]:
    questions = load_questions()
    if exam:
        questions = [q for q in questions if q.get("exam", "").lower() == exam.lower()]
    if subject:
        questions = [q for q in questions if q.get("subject", "").lower() == subject.lower()]
    values = sorted({q.get("chapter", "") for q in questions if q.get("chapter")})
    return {"chapters": values}


@app.get("/questions")
def questions(
    exam: str | None = None,
    subject: str | None = None,
    chapter: str | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    question_type: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    items = filter_questions(
        load_questions(), exam, subject, chapter, topic, difficulty, question_type
    )
    items.sort(key=lambda q: q.get("question_id", ""))
    total = len(items)
    page = items[offset : offset + limit]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "questions": [public_question(q) for q in page],
    }


class TestCreateRequest(BaseModel):
    exam: str
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    question_count: int = Field(default=10, ge=1, le=50)
    duration_minutes: int = Field(default=30, ge=1, le=180)


class TestSubmitRequest(BaseModel):
    answers: dict[str, str] = Field(default_factory=dict)


@app.post("/tests")
def create_test(request: TestCreateRequest) -> dict[str, Any]:
    candidates = filter_questions(
        load_questions(),
        request.exam,
        request.subject,
        request.chapter,
        difficulty=request.difficulty,
    )
    if not candidates:
        raise HTTPException(status_code=404, detail="No questions match these filters")
    if len(candidates) < request.question_count:
        question_count = len(candidates)
    else:
        question_count = request.question_count

    selected = random.sample(candidates, question_count)
    test_id = uuid.uuid4().hex
    TEST_SESSIONS[test_id] = {
        "question_ids": [q["question_id"] for q in selected],
        "duration_minutes": request.duration_minutes,
        "exam": request.exam,
        "submitted": False,
    }
    return {
        "test_id": test_id,
        "duration_minutes": request.duration_minutes,
        "question_count": question_count,
        "questions": [public_question(q) for q in selected],
    }


@app.get("/tests/{test_id}")
def get_test(test_id: str) -> dict[str, Any]:
    session = TEST_SESSIONS.get(test_id)
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    questions_by_id = {q["question_id"]: q for q in load_questions()}
    selected = [questions_by_id[qid] for qid in session["question_ids"] if qid in questions_by_id]
    return {
        "test_id": test_id,
        "duration_minutes": session["duration_minutes"],
        "question_count": len(selected),
        "submitted": session["submitted"],
        "questions": [public_question(q) for q in selected],
    }


@app.post("/tests/{test_id}/submit")
def submit_test(test_id: str, request: TestSubmitRequest) -> dict[str, Any]:
    session = TEST_SESSIONS.get(test_id)
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    if session["submitted"]:
        raise HTTPException(status_code=409, detail="Test already submitted")

    questions_by_id = {q["question_id"]: q for q in load_questions()}
    results = []
    score = 0
    correct = 0
    wrong = 0
    unanswered = 0

    for question_id in session["question_ids"]:
        question = questions_by_id.get(question_id)
        if not question:
            continue
        submitted = request.answers.get(question_id)
        expected = question.get("correct_answer")
        if submitted is None or submitted == "":
            status = "unanswered"
            unanswered += 1
        elif answers_match(submitted, expected, question):
            status = "correct"
            correct += 1
            score += question.get("marks", 0)
        else:
            status = "wrong"
            wrong += 1
            score -= question.get("negative_marks", 0)

        results.append({
            "question_id": question_id,
            "selected_answer": submitted,
            "correct_answer": expected,
            "status": status,
            "marks": question.get("marks", 0),
            "negative_marks": question.get("negative_marks", 0),
        })

    session["submitted"] = True
    return {
        "test_id": test_id,
        "score": score,
        "correct": correct,
        "wrong": wrong,
        "unanswered": unanswered,
        "total": len(results),
        "results": results,
    }


@app.get("/questions/{question_id}")
def question(question_id: str) -> dict[str, Any]:
    for item in load_questions():
        if item.get("question_id") == question_id:
            return public_question(item)
    raise HTTPException(status_code=404, detail="Question not found")


@app.get("/solutions/{question_id}")
def solution(question_id: str) -> dict[str, Any]:
    item = load_solutions().get(question_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Solution not found")
    return item


@app.get("/questions/{question_id}/solution")
def question_solution(question_id: str) -> dict[str, Any]:
    question_item = next((q for q in load_questions() if q.get("question_id") == question_id), None)
    if question_item is None:
        raise HTTPException(status_code=404, detail="Question not found")
    solution_item = load_solutions().get(question_id)
    if solution_item is None:
        raise HTTPException(status_code=404, detail="Solution not found")
    return {"question": public_question(question_item), "solution": solution_item}
