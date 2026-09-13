# Incoming question data

Put legally obtained question and solution batches here before importing them into `data/`.

## Question JSONL format

One JSON object per line. Example:

```json
{"question_id":"JEE-MAIN-PHY-2026-000002","exam":"JEE Main","exam_year":2026,"subject":"Physics","chapter":"Kinematics","topic":"Motion in a straight line","difficulty":"Medium","question_type":"MCQ","question_text":"An object starts from rest and moves with constant acceleration a. Which expression gives its displacement after time t?","options":["at","at^2/2","2at^2","a/t"],"correct_answer":"B","marks":4,"negative_marks":1,"source":"Original demonstration content","source_reference":""}
```

## Solution JSONL format

```json
{"question_id":"JEE-MAIN-PHY-2026-000002","solution_text":"For constant acceleration from rest, use s = ut + (1/2)at^2 with u = 0.","answer_explanation":"Therefore s = at^2/2, which corresponds to option B.","final_answer":"B","key_concepts":["equations of motion"],"common_mistakes":["forgetting that the initial velocity is zero"],"source":"Original demonstration content","source_reference":""}
```

Then run:

```bash
python scripts/import_questions.py --input incoming/questions.jsonl --solutions incoming/solutions.jsonl --dry-run
```

If validation succeeds, remove `--dry-run` to import the records into the correct exam/subject files.

**Content/legal note:** only import material you are legally permitted to reproduce. Do not use this folder as a scraper output or for copyrighted question-bank dumps.
