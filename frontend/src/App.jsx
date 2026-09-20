import { useEffect, useMemo, useState } from 'react';
import { api, API_BASE_URL } from './api';

const EXAM_LABELS = {
  'JEE Main': 'JEE Main',
  'JEE Advanced': 'JEE Advanced',
  KCET: 'KCET',
  'MHT-CET': 'MHT-CET',
  BITSAT: 'BITSAT',
  GAKAO: 'GAKAO',
  SAT: 'SAT',
};

function App() {
  const [mode, setMode] = useState('practice');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [exams, setExams] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [chapters, setChapters] = useState([]);
  const [topics, setTopics] = useState([]);
  const [exam, setExam] = useState('');
  const [subject, setSubject] = useState('');
  const [chapter, setChapter] = useState('');
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [questionType, setQuestionType] = useState('');
  const [questions, setQuestions] = useState([]);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [solutions, setSolutions] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [test, setTest] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function connect() {
      try {
        await api.health();
        if (!mounted) return;
        setBackendStatus('connected');
        const data = await api.getExams();
        if (mounted) setExams(data.exams || []);
      } catch (e) {
        if (!mounted) return;
        setBackendStatus('offline');
        setError(`Cannot connect to Study Buddy backend at ${API_BASE_URL}. Start FastAPI on port 8001 and refresh.`);
      }
    }
    connect();
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    setSubject('');
    setChapter('');
    setChapters([]);
    setTopics([]);
    setQuestions([]);
    setTotalQuestions(0);
    setSolutions({});
    if (!exam) {
      setSubjects([]);
      return;
    }
    api.getSubjects(exam)
      .then(data => setSubjects(data.subjects || []))
      .catch(e => setError(e.message));
  }, [exam]);

  useEffect(() => {
    setChapter('');
    setTopic('');
    setTopics([]);
    setQuestions([]);
    setTotalQuestions(0);
    setSolutions({});
    if (!exam || !subject) {
      setChapters([]);
      return;
    }
    api.getChapters(exam, subject)
      .then(data => setChapters(data.chapters || []))
      .catch(e => setError(e.message));
  }, [exam, subject]);


  useEffect(() => {
    setTopic('');
    setTopics([]);
    setQuestions([]);
    setTotalQuestions(0);
    setSolutions({});
    if (!exam || !subject || !chapter) return;
    api.getTopics(exam, subject, chapter)
      .then(data => setTopics(data.topics || []))
      .catch(e => setError(e.message));
  }, [exam, subject, chapter]);

  async function loadQuestions() {
    setLoading(true);
    setError('');
    setSolutions({});
    try {
      const data = await api.getQuestions({ exam, subject, chapter, topic, difficulty, question_type: questionType, limit: 20 });
      setQuestions(data.questions || []);
      setTotalQuestions(data.total || 0);
      if (!data.questions?.length) setError('No questions match these filters.');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function startTest() {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await api.createTest({
        exam,
        subject: subject || null,
        chapter: chapter || null,
        topic: topic || null,
        difficulty: difficulty || null,
        question_type: questionType || null,
        question_count: 10,
        duration_minutes: 15,
      });
      setTest({
        ...data,
        answers: {},
        index: 0,
        submitted: false,
        startedAt: Date.now(),
      });
      setMode('test');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function resetTest() {
    setTest(null);
    setResult(null);
    setMode('practice');
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-mark">SB</div>
        <div>
          <div className="brand">Study Buddy</div>
          <div className="tagline">Practice smarter. Prepare better.</div>
        </div>
        <div className={`backend-pill ${backendStatus}`}>
          <span className="status-dot" />
          {backendStatus === 'connected' ? 'Backend connected' : backendStatus === 'checking' ? 'Connecting…' : 'Backend offline'}
        </div>
        <div className="stage-pill">Stage 1 · Question Bank</div>
      </header>

      <main className="container">
        {mode !== 'test' && !result && (
          <SelectionPanel
            exam={exam} setExam={setExam}
            subject={subject} setSubject={setSubject}
            chapter={chapter} setChapter={setChapter}
            topic={topic} setTopic={setTopic}
            difficulty={difficulty} setDifficulty={setDifficulty}
            questionType={questionType} setQuestionType={setQuestionType}
            exams={exams} subjects={subjects} chapters={chapters} topics={topics}
            loading={loading} loadQuestions={loadQuestions} startTest={startTest}
            disabled={backendStatus !== 'connected'}
          />
        )}

        {error && (
          <div className="error">
            <span>{error}</span>
            <button className="error-close" onClick={() => setError('')} aria-label="Dismiss">×</button>
          </div>
        )}

        {mode === 'practice' && !result && (
          <Practice
            questions={questions}
            totalQuestions={totalQuestions}
            solutions={solutions}
            setSolutions={setSolutions}
            setError={setError}
          />
        )}

        {mode === 'test' && test && (
          <TestRunner
            test={test}
            setTest={setTest}
            onFinish={(data) => { setResult(data); setTest(null); setMode('practice'); }}
            setError={setError}
          />
        )}

        {result && <Results result={result} onAgain={resetTest} />}
      </main>

      <footer>Study Buddy · 1,833-question validated bank · Practice &amp; timed tests</footer>
    </div>
  );
}

function SelectionPanel({ exam, setExam, subject, setSubject, chapter, setChapter, topic, setTopic, difficulty, setDifficulty, questionType, setQuestionType, exams, subjects, chapters, topics, loading, loadQuestions, startTest, disabled }) {
  return (
    <section className="hero-area">
      <div className="hero">
        <div>
          <span className="eyebrow">COMPETITIVE EXAM PREP</span>
          <h1>Practice with purpose.</h1>
          <p>Choose your exam, filter the question bank, practice with solutions, or start a timed test.</p>
        </div>
        <div className="hero-stat"><strong>1,833</strong><span>questions &amp; solutions</span></div>
      </div>

      <section className="filters card">
        <div className="section-title">
          <div><span className="step">01</span><h2>Choose your test</h2></div>
          <span className="muted">Practice or start a timed test</span>
        </div>

        <div className="filter-grid">
          <Select label="Exam" value={exam} onChange={setExam} options={exams} placeholder="Choose exam" labels={EXAM_LABELS} disabled={disabled} />
          <Select label="Subject" value={subject} onChange={setSubject} options={subjects} placeholder="All subjects" disabled={disabled || !exam} />
          <Select label="Chapter" value={chapter} onChange={setChapter} options={chapters} placeholder="All chapters" disabled={disabled || !subject} />
          <Select label="Topic" value={topic} onChange={setTopic} options={topics} placeholder={chapter ? 'All topics' : 'Choose chapter first'} disabled={disabled || !chapter} />
          <Select label="Difficulty" value={difficulty} onChange={setDifficulty} options={['Very Easy', 'Easy', 'Medium', 'Hard', 'Very Hard', 'Extreme']} placeholder="Any level" disabled={disabled} />
          <Select label="Question type" value={questionType} onChange={setQuestionType} options={['MCQ', 'Multiple Correct', 'Numerical', 'Integer', 'Assertion Reason', 'Grid-In', 'Subjective']} placeholder="Any type" disabled={disabled} />
        </div>

        <div className="button-row">
          <button className="secondary" onClick={loadQuestions} disabled={!exam || loading || disabled}>
            {loading ? 'Loading…' : 'Practice questions'}
          </button>
          <button className="primary" onClick={startTest} disabled={!exam || loading || disabled}>
            {loading ? 'Starting…' : 'Start timed test →'}
          </button>
        </div>
      </section>
    </section>
  );
}

function Select({ label, value, onChange, options, placeholder, disabled, labels = {} }) {
  return (
    <label>
      {label}
      <select value={value} onChange={e => onChange(e.target.value)} disabled={disabled}>
        <option value="">{placeholder}</option>
        {options.map(option => <option key={option} value={option}>{labels[option] || option}</option>)}
      </select>
    </label>
  );
}

function Practice({ questions, totalQuestions, solutions, setSolutions, setError }) {
  const [loadingId, setLoadingId] = useState('');

  async function showSolution(id) {
    setLoadingId(id);
    setError('');
    try {
      const data = await api.getQuestionSolution(id);
      setSolutions(current => ({ ...current, [id]: data.solution }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingId('');
    }
  }

  return (
    <section className="questions-section">
      <div className="section-heading">
        <div><span className="step">02</span><h2>Practice</h2></div>
        <span className="count">{questions.length} shown · {totalQuestions} matching</span>
      </div>

      {questions.length === 0 ? (
        <div className="empty card">
          <div className="empty-icon">✦</div>
          <h3>Ready when you are.</h3>
          <p>Select an exam and load practice questions, or start a timed test.</p>
        </div>
      ) : (
        <div className="question-list">
          {questions.map((question, index) => (
            <QuestionCard
              key={question.question_id}
              question={question}
              index={index}
              solution={solutions[question.question_id]}
              loading={loadingId === question.question_id}
              onSolution={showSolution}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function QuestionCard({ question, index, solution, loading, onSolution }) {
  const options = question.options || [];
  return (
    <article className="question-card card">
      <div className="question-meta">
        <span>Q{index + 1}</span>
        <span>{question.subject}</span>
        <span>{question.chapter}</span>
        {question.difficulty && <span>{question.difficulty}</span>}
      </div>
      <h3>{question.question_text || question.question}</h3>

      {options.length > 0 && (
        <div className="options">
          {options.map((option, i) => (
            <div className="option" key={i}>
              <span>{String.fromCharCode(65 + i)}</span>
              <div>{typeof option === 'string' ? option : option.text}</div>
            </div>
          ))}
        </div>
      )}

      <div className="question-actions">
        <span className="qid">{question.question_id}</span>
        <button className="secondary" onClick={() => onSolution(question.question_id)} disabled={loading}>
          {loading ? 'Loading…' : solution ? 'Solution shown' : 'Show solution'}
        </button>
      </div>

      {solution && <Solution solution={solution} />}
    </article>
  );
}

function Solution({ solution }) {
  const explanation = solution.solution_text || solution.explanation || solution.solution || solution.steps || solution.answer_explanation;
  return (
    <div className="solution">
      <div className="solution-title">✓ Worked solution</div>
      {solution.final_answer && <div className="final-answer"><strong>Answer:</strong> {solution.final_answer}</div>}
      {explanation && <p>{typeof explanation === 'string' ? explanation : JSON.stringify(explanation)}</p>}
      {Array.isArray(solution.tips) && solution.tips.length > 0 && (
        <div className="solution-tips">
          <strong>Tips</strong>
          <ul>{solution.tips.map((tip, index) => <li key={index}>{tip}</li>)}</ul>
        </div>
      )}
    </div>
  );
}

function TestRunner({ test, setTest, onFinish, setError }) {
  const [seconds, setSeconds] = useState(test.duration_minutes * 60);
  const [submitting, setSubmitting] = useState(false);
  const [freeAnswer, setFreeAnswer] = useState('');

  const q = test.questions[test.index];
  const options = q?.options || [];
  const selected = test.answers[q?.question_id];

  useEffect(() => {
    if (submitting) return undefined;
    const timer = setInterval(() => setSeconds(value => Math.max(0, value - 1)), 1000);
    return () => clearInterval(timer);
  }, [submitting]);

  useEffect(() => {
    if (seconds === 0 && !submitting) submit(test.answers);
  }, [seconds, submitting]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    setFreeAnswer(selected || '');
  }, [q?.question_id, selected]);

  function choose(answer) {
    setTest(current => ({
      ...current,
      answers: { ...current.answers, [q.question_id]: answer },
    }));
  }

  async function submit(answersToSubmit = test.answers) {
    if (submitting) return;
    setSubmitting(true);
    setError('');
    try {
      const data = await api.submitTest(test.test_id, answersToSubmit);
      onFinish(data);
    } catch (e) {
      setSubmitting(false);
      setError(e.message);
    }
  }

  function saveFreeAnswer() {
    choose(freeAnswer.trim());
  }

  if (!q) return <div className="error">This test contains no questions.</div>;

  return (
    <section className="test-shell">
      <div className="test-top card">
        <div><span className="eyebrow">TIMED TEST</span><h2>{test.exam}</h2></div>
        <div className={seconds < 60 ? 'timer danger' : 'timer'}>⏱ {Math.floor(seconds / 60)}:{String(seconds % 60).padStart(2, '0')}</div>
      </div>

      <div className="test-progress">
        <span>Question {test.index + 1} of {test.questions.length}</span>
        <div><span style={{ width: `${((test.index + 1) / test.questions.length) * 100}%` }} /></div>
      </div>

      <article className="test-question card">
        <div className="question-meta">
          <span>{q.subject}</span><span>{q.chapter}</span><span>{q.difficulty}</span>
        </div>
        <h3>{q.question_text || q.question}</h3>

        {options.length > 0 ? (
          <div className="test-options">
            {options.map((option, i) => {
              const text = typeof option === 'string' ? option : option.text;
              return (
                <button
                  key={i}
                  className={selected === text ? 'test-option selected' : 'test-option'}
                  onClick={() => choose(text)}
                  disabled={submitting}
                >
                  <span>{String.fromCharCode(65 + i)}</span>{text}
                </button>
              );
            })}
          </div>
        ) : (
          <div className="free-answer">
            <input
              value={freeAnswer}
              onChange={e => setFreeAnswer(e.target.value)}
              onBlur={saveFreeAnswer}
              placeholder="Enter your answer"
              disabled={submitting}
            />
            <button className="secondary" onClick={saveFreeAnswer} disabled={submitting}>Save answer</button>
          </div>
        )}
      </article>

      <div className="test-nav">
        <button className="secondary" disabled={test.index === 0 || submitting} onClick={() => setTest(current => ({ ...current, index: current.index - 1 }))}>← Previous</button>
        {test.index < test.questions.length - 1 ? (
          <button className="primary" disabled={submitting} onClick={() => setTest(current => ({ ...current, index: current.index + 1 }))}>Next →</button>
        ) : (
          <button className="primary" disabled={submitting} onClick={() => submit(test.answers)}>{submitting ? 'Submitting…' : 'Submit test'}</button>
        )}
      </div>
    </section>
  );
}

function Results({ result, onAgain }) {
  const pct = result.total ? Math.round((result.correct / result.total) * 100) : 0;
  const statusText = useMemo(() => ({ correct: 'Correct', wrong: 'Wrong', unanswered: 'Unanswered' }), []);

  return (
    <section className="results">
      <div className="result-hero card">
        <span className="eyebrow">TEST COMPLETE</span>
        <div className="score">{result.score}</div>
        <div className="score-label">marks</div>
        <div className="result-grid">
          <Stat value={result.correct} label="Correct" />
          <Stat value={result.wrong} label="Wrong" />
          <Stat value={result.unanswered} label="Unanswered" />
          <Stat value={`${pct}%`} label="Accuracy" />
        </div>
      </div>

      <div className="result-actions"><button className="primary" onClick={onAgain}>Back to practice</button></div>

      <div className="card result-details">
        <h2>Question review</h2>
        {result.results.map((item, index) => (
          <div className="review-row" key={item.question_id}>
            <span>Q{index + 1}</span>
            <strong className={item.status}>{statusText[item.status] || item.status}</strong>
            <span>{item.selected_answer || '—'}</span>
            <span className="review-answer">Answer: {item.correct_answer}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function Stat({ value, label }) {
  return <div><strong>{value}</strong><span>{label}</span></div>;
}

export default App;
