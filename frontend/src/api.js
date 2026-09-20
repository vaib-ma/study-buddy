const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: options.body ? { 'Content-Type': 'application/json' } : undefined,
    ...options,
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return response.json();
}

export const api = {
  getExams: () => request('/exams'),
  getSubjects: (exam) => request(`/subjects?exam=${encodeURIComponent(exam)}`),
  getChapters: (exam, subject) => request(`/chapters?exam=${encodeURIComponent(exam)}&subject=${encodeURIComponent(subject)}`),
  getQuestions: (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => { if (value) params.set(key, value); });
    return request(`/questions?${params.toString()}`);
  },
  getQuestionSolution: (questionId) => request(`/questions/${encodeURIComponent(questionId)}/solution`),
  createTest: (payload) => request('/tests', { method: 'POST', body: JSON.stringify(payload) }),
  submitTest: (testId, answers) => request(`/tests/${encodeURIComponent(testId)}/submit`, {
    method: 'POST', body: JSON.stringify({ answers }),
  }),
};

export { API_BASE_URL };
