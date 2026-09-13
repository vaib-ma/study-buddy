# Study Buddy

A data-first competitive-exam preparation platform for practice, tests, analytics, and ML-based study planning.

## Stage 1 — Question & Solution Repository

This repository starts with an exam-aware question/solution data layer. The same stable `question_id` is used in both the question and solution records so the application can retrieve the exact solution for a selected question.

### Current repository layout

```text
data/
├── questions/
│   ├── jee_main/{physics,chemistry,mathematics}.json
│   ├── jee_advanced/{physics,chemistry,mathematics}.json
│   ├── cet/
│   │   ├── kcet/{physics,chemistry,mathematics}.json
│   │   └── mht_cet/{physics,chemistry,mathematics}.json
│   ├── bitsat/{physics,chemistry,mathematics}.json
│   ├── gakao/mathematics.json
│   └── sat/{sat_math,sat_reading_and_writing}.json
├── taxonomy.json
└── question_index.json  # generated catalog when the index builder is run

schema/
├── question.schema.json
└── solution.schema.json

docs/
├── CONTENT_RIGHTS.md
└── STAGE1_DATA_MODEL.md

scripts/
├── validate_question_bank.py
├── import_questions.py
└── build_question_index.py
```

## Question IDs

Use stable IDs such as:

`JEE-MAIN-PHY-2026-000001`

The ID should never be reused for another question.

## Content model

Stage 1 records content provenance and reuse status on every question:

- `original_exam_style` — newly authored Study Buddy question matching an exam's style.
- `official_pyq` — official past-exam question; reuse must be verified before redistribution.
- `licensed_pyq` / `open_license` — reusable material with an appropriate license or permission.
- `source_reference_only` — source metadata without copying protected question text.

Every question also has `rights_status` and `redistribution_allowed`. See `docs/CONTENT_RIGHTS.md` for the full policy.

**Public availability does not automatically mean open-source.** We can add actual PYQs when a suitable permission/license or other verified lawful basis supports redistribution. Until then, the repository can store official-source metadata separately and use original exam-style questions for the working bank.

## Current Stage 1 bank

The repository currently contains **36 original exam-style questions with 36 matching worked/conceptual solutions** across all seven supported exam categories:

- JEE Main — Physics, Chemistry, Mathematics (6)
- JEE Advanced — Physics, Chemistry, Mathematics (6)
- KCET — Physics, Chemistry, Mathematics (6)
- MHT-CET — Physics, Chemistry, Mathematics (6)
- BITSAT — Physics, Chemistry, Mathematics (6)
- GAKAO — Mathematics (2)
- SAT — SAT Math, Reading and Writing (4)

These are **not claimed to be official PYQs**.

## Importing more questions

Validate a batch before importing it:

```bash
python scripts/import_questions.py --input incoming/questions.jsonl --solutions incoming/solutions.jsonl --dry-run
```

Then run without `--dry-run` to import it.

## Building the filter index

After adding or changing questions, regenerate the metadata-only catalog:

```bash
python scripts/build_question_index.py
```

The generated index is designed for fast filtering by exam, subject, chapter, topic, difficulty, and question type without duplicating full question text.

## Validation

From the repository root:

```bash
python scripts/validate_question_bank.py
```

The validator checks JSON structure, required fields, ID format/uniqueness, question-to-solution matching, answer consistency, rights metadata, and supported taxonomy values.

GitHub Actions also runs the validator on pushes and pull requests targeting `main`.

## Roadmap

1. Question & Solution Repository ← **current**
2. Database & Backend
3. Basic Practice Website
4. Test Engine
5. Basic Analysis
6. Advanced Analysis
7. Machine Learning (no LLM)
8. Ads & Premium
9. Admin Panel
10. Optimization & Launch
