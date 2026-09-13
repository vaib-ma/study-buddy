# Study Buddy frontend

Stage 3 is a React + Vite practice interface for the FastAPI backend.

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
- Displays MCQ options when supplied by the question record
- Fetches the exact matching solution using the immutable `question_id`
- Responsive desktop/mobile layout
- Loading and API error states

Timed tests, scoring, analytics, accounts, ads, premium, and ML study planning are intentionally left for later roadmap stages.
