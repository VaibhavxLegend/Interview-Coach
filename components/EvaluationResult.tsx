'use client';

import { Evaluation } from '@/lib/types';

interface EvaluationResultProps {
  evaluation: Evaluation;
  answer: string;
}

export default function EvaluationResult({ evaluation, answer }: EvaluationResultProps) {
  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    if (score >= 4) return 'text-orange-600';
    return 'text-red-600';
  };

  const getProgressBarColor = (score: number) => {
    if (score >= 8) return 'bg-green-500';
    if (score >= 6) return 'bg-yellow-500';
    if (score >= 4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const ScoreBar = ({ label, score }: { label: string; score: number }) => (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="font-medium text-gray-700">{label}</span>
        <span className={`font-bold ${getScoreColor(score)}`}>{score}/10</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`h-3 rounded-full transition-all duration-500 ${getProgressBarColor(score)}`}
          style={{ width: `${(score / 10) * 100}%` }}
        />
      </div>
    </div>
  );

  return (
    <div className="space-y-6 bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-800 border-b pb-2">Evaluation Results</h2>
      
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
        <div className="text-center">
          <p className="text-gray-600 font-medium mb-2">Overall Score</p>
          <p className={`text-6xl font-bold ${getScoreColor(evaluation.overallScore)}`}>
            {evaluation.overallScore}/10
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-800">Detailed Scores</h3>
        <ScoreBar label="Clarity" score={evaluation.clarity} />
        <ScoreBar label="Conciseness" score={evaluation.conciseness} />
        <ScoreBar label="Confidence" score={evaluation.confidence} />
        <ScoreBar label="Technical Depth" score={evaluation.technicalDepth} />
      </div>

      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Feedback</h3>
        <p className="text-gray-700">{evaluation.feedback}</p>
      </div>

      <div className="bg-yellow-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Suggestions for Improvement</h3>
        <ul className="list-disc list-inside space-y-2">
          {evaluation.improvements.map((improvement, index) => (
            <li key={index} className="text-gray-700">{improvement}</li>
          ))}
        </ul>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Your Answer</h3>
        <p className="text-gray-700 whitespace-pre-wrap">{answer}</p>
        <p className="text-sm text-gray-500 mt-2">
          Word count: {answer.split(/\s+/).length}
        </p>
      </div>
    </div>
  );
}
