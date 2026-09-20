# Open-license question sources

## eQOURSE

Study Buddy can import the eQOURSE JEE Main and JEE Advanced datasets because their Hugging Face dataset cards declare **CC BY 4.0**. The datasets provide structured question metadata and worked solutions; JEE Advanced has 119 rows across Physics, Chemistry, and Mathematics. The importer preserves source, attribution, license, and source-paper metadata.

- JEE Advanced: https://huggingface.co/datasets/eQOURSE/jee-advanced-questions
- JEE Main: https://huggingface.co/datasets/eQOURSE/jee-main-questions

The application should continue to display attribution for imported open-license content.

## Difficulty policy

Existing Study Buddy-authored starter questions are the foundation tier. Imported JEE Advanced questions are initially classified by Study Buddy as **Very Hard** unless the source explicitly provides a harder/easier label. This is an application classification, not a claim made by eQOURSE.

## Stable IDs

Every imported question receives a Study Buddy ID such as JEEA-PHY-2021-000001. The matching solution uses the exact same question_id.

## Other datasets

JEEBench is useful as a research/reference source, but the repository's MIT software license should not be treated as a license for the underlying exam-question text. Until the question-data rights are separately verified, Study Buddy keeps JEEBench as reference_only.
