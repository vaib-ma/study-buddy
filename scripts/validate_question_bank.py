#!/usr/bin/env python3
"""Validate Study Buddy question and solution JSON files."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTION_ROOT = ROOT / "data" / "questions"
SOLUTION_ROOT = ROOT / "data" / "solutions"
ID_RE = re.compile(r"^[A-Z0-9-]+-[0-9]{4}-[0-9]{6}$")
REQUIRED = {"question_id", "exam", "exam_year", "subject", "chapter", "topic", "difficulty", "question_type", "question_text", "correct_answer", "marks", "negative_marks", "source", "content_type", "rights_status", "redistribution_allowed"}
ALLOWED_EXAMS = {"JEE Main", "JEE Advanced", "KCET", "MHT-CET", "BITSAT", "GAKAO", "SAT"}
ALLOWED_DIFFICULTY = {"Easy", "Medium", "Hard"}
ALLOWED_CONTENT_TYPES = {"original_exam_style", "official_pyq", "licensed_pyq", "public_domain", "open_license", "source_reference_only"}
ALLOWED_RIGHTS = {"study_buddy_owned", "licensed", "public_domain", "open_license", "permission_granted", "pending_verification", "reference_only", "restricted"}


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    errors: list[str] = []
    questions: dict[str, dict] = {}
    solutions: dict[str, dict] = {}

    for path in sorted(QUESTION_ROOT.rglob("*.json")):
        try:
            records = load(path)
        except Exception as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(records, list):
            errors.append(f"{path}: root must be a JSON array")
            continue
        for i, q in enumerate(records):
            label = f"{path} item {i + 1}"
            if not isinstance(q, dict):
                errors.append(f"{label}: record must be an object")
                continue
            missing = REQUIRED - q.keys()
            if missing:
                errors.append(f"{label}: missing {sorted(missing)}")
            qid = q.get("question_id")
            if not isinstance(qid, str) or not ID_RE.fullmatch(qid):
                errors.append(f"{label}: invalid question_id")
            elif qid in questions:
                errors.append(f"{label}: duplicate question_id {qid}")
            else:
                questions[qid] = q
            if q.get("exam") not in ALLOWED_EXAMS:
                errors.append(f"{label}: unsupported exam")
            if q.get("difficulty") not in ALLOWED_DIFFICULTY:
                errors.append(f"{label}: unsupported difficulty")
            if q.get("content_type") not in ALLOWED_CONTENT_TYPES:
                errors.append(f"{label}: unsupported content_type")
            if q.get("rights_status") not in ALLOWED_RIGHTS:
                errors.append(f"{label}: unsupported rights_status")
            if not isinstance(q.get("redistribution_allowed"), bool):
                errors.append(f"{label}: redistribution_allowed must be boolean")
            if q.get("content_type") == "original_exam_style" and q.get("rights_status") != "study_buddy_owned":
                errors.append(f"{label}: original_exam_style must be study_buddy_owned")
            if q.get("rights_status") in {"pending_verification", "reference_only", "restricted"} and q.get("redistribution_allowed") is True:
                errors.append(f"{label}: unverified/reference/restricted content cannot be redistributable")
            if q.get("negative_marks", 0) < 0:
                errors.append(f"{label}: negative_marks cannot be below zero")

    for path in sorted(SOLUTION_ROOT.rglob("*.json")):
        try:
            records = load(path)
        except Exception as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(records, list):
            errors.append(f"{path}: root must be a JSON array")
            continue
        for i, s in enumerate(records):
            label = f"{path} item {i + 1}"
            if not isinstance(s, dict):
                errors.append(f"{label}: record must be an object")
                continue
            qid = s.get("question_id")
            if not isinstance(qid, str):
                errors.append(f"{label}: missing question_id")
            elif qid in solutions:
                errors.append(f"{label}: duplicate solution question_id {qid}")
            else:
                solutions[qid] = s

    missing_solutions = sorted(set(questions) - set(solutions))
    orphan_solutions = sorted(set(solutions) - set(questions))
    errors.extend(f"missing solution for {qid}" for qid in missing_solutions)
    errors.extend(f"solution has no matching question: {qid}" for qid in orphan_solutions)

    for qid, q in questions.items():
        s = solutions.get(qid)
        if s and s.get("final_answer") != q.get("correct_answer"):
            errors.append(f"{qid}: solution final_answer does not match correct_answer")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"VALIDATION PASSED: {len(questions)} questions, {len(solutions)} solutions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
