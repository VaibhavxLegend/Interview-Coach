const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export type StartResponse = { session_id: number; question: string };
export type Evaluation = {
  clarity: number;
  conciseness: number;
  confidence: number;
  technical_depth: number;
  overall: number;
  feedback: string;
  suggestions: string;
  friendly?: string;
};
export type AnswerResult = { evaluation: Evaluation; next_question: string };

export async function startSession(role = "software engineer", seniority = "mid"): Promise<StartResponse> {
  const res = await fetch(`${API_BASE}/api/sessions/start`, { method: "POST" });
  if (!res.ok) throw new Error(`startSession failed: ${res.status}`);
  return res.json();
}

export async function submitAnswer(sessionId: number, question: string, answer: string, transcript?: string): Promise<AnswerResult> {
  const res = await fetch(`${API_BASE}/api/qa/${sessionId}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, answer, transcript }),
  });
  if (!res.ok) throw new Error(`submitAnswer failed: ${res.status}`);
  return res.json();
}

export async function completeSession(sessionId: number, email?: string): Promise<{ status: string; summary: string }>{
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) throw new Error(`completeSession failed: ${res.status}`);
  return res.json();
}

export { API_BASE };
