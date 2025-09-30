export interface Question {
  id: string;
  category: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  question: string;
  topic: string;
}

export interface EvaluationCriteria {
  clarity: number; // 0-10
  conciseness: number; // 0-10
  confidence: number; // 0-10
  technicalDepth: number; // 0-10
}

export interface Evaluation extends EvaluationCriteria {
  overallScore: number;
  feedback: string;
  improvements: string[];
}

export interface InterviewSession {
  id: string;
  questionId: string;
  question: string;
  answer: string;
  evaluation: Evaluation;
  timestamp: number;
}
