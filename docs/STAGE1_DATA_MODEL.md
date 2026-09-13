# Stage 1 data model

Stage 1 is intentionally data-first. The repository separates question records from solution records and uses an immutable `question_id` as the join key.

## Question record

Each question stores:

- identity: `question_id`, `exam`, `exam_year`
- taxonomy: `subject`, `chapter`, `topic`, `tags`
- assessment: `difficulty`, `question_type`, `marks`, `negative_marks`
- delivery: `question_text`, optional `options`, `correct_answer`
- provenance: `source`, optional `source_reference`
- rights: `content_type`, `rights_status`, `redistribution_allowed`, optional `rights_holder`, `license`, `license_reference`

## Solution record

Each solution stores the same `question_id` plus:

- `solution_type`
- `solution_text`
- `final_answer`
- optional `answer_explanation`, `key_concepts`, `common_mistakes`, and `tips`

## Lookup contract

The future application should never guess a solution by array position or filename. It should:

1. select a question by `question_id`;
2. retrieve the solution with the exact same `question_id`;
3. display the solution only after the relevant practice/test state allows it.

## Index

`scripts/build_question_index.py` produces `data/question_index.json`. The index contains metadata needed for exam, subject, chapter, topic, difficulty, and question-type filters without duplicating question text or solutions.

## Taxonomy

`data/taxonomy.json` defines the stable Stage 1 exam/subject vocabulary and allowed difficulty/question/content/rights values. It is an application taxonomy and should be expanded carefully as the bank grows; it is not intended to replace an official exam syllabus.

## Rights safety

The index and question files must preserve rights metadata. Official or third-party exam material must not be treated as reusable merely because it is publicly accessible. Exact PYQs should only become redistributable when the applicable permission, license, or other verified lawful basis has been established.
