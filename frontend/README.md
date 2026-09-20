# Study Buddy frontend

Stage 3/4 is a React + Vite interface for the FastAPI backend.

## Run locally

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://127.0.0.1:5173` by default.

Start the backend in another terminal:

```bash
python -m uvicorn backend.app:app --reload
```

The frontend uses `http://127.0.0.1:8000` by default. To point it at another backend:

```bash
VITE_API_BASE_URL=http://your-backend-host:8000 npm run dev
```

## Stage 3 features

- Exam → subject → chapter filtering
- Difficulty filtering
- Loads questions from the backend API
- Displays MCQ options
- Fetches the exact matching solution using immutable `question_id`

## Stage 4 features

- Creates a server-side test session
- Randomly selects questions matching the chosen filters
- Timed 15-minute test by default
- Previous/next navigation
- Answer selection
- Automatic submission when the timer reaches zero
- Manual submission
- Server-side scoring using marks and negative marks
- Correct/wrong/unanswered counts
- Accuracy and question-by-question review
- Answer keys are removed from normal question responses so the browser does not receive them before submission

Stage 4 test sessions currently live in backend memory. They are intentionally a prototype; persistent accounts, saved attempts, analytics, and production database storage come in later stages.
