# Study Buddy Backend

Stage 2 starts with a small FastAPI service over the Stage 1 JSON repository.

## Run locally

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```

The API runs at `http://127.0.0.1:8000`.

Interactive API documentation is available at `/docs`.

## Endpoints

- `GET /health` — API status and question count
- `GET /exams` — supported exams
- `GET /subjects?exam=KCET` — subjects for an exam
- `GET /chapters?exam=KCET&subject=Physics` — chapters
- `GET /questions` — paginated question listing with optional filters
- `GET /questions/{question_id}` — exact question by stable ID
- `GET /solutions/{question_id}` — exact solution by stable ID
- `GET /questions/{question_id}/solution` — question + matching solution joined by ID

The service reads the repository's JSON files directly for this first backend milestone. A production database can replace the storage layer later without changing the public API contract.
