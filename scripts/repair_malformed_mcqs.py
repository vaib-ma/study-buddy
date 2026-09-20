#!/usr/bin/env python3
"""Repair malformed MCQ records produced by the eQOURSE importer.

Some source rows are marked single_correct but contain fewer than two usable
options because the source extraction lost option fields. Those records are
kept as Subjective rather than presenting a broken MCQ in the app.

If a single option contains all choices separated by (B)/(C)/(D), recover the
choices before deciding the question type.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
QUESTION_ROOT = ROOT / "data" / "questions"

CHOICE_RE = re.compile(r"\s*\(([A-D])\)\s*")

def normalize_options(options):
    cleaned = [str(x).strip() for x in options if str(x).strip()]
    if len(cleaned) == 1:
        parts = CHOICE_RE.split(cleaned[0])
        if len(parts) >= 3:
            first = parts[0].strip()
            recovered = [first] if first else []
            for i in range(1, len(parts), 2):
                value = parts[i + 1].strip() if i + 1 < len(parts) else ""
                if value:
                    recovered.append(value)
            if len(recovered) >= 2:
                return recovered
    return cleaned

def repair_file(path):
    records = json.loads(path.read_text(encoding="utf-8"))
    changed = 0
    for q in records:
        if not isinstance(q, dict) or q.get("question_type") != "MCQ":
            continue
        options = normalize_options(q.get("options", []))
        if len(options) >= 2:
            q["options"] = options
            if q.get("correct_answer") not in options:
                q["question_type"] = "Subjective"
                q["negative_marks"] = 0
            elif options != q.get("options"):
                changed += 1
        else:
            q["question_type"] = "Subjective"
            q["negative_marks"] = 0
            q.pop("options", None)
            changed += 1
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed

def main():
    total = 0
    for path in sorted(QUESTION_ROOT.rglob("*.json")):
        total += repair_file(path)
    print(f"Done. Repaired {total} malformed MCQ records.")

if __name__ == "__main__":
    main()
