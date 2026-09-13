#!/usr/bin/env python3
"""Build a compact question index for fast filtering in Stage 2.

The index contains metadata only; question text, options, and solutions remain in
separate source files. Re-run this script whenever the question bank changes.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTION_ROOT = ROOT / "data" / "questions"
OUTPUT = ROOT / "data" / "question_index.json"


def load_records(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("questions", [])


def main() -> int:
    records: list[dict] = []
    for path in sorted(QUESTION_ROOT.rglob("*.json")):
        records.extend(load_records(path))

    records.sort(key=lambda q: q["question_id"])
    index = {
        "version": 1,
        "generated_by": "scripts/build_question_index.py",
        "question_count": len(records),
        "questions": [
            {
                "question_id": q["question_id"],
                "exam": q["exam"],
                "exam_year": q["exam_year"],
                "subject": q["subject"],
                "chapter": q["chapter"],
                "topic": q["topic"],
                "difficulty": q["difficulty"],
                "question_type": q["question_type"],
                "marks": q["marks"],
                "negative_marks": q["negative_marks"],
                "content_type": q["content_type"],
                "rights_status": q["rights_status"],
                "redistribution_allowed": q["redistribution_allowed"],
            }
            for q in records
        ],
        "facets": {
            "exams": sorted(Counter(q["exam"] for q in records).items()),
            "subjects": sorted(Counter(q["subject"] for q in records).items()),
            "difficulties": sorted(Counter(q["difficulty"] for q in records).items()),
            "question_types": sorted(Counter(q["question_type"] for q in records).items()),
            "chapters": sorted(Counter(q["chapter"] for q in records).items()),
        },
    }
    OUTPUT.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"WROTE {OUTPUT.relative_to(ROOT)}: {len(records)} questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
