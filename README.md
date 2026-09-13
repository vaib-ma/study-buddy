# Study Buddy

A data-first competitive-exam preparation platform for practice, tests, analytics, and ML-based study planning.

## Stage 1 — Question & Solution Repository ✓

This repository starts with an exam-aware question/solution data layer. The same stable `question_id` is used in both the question and solution records so the application can retrieve the exact solution for a selected question.

## Stage 2 — Database & Backend ✓

A FastAPI backend exposes the Stage 1 repository through a stable API. The first implementation reads the JSON data directly; the storage layer can later be migrated to PostgreSQL without changing the frontend-facing API contract.

See `backend/README.md` for setup and endpoints.

## Stage 3 — Basic Practice Website ← current

A React + Vite frontend now connects to the FastAPI API. Users can select an exam, subject, chapter, and difficulty, load a practice set, view questions, and reveal the exact matching solution by `question_id`.

See `frontend/README.md` for setup.

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
└── question_index.json

backend/
├── app.py
├── requirements.txt
└── README.md

frontend/
├── package.json
├── index.html
├── vite.config.js
├── README.md
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── api.js
    └── styles.css

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

## Current question bank

The repository currently contains **100 original exam-style questions with 100 matching worked/conceptual solutions** across all seven supported exam categories. These are **not claimed to be official PYQs**.

- JEE Main — Physics, Chemistry, Mathematics (9)
- JEE Advanced — Physics, Chemistry, Mathematics (9)
- KCET — Physics, Chemistry, Mathematics (6 each; 18 total)
- MHT-CET — Physics, Chemistry, Mathematics (6 each; 18 total)
- BITSAT — Physics, Chemistry, Mathematics (6 each; 18 total)
- GAKAO — Mathematics (10)
- SAT — SAT Math (10), Reading and Writing (8) — 18 total

## Backend API

- `GET /health` — API status and question count
- `GET /exams` — supported exams
- `GET /subjects?exam=KCET` — subjects for an exam
- `GET /chapters?exam=KCET&subject=Physics` — chapters
- `GET /questions` — paginated question listing with filters
- `GET /questions/{question_id}` — exact question by stable ID
- `GET /solutions/{question_id}` — exact solution by stable ID
- `GET /questions/{question_id}/solution` — exact question/solution join

## Local development

Start the backend:

```bash
python -m uvicorn backend.app:app --reload
```

In another terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

By default the frontend uses `http://127.0.0.1:8000` for the API and runs on `http://127.0.0.1:5173`.

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

## Validation

From the repository root:

```bash
python scripts/validate_question_bank.py
```

The validator checks JSON structure, required fields, ID format/uniqueness, question-to-solution matching, answer consistency, rights metadata, and supported taxonomy values.

GitHub Actions also runs the validator on pushes and pull requests targeting `main`.

## Roadmap

1. Question & Solution Repository ✓
2. Database & Backend ✓
3. Basic Practice Website ← **current**
4. Test Engine
5. Basic Analysis
6. Advanced Analysis
7. Machine Learning (no LLM)
8. Ads & Premium
9. Admin Panel
10. Optimization & Launch
