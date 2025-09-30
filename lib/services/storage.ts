import { InterviewSession } from '../types';

const STORAGE_KEY = 'interview_sessions';

export function saveSession(session: InterviewSession): void {
  if (typeof window === 'undefined') return;
  
  const sessions = getSessions();
  sessions.push(session);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
}

export function getSessions(): InterviewSession[] {
  if (typeof window === 'undefined') return [];
  
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : [];
}

export function clearSessions(): void {
  if (typeof window === 'undefined') return;
  
  localStorage.removeItem(STORAGE_KEY);
}

export function getSessionById(id: string): InterviewSession | undefined {
  const sessions = getSessions();
  return sessions.find(s => s.id === id);
}
