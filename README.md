# Study Buddy

A data-first competitive-exam preparation platform for practice, tests, analytics, and ML-based study planning.

## Stage 1 — Question & Solution Repository

This repository starts with a clean, exam-aware question/solution data layer. The same stable `question_id` is used in both the question and solution records so the application can retrieve the exact solution for a selected question.

### Current repository layout

```text
data/
├── questions/
│   ├── jee_main/
│   │   ├── physics.json
│   │   ├── chemistry.json
│   │   └── mathematics.json
│   ├── jee_advanced/
│   ├── cet/
│   │   ├── kcet/
│   │   └── mht_cet/
│   ├── bitsat/
│   ├── gakao/
│   └── sat/
└── solutions/
    ├── jee_main/
    ├── jee_advanced/
    ├── cet/
    │   ├── kcet/
    │   └── mht_cet/
    ├── bitsat/
    ├── gakao/
    └── sat/

schema/
└── question.schema.json

scripts/
└── validate_question_bank.py
```

## Question IDs

Use stable IDs such as:

`JEE-MAIN-PHY-2026-000001`

The ID should never be reused for another question.

## Important content rule

Do not scrape or commit copyrighted exam questions/solutions unless we have a lawful basis to reproduce them (for example, a license, permission, or an appropriately reusable source). The included sample content is original demonstration content used to validate the repository pipeline.

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
