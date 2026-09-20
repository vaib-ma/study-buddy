import { useEffect, useState } from 'react';
import { api } from './api';

const EXAM_LABELS = {
  'JEE Main': 'JEE Main', 'JEE Advanced': 'JEE Advanced', KCET: 'KCET',
  'MHT-CET': 'MHT-CET', BITSAT: 'BITSAT', GAKAO: 'GAKAO', SAT: 'SAT',
};

function App() {
  const [mode, setMode] = useState('practice');
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
  const [error, setError] = useState('');
  const [test, setTest] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => { api.getExams().then(d => setExams(d.exams || [])).catch(e => setError(e.message)); }, []);
  useEffect(() => {
    setSubject(''); setChapter(''); setChapters([]); setQuestions([]); setSolutions({});
    if (!exam) return setSubjects([]);
    api.getSubjects(exam).then(d => setSubjects(d.subjects || [])).catch(e => setError(e.message));
  }, [exam]);
  useEffect(() => {
    setChapter(''); setQuestions([]); setSolutions({});
    if (!exam || !subject) return setChapters([]);
    api.getChapters(exam, subject).then(d => setChapters(d.chapters || [])).catch(e => setError(e.message));
  }, [exam, subject]);

  async function loadQuestions() {
    setLoading(true); setError(''); setSolutions({});
    try { const d = await api.getQuestions({ exam, subject, chapter, difficulty, limit: 20 }); setQuestions(d.questions || []); }
    catch (e) { setError(e.message); } finally { setLoading(false); }
  }

  async function startTest() {
    setLoading(true); setError(''); setResult(null);
    try {
      const d = await api.createTest({ exam, subject: subject || null, chapter: chapter || null, difficulty: difficulty || null, question_count: 10, duration_minutes: 15 });
      setTest({ ...d, answers: {}, index: 0, startedAt: Date.now() }); setMode('test');
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  }

  function resetTest() { setTest(null); setResult(null); setMode('practice'); }

  return <div className="app-shell">
    <header className="topbar"><div className="brand-mark">SB</div><div><div className="brand">Study Buddy</div><div className="tagline">Practice smarter. Prepare better.</div></div><div className="stage-pill">Stage 4 · Test Engine</div></header>
    <main className="container">
      {mode !== 'test' && !result && <SelectionPanel {...{exam,setExam,subject,setSubject,chapter,setChapter,difficulty,setDifficulty,exams,subjects,chapters,loading,loadQuestions,startTest}} />}
      {error && <div className="error">{error}</div>}
      {mode === 'practice' && !result && <Practice questions={questions} solutions={solutions} setSolutions={setSolutions} setError={setError} />}
      {mode === 'test' && test && <TestRunner test={test} setTest={setTest} onFinish={setResult} setError={setError} />}
      {result && <Results result={result} onAgain={resetTest} />}
    </main>
    <footer>Study Buddy · Original exam-style practice content · Stage 4 test engine</footer>
  </div>;
}

function SelectionPanel({ exam, setExam, subject, setSubject, chapter, setChapter, difficulty, setDifficulty, exams, subjects, chapters, loading, loadQuestions, startTest }) {
  return <section className="hero-area">
    <div className="hero"><div><span className="eyebrow">COMPETITIVE EXAM PREP</span><h1>Practice with purpose.</h1><p>Build a practice set or start a timed test from the same question bank.</p></div><div className="hero-stat"><strong>100</strong><span>original questions</span></div></div>
    <section className="filters card">
      <div className="section-title"><div><span className="step">01</span><h2>Choose your test</h2></div><span className="muted">10 questions · 15 minutes</span></div>
      <div className="filter-grid">
        <Select label="Exam" value={exam} onChange={setExam} options={exams} placeholder="Choose exam" labels={EXAM_LABELS}/>
        <Select label="Subject" value={subject} onChange={setSubject} options={subjects} placeholder="All subjects" disabled={!exam}/>
        <Select label="Chapter" value={chapter} onChange={setChapter} options={chapters} placeholder="All chapters" disabled={!subject}/>
        <Select label="Difficulty" value={difficulty} onChange={setDifficulty} options={['Easy','Medium','Hard']} placeholder="Any level"/>
      </div>
      <div className="button-row"><button className="secondary" onClick={loadQuestions} disabled={!exam || loading}>Practice questions</button><button className="primary" onClick={startTest} disabled={!exam || loading}>{loading ? 'Starting…' : 'Start timed test →'}</button></div>
    </section>
  </section>;
}

function Select({ label, value, onChange, options, placeholder, disabled, labels = {} }) {
  return <label>{label}<select value={value} onChange={e => onChange(e.target.value)} disabled={disabled}><option value="">{placeholder}</option>{options.map(o => <option key={o} value={o}>{labels[o] || o}</option>)}</select></label>;
}

