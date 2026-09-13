# Study Buddy content-rights model

Stage 1 distinguishes between **content that Study Buddy owns**, content that is **licensed/openly reusable**, and official exam material for which we currently keep only a source reference until reuse rights are verified.

## Content types

- `original_exam_style` — newly authored Study Buddy material written to match an exam's style. This is the primary Stage 1 population strategy.
- `official_pyq` — an actual official past-exam question. Do not mark it redistributable unless the applicable rights basis has been verified.
- `licensed_pyq` — an actual PYQ covered by a license or permission that permits our intended use.
- `open_license` — material with an explicit license permitting the intended reuse.
- `source_reference_only` — metadata pointing to an official source without copying the protected question text.

## Rights statuses

- `study_buddy_owned`
- `licensed`
- `public_domain`
- `open_license`
- `permission_granted`
- `pending_verification`
- `reference_only`
- `restricted`

## Rule for imports

A question may be placed in the redistributable Study Buddy question bank only when `redistribution_allowed` is `true` and the rights status supports that decision.

Public availability of an exam paper is **not by itself treated as an open-source license**. Official PYQs can still be represented as source metadata while reuse is being verified.

## Current Stage 1 strategy

The repository is being populated first with original exam-style questions and worked solutions for JEE Main, JEE Advanced, KCET, MHT-CET, BITSAT, GAKAO, and SAT. This lets the application pipeline develop without assuming that publicly available exam papers are freely redistributable.

For future licensed/open material, retain the license or permission reference in `license`, `license_reference`, and `source_reference`.
