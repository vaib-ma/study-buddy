const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001').replace(/\/$/, '');

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {}),
    },
  });

  const contentType = response.headers.get('content-type') || '';
  const body = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof body === 'object' && body?.detail
      ? body.detail
      : `Request failed (${response.status})`;
    throw new Error(detail);
  }

  return body;
}

export const api = {
  health: () => request('/health'),
  getExams: () => request('/exams'),
  getSubjects: (exam) => request(`/subjects?exam=${encodeURIComponent(exam)}`),
  getChapters: (exam, subject) => request(`/chapters?exam=${encodeURIComponent(exam)}&subject=${encodeURIComponent(subject)}`),
  getQuestions: (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') params.set(key, value);
    });
    return request(`/questions?${params.toString()}`);
  },
  getQuestionSolution: (questionId) => request(`/questions/${encodeURIComponent(questionId)}/solution`),
  createTest: (payload) => request('/tests', { method: 'POST', body: JSON.stringify(payload) }),
  getTest: (testId) => request(`/tests/${encodeURIComponent(testId)}`),
  submitTest: (testId, answers) => request(`/tests/${encodeURIComponent(testId)}/submit`, {
    method: 'POST',
    body: JSON.stringify({ answers }),
  }),
};

export { API_BASE_URL };
