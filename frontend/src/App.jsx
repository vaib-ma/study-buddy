import { useEffect, useState } from 'react';
import { api } from './api';

const EXAM_LABELS = {
  jee_main: 'JEE Main',
  jee_advanced: 'JEE Advanced',
  kcet: 'KCET',
  mht_cet: 'MHT-CET',
  bitsat: 'BITSAT',
  gakao: 'GAKAO',
  sat: 'SAT',
};

function App() {
  const [exams, setExams] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [chapters, setChapters] = useState([]);
  const [exam, setExam] = useState('');
  const [subject, setSubject] = useState('');
  const [chapter, setChapter] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [questions, setQuestions] = useState([]);
  const [solutions, setSolutions] = useState({});
  const [loading, setLoading] = useState(false);
  const [loadingSolution, setLoadingSolution] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    api.getExams()
      .then((data) => setExams(data.exams || data))
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    setSubject('');
    setChapter('');
    setChapters([]);
    setQuestions([]);
    setSolutions({});
    if (!exam) {
      setSubjects([]);
      return;
    }
    api.getSubjects(exam)
      .then((data) => setSubjects(data.subjects || data))
      .catch((err) => setError(err.message));
  }, [exam]);

  useEffect(() => {
    setChapter('');
    setChapters([]);
    setQuestions([]);
    setSolutions({});
    if (!exam || !subject) return;
    api.getChapters(exam, subject)
      .then((data) => setChapters(data.chapters || data))
      .catch((err) => setError(err.message));
  }, [exam, subject]);

  async function loadQuestions() {
    setLoading(true);
    setError('');
    setSolutions({});
    try {
      const data = await api.getQuestions({
        exam,
        subject,
        chapter,
        difficulty,
        limit: 20,
        offset: 0,
      });
      setQuestions(data.questions || []);
    } catch (err) {
      setError(err.message);
      setQuestions([]);
    } finally {
      setLoading(false);
    }
  }

  async function showSolution(questionId) {
    setLoadingSolution(questionId);
    setError('');
    try {
      const data = await api.getQuestionSolution(questionId);
      setSolutions((current) => ({ ...current, [questionId]: data.solution }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingSolution('');
    }
  }

  const examOptions = exams.map((item) => {
    const value = typeof item === 'string' ? item : item.exam;
    return { value, label: EXAM_LABELS[value] || value };
  });

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-mark">SB</div>
        <div>
          <div className="brand">Study Buddy</div>
          <div className="tagline">Practice smarter. Prepare better.</div>
        </div>
        <div className="stage-pill">Stage 3 · Practice</div>
      </header>

      <main className="container">
        <section className="hero">
          <div>
            <span className="eyebrow">COMPETITIVE EXAM PREP</span>
            <h1>Your practice desk.</h1>
            <p>Choose an exam, narrow it down to a subject and chapter, then start solving.</p>
          </div>
          <div className="hero-stat"><strong>100</strong><span>original questions</span></div>
        </section>

        <section className="filters card">
          <div className="section-title">
            <div><span className="step">01</span><h2>Build your practice set</h2></div>
            <span className="muted">Up to 20 questions</span>
          </div>
          <div className="filter-grid">
            <label>Exam<select value={exam} onChange={(e) => setExam(e.target.value)}><option value="">Choose exam</option>{examOptions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
            <label>Subject<select value={subject} onChange={(e) => setSubject(e.target.value)} disabled={!exam}><option value="">Choose subject</option>{subjects.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
            <label>Chapter<select value={chapter} onChange={(e) => setChapter(e.target.value)} disabled={!subject}><option value="">All chapters</option>{chapters.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
            <label>Difficulty<select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}><option value="">Any level</option><option value="Easy">Easy</option><option value="Medium">Medium</option><option value="Hard">Hard</option></select></label>
          </div>
          <button className="primary" onClick={loadQuestions} disabled={!exam || loading}>{loading ? 'Loading…' : 'Load questions →'}</button>
        </section>

        {error && <div className="error">{error}</div>}

        <section className="questions-section">
          <div className="section-heading"><div><span className="step">02</span><h2>Practice</h2></div><span className="count">{questions.length} loaded</span></div>
          {questions.length === 0 && !loading ? (
            <div className="empty card"><div className="empty-icon">✦</div><h3>Ready when you are.</h3><p>Select an exam and click “Load questions” to begin your practice session.</p></div>
          ) : (
            <div className="question-list">{questions.map((question, index) => <QuestionCard key={question.question_id} question={question} index={index} solution={solutions[question.question_id]} loading={loadingSolution === question.question_id} onSolution={showSolution} />)}</div>
          )}
        </section>
      </main>
      <footer>Study Buddy · Original exam-style practice content · More features coming in later stages</footer>
    </div>
  );
}

function QuestionCard({ question, index, solution, loading, onSolution }) {
  const options = question.options || [];
  return (
    <article className="question-card card">
      <div className="question-meta"><span>Q{index + 1}</span><span>{question.subject}</span><span>{question.chapter}</span>{question.difficulty && <span>{question.difficulty}</span>}</div>
      <h3>{question.question || question.text}</h3>
      {options.length > 0 && <div className="options">{options.map((option, i) => <div className="option" key={i}><span>{String.fromCharCode(65 + i)}</span><div>{typeof option === 'string' ? option : option.text}</div></div>)}</div>}
      <div className="question-actions"><span className="qid">{question.question_id}</span><button className="secondary" onClick={() => onSolution(question.question_id)} disabled={loading}>{loading ? 'Loading…' : solution ? 'Solution shown' : 'Show solution'}</button></div>
      {solution && <Solution solution={solution} />}
    </article>
  );
}

function Solution({ solution }) {
  const explanation = solution.explanation || solution.solution || solution.steps || solution.answer_explanation;
  return <div className="solution"><div className="solution-title">✓ Worked solution</div>{solution.final_answer && <div className="final-answer"><strong>Answer:</strong> {solution.final_answer}</div>}<p>{typeof explanation === 'string' ? explanation : JSON.stringify(explanation)}</p></div>;
}

export default App;
