#!/usr/bin/env python3
"""Import Study Buddy questions and solutions from JSONL or JSON files.

The importer is intentionally conservative: it validates records, enforces
stable question IDs, and writes questions and solutions to separate exam files.
It never downloads or scrapes question content.

Usage examples:
  python scripts/import_questions.py --input incoming/questions.jsonl
  python scripts/import_questions.py --input incoming/questions.json --solutions incoming/solutions.json
  python scripts/import_questions.py --input incoming/questions.jsonl --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^[A-Z0-9-]+-[0-9]{4}-[0-9]{6}$")
ALLOWED_EXAMS = {"JEE Main", "JEE Advanced", "KCET", "MHT-CET", "BITSAT", "GAKAO", "SAT"}
ALLOWED_SUBJECTS = {"Physics", "Chemistry", "Mathematics", "SAT Math", "SAT Reading and Writing"}
ALLOWED_DIFFICULTIES = {"Easy", "Medium", "Hard"}
ALLOWED_TYPES = {"MCQ", "Multiple Correct", "Numerical", "Integer", "Assertion Reason", "Grid-In"}


def load_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        records = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        data = json.loads(text)
        records = data if isinstance(data, list) else data.get("questions", data.get("solutions", []))
    if not isinstance(records, list) or not all(isinstance(x, dict) for x in records):
        raise ValueError(f"{path}: expected a JSON array or JSONL objects")
    return records


def validate_question(q: dict[str, Any]) -> list[str]:
    required = ["question_id", "exam", "exam_year", "subject", "chapter", "topic", "difficulty", "question_type", "question_text", "correct_answer", "marks", "negative_marks", "source"]
    errors = [f"missing {field}" for field in required if field not in q]
    if errors:
        return errors
    if not isinstance(q["question_id"], str) or not ID_RE.fullmatch(q["question_id"]):
        errors.append("invalid question_id")
    if q["exam"] not in ALLOWED_EXAMS:
        errors.append("unsupported exam")
    if q["subject"] not in ALLOWED_SUBJECTS:
        errors.append("unsupported subject")
    if q["difficulty"] not in ALLOWED_DIFFICULTIES:
        errors.append("unsupported difficulty")
    if q["question_type"] not in ALLOWED_TYPES:
        errors.append("unsupported question_type")
    if not isinstance(q["exam_year"], int) or not 2000 <= q["exam_year"] <= 2100:
        errors.append("invalid exam_year")
    if not isinstance(q["question_text"], str) or not q["question_text"].strip():
        errors.append("empty question_text")
    if not isinstance(q["correct_answer"], str) or not q["correct_answer"].strip():
        errors.append("empty correct_answer")
    if not isinstance(q["negative_marks"], (int, float)) or q["negative_marks"] < 0:
        errors.append("invalid negative_marks")
    return errors


def validate_solution(s: dict[str, Any]) -> list[str]:
    required = ["question_id", "solution_text", "answer_explanation", "source"]
    errors = [f"missing {field}" for field in required if field not in s]
    if errors:
        return errors
    if not isinstance(s["question_id"], str) or not ID_RE.fullmatch(s["question_id"]):
        errors.append("invalid question_id")
    for field in ("solution_text", "answer_explanation", "source"):
        if not isinstance(s[field], str) or not s[field].strip():
            errors.append(f"empty {field}")
    return errors


def target_question_path(q: dict[str, Any]) -> Path:
    exam_map = {
        "JEE Main": "jee_main",
        "JEE Advanced": "jee_advanced",
        "KCET": "cet/kcet",
        "MHT-CET": "cet/mht_cet",
        "BITSAT": "bitsat",
        "GAKAO": "gakao",
        "SAT": "sat",
    }
    subject_map = {
        "Physics": "physics",
        "Chemistry": "chemistry",
        "Mathematics": "mathematics",
        "SAT Math": "sat_math",
        "SAT Reading and Writing": "sat_reading_writing",
    }
    return ROOT / "data" / "questions" / exam_map[q["exam"]] / f"{subject_map[q['subject']]}.json"


def target_solution_path(q: dict[str, Any]) -> Path:
    exam_map = {
        "JEE Main": "jee_main",
        "JEE Advanced": "jee_advanced",
        "KCET": "cet/kcet",
        "MHT-CET": "cet/mht_cet",
        "BITSAT": "bitsat",
        "GAKAO": "gakao",
        "SAT": "sat",
    }
    subject_map = {
        "Physics": "physics",
        "Chemistry": "chemistry",
        "Mathematics": "mathematics",
        "SAT Math": "sat_math",
        "SAT Reading and Writing": "sat_reading_writing",
    }
    return ROOT / "data" / "solutions" / exam_map[q["exam"]] / f"{subject_map[q['subject']]}.json"


def read_existing(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("questions", data.get("solutions", []))


def merge_records(records: list[dict[str, Any]], path: Path) -> int:
    existing = read_existing(path)
    ids = {r["question_id"] for r in existing}
    added = 0
    for record in records:
        if record["question_id"] in ids:
            raise ValueError(f"duplicate question_id {record['question_id']} in {path}")
        existing.append(record)
        ids.add(record["question_id"])
        added += 1
    existing.sort(key=lambda r: r["question_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return added


def main() -> int:
    parser = argparse.ArgumentParser(description="Import validated Study Buddy question/solution records")
    parser.add_argument("--input", required=True, type=Path, help="questions JSON/JSONL file")
    parser.add_argument("--solutions", type=Path, help="matching solutions JSON/JSONL file")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    questions = load_records(args.input)
    errors: list[str] = []
    seen: set[str] = set()
    for i, q in enumerate(questions, 1):
        errors.extend(f"question #{i}: {e}" for e in validate_question(q))
        qid = q.get("question_id")
        if qid in seen:
            errors.append(f"question #{i}: duplicate question_id {qid}")
        seen.add(qid)

    solutions: list[dict[str, Any]] = []
    if args.solutions:
        solutions = load_records(args.solutions)
        solution_ids: set[str] = set()
        for i, s in enumerate(solutions, 1):
            errors.extend(f"solution #{i}: {e}" for e in validate_solution(s))
            if s.get("question_id") in solution_ids:
                errors.append(f"solution #{i}: duplicate question_id {s.get('question_id')}")
            solution_ids.add(s.get("question_id"))
        question_ids = {q["question_id"] for q in questions}
        missing = question_ids - solution_ids
        extra = solution_ids - question_ids
        errors.extend(f"missing solution for {qid}" for qid in sorted(missing))
        errors.extend(f"solution has no question in import batch: {qid}" for qid in sorted(extra))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if args.dry_run:
        print(f"OK: {len(questions)} questions validated" + (f" and {len(solutions)} solutions validated" if args.solutions else ""))
        return 0

    grouped_q: dict[Path, list[dict[str, Any]]] = {}
    for q in questions:
        grouped_q.setdefault(target_question_path(q), []).append(q)
    for path, records in grouped_q.items():
        print(f"Imported {merge_records(records, path)} questions -> {path.relative_to(ROOT)}")

    if solutions:
        grouped_s: dict[Path, list[dict[str, Any]]] = {}
        question_lookup = {q["question_id"]: q for q in questions}
        for s in solutions:
            grouped_s.setdefault(target_solution_path(question_lookup[s["question_id"]]), []).append(s)
        for path, records in grouped_s.items():
            print(f"Imported {merge_records(records, path)} solutions -> {path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
