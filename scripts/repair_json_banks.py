#!/usr/bin/env python3
"""Repair Study Buddy JSON banks after an interrupted/older import."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ROOTS = [ROOT / "data" / "questions", ROOT / "data" / "solutions"]

def decode_many(text, path):
    decoder = json.JSONDecoder()
    values = []
    pos = 0
    while pos < len(text):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text):
            break
        try:
            value, end = decoder.raw_decode(text, pos)
        except json.JSONDecodeError as exc:
            tail = text[pos:].strip()
            if tail in {r"\n", r"\\n"}:
                break
            raise ValueError(f"{path}: cannot recover JSON at position {exc.pos}: {exc}") from exc
        values.append(value)
        pos = end
    records = []
    for value in values:
        if isinstance(value, list):
            records.extend(value)
        elif isinstance(value, dict) and isinstance(value.get("questions"), list):
            records.extend(value["questions"])
        else:
            raise ValueError(f"{path}: unsupported JSON root")
    return records

def repair(path):
    text = path.read_text(encoding="utf-8")
    records = decode_many(text, path)
    unique = []
    seen = set()
    for record in records:
        qid = record.get("question_id") if isinstance(record, dict) else None
        if qid and qid in seen:
            continue
        if qid:
            seen.add(qid)
        unique.append(record)
    path.write_text(json.dumps(unique, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"REPAIRED {path}: {len(records)} records -> {len(unique)} unique")

def main():
    changed = 0
    for root in ROOTS:
        for path in sorted(root.rglob("*.json")):
            try:
                with path.open(encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError:
                repair(path)
                changed += 1
    print(f"Done. Repaired {changed} JSON files.")

if __name__ == "__main__":
    main()
