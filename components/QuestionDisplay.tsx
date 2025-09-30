'use client';

import { Question } from '@/lib/types';

interface QuestionDisplayProps {
  question: Question;
  onNewQuestion: () => void;
}

export default function QuestionDisplay({ question, onNewQuestion }: QuestionDisplayProps) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy':
        return 'bg-green-100 text-green-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg space-y-4">
      <div className="flex items-start justify-between">
        <div className="space-y-2 flex-1">
          <div className="flex gap-2 flex-wrap">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
              {question.category}
            </span>
            <span className={`px-3 py-1 text-sm font-medium rounded-full ${getDifficultyColor(question.difficulty)}`}>
              {question.difficulty}
            </span>
            <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm font-medium rounded-full">
              {question.topic}
            </span>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mt-4">
            {question.question}
          </h2>
        </div>
      </div>
      
      <div className="pt-4 border-t">
        <button
          onClick={onNewQuestion}
          className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
        >
          Get New Question
        </button>
      </div>
    </div>
  );
}