function Practice({ questions, solutions, setSolutions, setError }) {
  const [loadingId, setLoadingId] = useState('');
  async function showSolution(id) {
    setLoadingId(id); setError('');
    try { const d = await api.getQuestionSolution(id); setSolutions(s => ({ ...s, [id]: d.solution })); }
    catch (e) { setError(e.message); } finally { setLoadingId(''); }
  }
  return <section className="questions-section"><div className="section-heading"><div><span className="step">02</span><h2>Practice</h2></div><span className="count">{questions.length} loaded</span></div>
    {questions.length === 0 ? <div className="empty card"><div className="empty-icon">✦</div><h3>Ready when you are.</h3><p>Select an exam and load practice questions, or start a timed test.</p></div> :
      <div className="question-list">{questions.map((q,i) => <QuestionCard key={q.question_id} question={q} index={i} solution={solutions[q.question_id]} loading={loadingId === q.question_id} onSolution={showSolution}/>)}</div>}
  </section>;
}

function QuestionCard({ question, index, solution, loading, onSolution }) {
  const options = question.options || [];
  return <article className="question-card card"><div className="question-meta"><span>Q{index+1}</span><span>{question.subject}</span><span>{question.chapter}</span>{question.difficulty && <span>{question.difficulty}</span>}</div>
    <h3>{question.question_text || question.question}</h3>
    {options.length > 0 && <div className="options">{options.map((o,i) => <div className="option" key={i}><span>{String.fromCharCode(65+i)}</span><div>{typeof o === 'string' ? o : o.text}</div></div>)}</div>}
    <div className="question-actions"><span className="qid">{question.question_id}</span><button className="secondary" onClick={() => onSolution(question.question_id)} disabled={loading}>{loading ? 'Loading…' : solution ? 'Solution shown' : 'Show solution'}</button></div>
    {solution && <Solution solution={solution}/>}
  </article>;
}

function Solution({ solution }) {
  const explanation = solution.explanation || solution.solution || solution.steps || solution.answer_explanation;
  return <div className="solution"><div className="solution-title">✓ Worked solution</div>{solution.final_answer && <div className="final-answer"><strong>Answer:</strong> {solution.final_answer}</div>}<p>{typeof explanation === 'string' ? explanation : JSON.stringify(explanation)}</p></div>;
}

function TestRunner({ test, setTest, onFinish, setError }) {
  const [seconds, setSeconds] = useState(test.duration_minutes * 60);
  const q = test.questions[test.index];
  useEffect(() => { const id = setInterval(() => setSeconds(s => Math.max(0,s-1)),1000); return () => clearInterval(id); }, []);
  useEffect(() => { if (seconds === 0) submit(); }, [seconds]);
  function choose(answer) { setTest(t => ({...t, answers: {...t.answers, [q.question_id]: answer}})); }
  async function submit() {
    try { const d = await api.submitTest(test.test_id, test.answers); onFinish(d); }
    catch (e) { setError(e.message); }
  }
  const selected = test.answers[q.question_id];
  const letters = q.options || [];
  return <section className="test-shell">
    <div className="test-top card"><div><span className="eyebrow">TIMED TEST</span><h2>{test.exam}</h2></div><div className={seconds < 60 ? 'timer danger' : 'timer'}>⏱ {Math.floor(seconds/60)}:{String(seconds%60).padStart(2,'0')}</div></div>
    <div className="test-progress"><span>Question {test.index+1} of {test.questions.length}</span><div><span style={{width: `${((test.index+1)/test.questions.length)*100}%`}}/></div></div>
    <article className="test-question card"><div className="question-meta"><span>{q.subject}</span><span>{q.chapter}</span><span>{q.difficulty}</span></div><h3>{q.question_text || q.question}</h3>
      <div className="test-options">{letters.map((o,i) => { const text = typeof o === 'string' ? o : o.text; return <button key={i} className={selected === text ? 'test-option selected' : 'test-option'} onClick={() => choose(text)}><span>{String.fromCharCode(65+i)}</span>{text}</button>; })}</div>
    </article>
    <div className="test-nav"><button className="secondary" disabled={test.index===0} onClick={() => setTest(t=>({...t,index:t.index-1}))}>← Previous</button>{test.index < test.questions.length-1 ? <button className="primary" onClick={() => setTest(t=>({...t,index:t.index+1}))}>Next →</button> : <button className="primary" onClick={submit}>Submit test</button>}</div>
  </section>;
}

function Results({ result, onAgain }) {
  const pct = result.total ? Math.round((result.correct/result.total)*100) : 0;
  return <section className="results"><div className="result-hero card"><span className="eyebrow">TEST COMPLETE</span><div className="score">{result.score}</div><div className="score-label">marks</div><div className="result-grid"><Stat value={result.correct} label="Correct"/><Stat value={result.wrong} label="Wrong"/><Stat value={result.unanswered} label="Unanswered"/><Stat value={`${pct}%`} label="Accuracy"/></div></div>
    <div className="result-actions"><button className="primary" onClick={onAgain}>Back to practice</button></div>
    <div className="card result-details"><h2>Question review</h2>{result.results.map((r,i)=><div className="review-row" key={r.question_id}><span>Q{i+1}</span><strong className={r.status}>{r.status}</strong><span>{r.selected_answer || '—'}</span><span className="review-answer">Answer: {r.correct_answer}</span></div>)}</div>
  </section>;
}
function Stat({value,label}) { return <div><strong>{value}</strong><span>{label}</span></div>; }

export default App;
