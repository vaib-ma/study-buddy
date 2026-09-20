#!/usr/bin/env python3
"""Audit imported question banks for completeness, answer integrity, and math extraction damage.

This script is intentionally conservative: it flags suspicious records instead of silently
inventing missing exam content. Run it against the local question/solution files before
publishing a bank.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = ROOT / "data" / "questions"
SOLUTIONS_DIR = ROOT / "data" / "solutions"
REPORT_PATH = ROOT / "data" / "question_quality_report.json"

QUESTION_ENDINGS = re.compile(
    r"\b(?:if|when|where|which|that|given|satisfying|according to|then|is|are|"
    r"has|have|will be|can be|the value of|the number of)\s*$",
    re.I,
)
MISSING_INTERVAL = re.compile(r"\binterval\b", re.I)
INTERVAL_RANGE = re.compile(
    r"(?:\[[^\[\]]+[,;][^\[\]]+\]|\([^()]+[,;][^()]+\)|"
    r"\b(?:from|between)\s+[^,.]+\s+(?:to|and)\s+[^,.]+)",
    re.I,
)
MISSING_REFERENCE = re.compile(
    r"\b(?:shown|given|shown below|given below|following)\b.*\b(?:figure|diagram|graph|"
    r"plot|matrix|table|image)\b",
    re.I,
)
LATEX_DAMAGE = re.compile(
    r"(?:\\_|\\\^|\\sum\\_|\\prod\\_|(?<!\\)\bsin(?=\d|[a-zA-Z])|"
    r"(?<!\\)\bcos(?=\d|[a-zA-Z])|(?<!\\)\btan(?=\d|[a-zA-Z]))"
)
PLACEHOLDER = re.compile(r"\b(?:null|none|undefined|todo|tbd)\b", re.I)


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and isinstance(data.get("questions"), list):
        return data["questions"]
    return data if isinstance(data, list) else []


def normalized(value):
    return re.sub(r"\s+", "", str(value or "")).replace("−", "-")


def audit():
    solutions = {}
    for path in SOLUTIONS_DIR.rglob("*.json"):
        for item in load(path):
            if isinstance(item, dict) and item.get("question_id"):
                solutions[item["question_id"]] = item

    report = {
        "question_count": 0,
        "issue_count": 0,
        "issues": [],
    }

    for path in sorted(QUESTIONS_DIR.rglob("*.json")):
        if path.name in {"taxonomy.json", "question_index.json"}:
            continue

        for q in load(path):
            if not isinstance(q, dict):
                continue
            report["question_count"] += 1
            qid = q.get("question_id", "")
            text = str(q.get("question_text") or q.get("question") or "").strip()
            issues = []

            if len(text) < 20:
                issues.append("question-too-short")
            if QUESTION_ENDINGS.search(text):
                issues.append("possibly-truncated-question")
            if MISSING_INTERVAL.search(text) and not INTERVAL_RANGE.search(text):
                issues.append("interval-without-range")
            if MISSING_REFERENCE.search(text) and "[Diagram]" not in text and "[IMAGE]" not in text:
                issues.append("possible-missing-reference")
            if LATEX_DAMAGE.search(text):
                issues.append("possible-math-extraction-damage")
            if PLACEHOLDER.search(text):
                issues.append("placeholder-text")

            answer = q.get("correct_answer")
            if answer is None or str(answer).strip() == "":
                issues.append("missing-answer")

            solution = solutions.get(qid)
            if solution is None:
                issues.append("missing-solution")
            else:
                solution_text = str(solution.get("solution_text") or "").strip()
                if not solution_text:
                    issues.append("empty-solution")
                final_answer = solution.get("final_answer")
                if final_answer is not None and normalized(final_answer) != normalized(answer):
                    issues.append("solution-answer-mismatch")

            if issues:
                report["issues"].append({
                    "question_id": qid,
                    "file": str(path.relative_to(ROOT)),
                    "exam": q.get("exam"),
                    "subject": q.get("subject"),
                    "chapter": q.get("chapter"),
                    "topic": q.get("topic"),
                    "question_type": q.get("question_type"),
                    "difficulty": q.get("difficulty"),
                    "question_text": text,
                    "correct_answer": answer,
                    "solution_text": (solutions.get(qid) or {}).get("solution_text", ""),
                    "solution_final_answer": (solutions.get(qid) or {}).get("final_answer"),
                    "issues": issues,
                })

    report["issue_count"] = len(report["issues"])
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Audited {report['question_count']} questions.")
    print(f"Flagged {report['issue_count']} records.")
    print(f"Report: {REPORT_PATH}")

    return 1 if report["issue_count"] else 0


if __name__ == "__main__":
    sys.exit(audit())
