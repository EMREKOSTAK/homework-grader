'use client';

import { useState } from 'react';
import { GradingResult } from '@/types';
import { CircularScore } from './ScoreDisplay';
import RubricSection from './RubricSection';
import { formatCheckName, getPriorityColor } from '@/lib/api';

interface ResultsDisplayProps {
  result: GradingResult;
  onReset: () => void;
}

export default function ResultsDisplay({ result, onReset }: ResultsDisplayProps) {
  const [copiedJson, setCopiedJson] = useState(false);

  const handleCopyJson = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(result, null, 2));
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header with total score */}
      <div className="card">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="text-center md:text-left">
            <h2 className="text-2xl font-bold text-gray-900">
              Degerlendirme Sonucu
            </h2>
            <p className="text-gray-600 mt-1">
              {result.on_time_submitted
                ? 'Zamaninda teslim edildi (+10 puan)'
                : 'Zamaninda teslim bilgisi girilmedi'}
            </p>
          </div>
          <CircularScore score={result.total_score} maxScore={100} size={140} />
        </div>

        {/* Overall Evaluation */}
        {result.overall_evaluation && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Genel Degerlendirme</h3>
            <p className="text-gray-700">{result.overall_evaluation}</p>
          </div>
        )}
      </div>

      {/* Rubric Scores */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-900">Rubrik Puanlari</h3>
        <div className="space-y-4">
          {result.rubric_scores.map((score, idx) => (
            <RubricSection key={idx} rubricScore={score} />
          ))}
        </div>
      </div>

      {/* Deterministic Checks */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          Otomatik Kontroller
        </h3>
        <div className="space-y-3">
          {result.deterministic_checks.map((check, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                {check.passed ? (
                  <span className="w-6 h-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </span>
                ) : (
                  <span className="w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </span>
                )}
                <div>
                  <p className="font-medium text-gray-900">
                    {formatCheckName(check.check_name)}
                  </p>
                  {check.details && (
                    <p className="text-sm text-gray-500">{check.details}</p>
                  )}
                </div>
              </div>
              <span className="text-sm font-medium text-gray-700">
                {check.score.toFixed(1)} / {check.max_score}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Missing Items */}
      {result.missing_items.length > 0 && (
        <div className="card border-l-4 border-yellow-400">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Eksik Ogeler
          </h3>
          <ul className="space-y-2">
            {result.missing_items.map((item, idx) => (
              <li key={idx} className="flex items-center gap-2 text-gray-700">
                <svg
                  className="w-5 h-5 text-yellow-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Improvement Suggestions */}
      {result.improvements.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Iyilestirme Onerileri
          </h3>
          <div className="space-y-3">
            {result.improvements.map((imp, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
              >
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                    imp.priority
                  )}`}
                >
                  {imp.priority === 'high'
                    ? 'Yuksek'
                    : imp.priority === 'medium'
                    ? 'Orta'
                    : 'Dusuk'}
                </span>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {imp.category}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">{imp.suggestion}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grading Notes */}
      {result.grading_notes && (
        <div className="card bg-blue-50 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            Ek Notlar
          </h3>
          <p className="text-blue-800">{result.grading_notes}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button onClick={handleCopyJson} className="btn-secondary flex items-center justify-center gap-2">
          {copiedJson ? (
            <>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              Kopyalandi!
            </>
          ) : (
            <>
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"
                />
              </svg>
              JSON Kopyala
            </>
          )}
        </button>
        <button onClick={onReset} className="btn-primary">
          Yeni Dosya Yukle
        </button>
      </div>
    </div>
  );
}
