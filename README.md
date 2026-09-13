# Study Buddy

A data-first competitive-exam preparation platform for practice, tests, analytics, and ML-based study planning.

## Stage 1 — Question & Solution Repository

This repository starts with an exam-aware question/solution data layer. The same stable `question_id` is used in both the question and solution records so the application can retrieve the exact solution for a selected question.

### Current repository layout

```text
data/
├── questions/
│   ├── jee_main/
│   │   ├── physics.json
│   │   ├── chemistry.json
│   │   └── mathematics.json
│   ├── jee_advanced/
│   │   ├── physics.json
│   │   ├── chemistry.json
│   │   └── mathematics.json
│   ├── cet/
│   │   ├── kcet/physics.json
│   │   └── mht_cet/physics.json
│   ├── bitsat/physics.json
│   ├── gakao/mathematics.json
│   └── sat/sat_math.json
└── solutions/
    └── matching exam/subject files

schema/
├── question.schema.json
└── solution.schema.json

docs/
└── CONTENT_RIGHTS.md

scripts/
├── validate_question_bank.py
└── import_questions.py
```

## Question IDs

Use stable IDs such as:

`JEE-MAIN-PHY-2026-000001`

The ID should never be reused for another question.

## Content model

Stage 1 now records content provenance and reuse status on every question:

- `original_exam_style` — newly authored Study Buddy question matching an exam's style.
- `official_pyq` — official past-exam question; reuse must be verified before redistribution.
- `licensed_pyq` / `open_license` — reusable material with an appropriate license or permission.
- `source_reference_only` — source metadata without copying protected question text.

Every question also has `rights_status` and `redistribution_allowed`. See `docs/CONTENT_RIGHTS.md` for the full policy.

**Public availability does not automatically mean open-source.** We can add actual PYQs when a suitable permission/license or other verified lawful basis supports redistribution. Until then, the repository can store official-source metadata separately and use original exam-style questions for the working bank.

## Current Stage 1 bank

The repository currently contains original exam-style questions and worked solutions covering all seven supported exam categories:

- JEE Main — Physics, Chemistry, Mathematics
- JEE Advanced — Physics, Chemistry, Mathematics
- KCET — Physics
- MHT-CET — Physics
- BITSAT — Physics
- GAKAO — Mathematics
- SAT — SAT Math

These are **not claimed to be official PYQs**.

## Importing more questions

Validate a batch before importing it:

```bash
python scripts/import_questions.py --input incoming/questions.jsonl --solutions incoming/solutions.jsonl --dry-run
```

Then run without `--dry-run` to import it.

## Validation

From the repository root:

```bash
python scripts/validate_question_bank.py
```

The validator checks JSON structure, required fields, ID format/uniqueness, question-to-solution matching, answer consistency, and supported taxonomy values.

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
