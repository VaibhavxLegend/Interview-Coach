'use client';

import { useState, useEffect } from 'react';
import { InterviewSession } from '@/lib/types';
import { getSessions } from '@/lib/services/storage';

export default function HistoryView() {
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<InterviewSession | null>(null);

  useEffect(() => {
    setSessions(getSessions());
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    if (score >= 4) return 'text-orange-600';
    return 'text-red-600';
  };

  if (sessions.length === 0) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-lg text-center">
        <p className="text-gray-600">No practice sessions yet. Start practicing to see your history!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Practice History</h2>
        <div className="space-y-3">
          {sessions.map((session) => (
            <div
              key={session.id}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => setSelectedSession(session)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="font-medium text-gray-800 line-clamp-2">{session.question}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {new Date(session.timestamp).toLocaleString()}
                  </p>
                </div>
                <div className="ml-4">
                  <span className={`text-2xl font-bold ${getScoreColor(session.evaluation.overallScore)}`}>
                    {session.evaluation.overallScore}/10
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedSession && (
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-xl font-bold text-gray-800">Session Details</h3>
            <button
              onClick={() => setSelectedSession(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <p className="font-medium text-gray-700">Question:</p>
              <p className="text-gray-800">{selectedSession.question}</p>
            </div>

            <div>
              <p className="font-medium text-gray-700">Your Answer:</p>
              <p className="text-gray-600 bg-gray-50 p-3 rounded">{selectedSession.answer}</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded">
                <p className="text-sm text-gray-600">Clarity</p>
                <p className={`text-2xl font-bold ${getScoreColor(selectedSession.evaluation.clarity)}`}>
                  {selectedSession.evaluation.clarity}
                </p>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded">
                <p className="text-sm text-gray-600">Conciseness</p>
                <p className={`text-2xl font-bold ${getScoreColor(selectedSession.evaluation.conciseness)}`}>
                  {selectedSession.evaluation.conciseness}
                </p>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded">
                <p className="text-sm text-gray-600">Confidence</p>
                <p className={`text-2xl font-bold ${getScoreColor(selectedSession.evaluation.confidence)}`}>
                  {selectedSession.evaluation.confidence}
                </p>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded">
                <p className="text-sm text-gray-600">Tech Depth</p>
                <p className={`text-2xl font-bold ${getScoreColor(selectedSession.evaluation.technicalDepth)}`}>
                  {selectedSession.evaluation.technicalDepth}
                </p>
              </div>
            </div>

            <div>
              <p className="font-medium text-gray-700 mb-2">Feedback:</p>
              <p className="text-gray-600 bg-blue-50 p-3 rounded">{selectedSession.evaluation.feedback}</p>
            </div>

            <div>
              <p className="font-medium text-gray-700 mb-2">Improvements:</p>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {selectedSession.evaluation.improvements.map((imp, idx) => (
                  <li key={idx}>{imp}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
