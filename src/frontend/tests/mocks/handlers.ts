import { http, HttpResponse } from "msw";

// Default happy-path handlers, matching the real endpoints each service
// calls (see src/services/*.ts). Individual tests override specific
// routes via `server.use(...)` for error/edge cases — see msw.setup.ts.
const API_BASE = "http://localhost:8000/api/v1";

export const handlers = [
  http.get(`${API_BASE}/auth/me`, () =>
    HttpResponse.json({
      id: "user-1",
      email: "student@example.com",
      full_name: "Test Student",
      role: "student",
    })
  ),

  http.post(`${API_BASE}/auth/login`, () =>
    HttpResponse.json({ access_token: "fake.jwt.token", token_type: "bearer" })
  ),

  http.post(`${API_BASE}/auth/register`, () =>
    HttpResponse.json(
      { access_token: "fake.jwt.token", token_type: "bearer" },
      { status: 201 }
    )
  ),

  http.post(`${API_BASE}/auth/logout`, () => new HttpResponse(null, { status: 204 })),

  http.get(`${API_BASE}/chat/sessions/:sessionId`, ({ params }) =>
    HttpResponse.json({
      id: params.sessionId,
      student_id: "user-1",
      task_id: "task-1",
      title: "Test session",
      is_active: true,
      created_at: new Date().toISOString(),
      ended_at: null,
    })
  ),

  http.get(`${API_BASE}/chat/sessions/:sessionId/history`, () =>
    HttpResponse.json({ messages: [] })
  ),

  http.post(`${API_BASE}/chat/sessions/:sessionId/auto-end`, () =>
    new HttpResponse(null, { status: 204 })
  ),

  http.get(`${API_BASE}/chat/sessions/task/:taskId`, () => HttpResponse.json([])),

  http.get(`${API_BASE}/classes/`, () => HttpResponse.json([])),
  http.get(`${API_BASE}/courses/`, () => HttpResponse.json([])),
  http.get(`${API_BASE}/courses/all`, () => HttpResponse.json([])),
  http.get(`${API_BASE}/analytics/me`, () =>
    HttpResponse.json({ total_sessions: 0, total_messages: 0 })
  ),
  http.get(`${API_BASE}/enrollments/me`, () => HttpResponse.json([])),
];
