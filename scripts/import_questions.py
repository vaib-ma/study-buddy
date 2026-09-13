#!/usr/bin/env python3
"""Import Study Buddy questions and solutions from JSONL or JSON files.

The importer validates records, enforces stable question IDs, checks content-rights
metadata, and writes questions and solutions to separate exam/subject files.
It never downloads or scrapes question content.
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
ALLOWED_CONTENT_TYPES = {"original_exam_style", "official_pyq", "licensed_pyq", "public_domain", "open_license", "source_reference_only"}
ALLOWED_RIGHTS = {"study_buddy_owned", "licensed", "public_domain", "open_license", "permission_granted", "pending_verification", "reference_only", "restricted"}


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
    required = [
        "question_id", "exam", "exam_year", "subject", "chapter", "topic",
        "difficulty", "question_type", "question_text", "correct_answer",
        "marks", "negative_marks", "source", "content_type",
        "rights_status", "redistribution_allowed",
    ]
    errors = [f"missing {field}" for field in required if field not in q]
    if errors:
        return errors
    if not isinstance(q["question_id"], str) or not ID_RE.fullmatch(q["question_id"]): errors.append("invalid question_id")
    if q["exam"] not in ALLOWED_EXAMS: errors.append("unsupported exam")
    if q["subject"] not in ALLOWED_SUBJECTS: errors.append("unsupported subject")
    if q["difficulty"] not in ALLOWED_DIFFICULTIES: errors.append("unsupported difficulty")
    if q["question_type"] not in ALLOWED_TYPES: errors.append("unsupported question_type")
    if q["content_type"] not in ALLOWED_CONTENT_TYPES: errors.append("unsupported content_type")
    if q["rights_status"] not in ALLOWED_RIGHTS: errors.append("unsupported rights_status")
    if not isinstance(q["redistribution_allowed"], bool): errors.append("redistribution_allowed must be boolean")
    if not isinstance(q["exam_year"], int) or not 2000 <= q["exam_year"] <= 2100: errors.append("invalid exam_year")
    if not isinstance(q["question_text"], str) or not q["question_text"].strip(): errors.append("empty question_text")
    if not isinstance(q["correct_answer"], str) or not q["correct_answer"].strip(): errors.append("empty correct_answer")
    if not isinstance(q["negative_marks"], (int, float)) or q["negative_marks"] < 0: errors.append("invalid negative_marks")
    if q["content_type"] == "original_exam_style" and q["rights_status"] != "study_buddy_owned": errors.append("original_exam_style must be study_buddy_owned")
    if q["rights_status"] in {"pending_verification", "reference_only", "restricted"} and q["redistribution_allowed"]:
        errors.append("redistribution_allowed cannot be true for an unverified/reference/restricted rights status")
    return errors


def validate_solution(s: dict[str, Any]) -> list[str]:
    required = ["question_id", "solution_text", "final_answer"]
    errors = [f"missing {field}" for field in required if field not in s]
    if errors:
        return errors
    if not isinstance(s["question_id"], str) or not ID_RE.fullmatch(s["question_id"]): errors.append("invalid question_id")
    for field in ("solution_text", "final_answer"):
        if not isinstance(s[field], str) or not s[field].strip(): errors.append(f"empty {field}")
    return errors


def exam_slug(exam: str) -> str:
    return {"JEE Main":"jee_main", "JEE Advanced":"jee_advanced", "KCET":"cet/kcet", "MHT-CET":"cet/mht_cet", "BITSAT":"bitsat", "GAKAO":"gakao", "SAT":"sat"}[exam]


def subject_slug(subject: str) -> str:
    return {"Physics":"physics", "Chemistry":"chemistry", "Mathematics":"mathematics", "SAT Math":"sat_math", "SAT Reading and Writing":"sat_reading_writing"}[subject]


def target_path(record: dict[str, Any], kind: str) -> Path:
    return ROOT / "data" / kind / exam_slug(record["exam"]) / f"{subject_slug(record['subject'])}.json"


def read_existing(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("questions", data.get("solutions", []))


def merge_records(records: list[dict[str, Any]], path: Path) -> int:
    existing = read_existing(path)
    ids = {r["question_id"] for r in existing}
    for record in records:
        if record["question_id"] in ids: raise ValueError(f"duplicate question_id {record['question_id']} in {path}")
        existing.append(record); ids.add(record["question_id"])
    existing.sort(key=lambda r: r["question_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(records)


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
        if qid in seen: errors.append(f"question #{i}: duplicate question_id {qid}")
        seen.add(qid)

    solutions = load_records(args.solutions) if args.solutions else []
    if args.solutions:
        solution_ids: set[str] = set()
        for i, s in enumerate(solutions, 1):
            errors.extend(f"solution #{i}: {e}" for e in validate_solution(s))
            qid = s.get("question_id")
            if qid in solution_ids: errors.append(f"solution #{i}: duplicate question_id {qid}")
            solution_ids.add(qid)
        question_ids = {q["question_id"] for q in questions}
        errors.extend(f"missing solution for {qid}" for qid in sorted(question_ids - solution_ids))
        errors.extend(f"solution has no question in import batch: {qid}" for qid in sorted(solution_ids - question_ids))

    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    if args.dry_run:
        print(f"OK: {len(questions)} questions validated" + (f" and {len(solutions)} solutions validated" if args.solutions else ""))
        return 0

    grouped_q: dict[Path, list[dict[str, Any]]] = {}
    for q in questions: grouped_q.setdefault(target_path(q, "questions"), []).append(q)
    for path, records in grouped_q.items(): print(f"Imported {merge_records(records, path)} questions -> {path.relative_to(ROOT)}")

    if solutions:
        lookup = {q["question_id"]: q for q in questions}
        grouped_s: dict[Path, list[dict[str, Any]]] = {}
        for s in solutions: grouped_s.setdefault(target_path(lookup[s["question_id"]], "solutions"), []).append(s)
        for path, records in grouped_s.items(): print(f"Imported {merge_records(records, path)} solutions -> {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
