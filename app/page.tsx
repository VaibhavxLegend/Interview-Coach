'use client';

import { useState } from 'react';
import QuestionDisplay from '@/components/QuestionDisplay';
import AnswerInput from '@/components/AnswerInput';
import EvaluationResult from '@/components/EvaluationResult';
import HistoryView from '@/components/HistoryView';
import { getRandomQuestion } from '@/lib/data/questions';
import { evaluateAnswer } from '@/lib/services/evaluation';
import { saveSession } from '@/lib/services/storage';
import { Question, Evaluation } from '@/lib/types';

type View = 'practice' | 'history';

export default function Home() {
  const [view, setView] = useState<View>('practice');
  const [question, setQuestion] = useState<Question>(() => getRandomQuestion());
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState<string>('');
  const [isEvaluating, setIsEvaluating] = useState(false);

  const handleNewQuestion = () => {
    setQuestion(getRandomQuestion());
    setEvaluation(null);
    setCurrentAnswer('');
  };

  const handleSubmitAnswer = async (answer: string) => {
    setIsEvaluating(true);
    setCurrentAnswer(answer);

    // Simulate evaluation delay for better UX
    await new Promise(resolve => setTimeout(resolve, 1000));

    const result = evaluateAnswer(answer);
    setEvaluation(result);

    // Save session
    saveSession({
      id: Date.now().toString(),
      questionId: question.id,
      question: question.question,
      answer,
      evaluation: result,
      timestamp: Date.now(),
    });

    setIsEvaluating(false);
  };

  const handleTryAgain = () => {
    setEvaluation(null);
    setCurrentAnswer('');
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Interview Coach</h1>
              <p className="text-sm text-gray-600 mt-1">Practice and improve your interview skills</p>
            </div>
            <nav className="flex gap-2">
              <button
                onClick={() => setView('practice')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  view === 'practice'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Practice
              </button>
              <button
                onClick={() => setView('history')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  view === 'history'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                History
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {view === 'practice' ? (
          <div className="space-y-6">
            <QuestionDisplay question={question} onNewQuestion={handleNewQuestion} />

            {!evaluation ? (
              <div className="bg-white p-6 rounded-lg shadow-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Your Answer</h3>
                <AnswerInput onSubmit={handleSubmitAnswer} isLoading={isEvaluating} />
              </div>
            ) : (
              <>
                <EvaluationResult evaluation={evaluation} answer={currentAnswer} />
                <div className="flex gap-4">
                  <button
                    onClick={handleTryAgain}
                    className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                  >
                    Try Same Question Again
                  </button>
                  <button
                    onClick={handleNewQuestion}
                    className="flex-1 bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                  >
                    Next Question
                  </button>
                </div>
              </>
            )}

            {/* Information Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">💡 Tips for Success</h3>
              <ul className="space-y-2 text-blue-800">
                <li>• Structure your answer with a clear beginning, middle, and end</li>
                <li>• Use specific examples and technical terms when relevant</li>
                <li>• Keep your answer concise (50-150 words is often ideal)</li>
                <li>• Speak or write confidently - avoid uncertain phrases</li>
                <li>• Use the microphone for speech practice or type your answer</li>
              </ul>
            </div>
          </div>
        ) : (
          <HistoryView />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-gray-600 text-sm">
            Interview Coach - AI-powered interview practice platform
          </p>
        </div>
      </footer>
    </div>
  );
}
