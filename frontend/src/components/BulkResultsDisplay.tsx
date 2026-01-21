'use client';

import { BulkAnalyzeResponse, StudentResult } from '@/types';
import { getScoreColor, getScoreBgColor } from '@/lib/api';
import { useState } from 'react';

interface BulkResultsDisplayProps {
  result: BulkAnalyzeResponse;
  onReset: () => void;
  onExportExcel: () => void;
  isExporting: boolean;
}

function StudentResultCard({ student }: { student: StudentResult }) {
  const [expanded, setExpanded] = useState(false);

  if (!student.success) {
    return (
      <div className="border border-red-200 bg-red-50 rounded-lg p-4">
        <div className="flex justify-between items-center">
          <div>
            <p className="font-medium text-gray-900">{student.student_name}</p>
            <p className="text-sm text-gray-500">{student.filename}</p>
          </div>
          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm">
            Hata
          </span>
        </div>
        <p className="mt-2 text-sm text-red-600">{student.error}</p>
      </div>
    );
  }

  const result = student.result!;

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-center">
        <div>
          <p className="font-medium text-gray-900">{student.student_name}</p>
          <p className="text-sm text-gray-500">{student.filename}</p>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`text-2xl font-bold ${getScoreColor(
              result.total_score,
              100
            )}`}
          >
            {result.total_score.toFixed(0)}
          </span>
          <span className="text-gray-400">/100</span>
          <button
            onClick={() => setExpanded(!expanded)}
            className="ml-2 text-gray-400 hover:text-gray-600"
          >
            <svg
              className={`w-5 h-5 transform transition-transform ${
                expanded ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        </div>
      </div>

      {expanded && (
        <div className="mt-4 space-y-3">
          {/* Rubric scores */}
          <div className="grid grid-cols-2 gap-2">
            {result.rubric_scores.map((rubric, idx) => (
              <div
                key={idx}
                className={`p-2 rounded ${getScoreBgColor(
                  rubric.score,
                  rubric.max_score
                )}`}
              >
                <p className="text-xs text-gray-600">{rubric.category}</p>
                <p
                  className={`font-medium ${getScoreColor(
                    rubric.score,
                    rubric.max_score
                  )}`}
                >
                  {rubric.score}/{rubric.max_score}
                </p>
              </div>
            ))}
          </div>

          {/* Overall evaluation */}
          {result.overall_evaluation && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">{result.overall_evaluation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function BulkResultsDisplay({
  result,
  onReset,
  onExportExcel,
  isExporting,
}: BulkResultsDisplayProps) {
  // Calculate average score
  const successfulResults = result.results.filter((r) => r.success && r.result);
  const avgScore =
    successfulResults.length > 0
      ? successfulResults.reduce((acc, r) => acc + r.result!.total_score, 0) /
        successfulResults.length
      : 0;

  // Sort by score descending
  const sortedResults = [...result.results].sort((a, b) => {
    if (!a.success) return 1;
    if (!b.success) return -1;
    return b.result!.total_score - a.result!.total_score;
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Toplu Degerlendirme Sonuclari</h2>
          <p className="text-gray-600 mt-1">
            {result.total_files} dosya islendi
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={onExportExcel}
            disabled={isExporting}
            className="btn-primary flex items-center gap-2"
          >
            {isExporting ? (
              <>
                <svg
                  className="animate-spin h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Olusturuluyor...
              </>
            ) : (
              <>
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Excel Indir
              </>
            )}
          </button>
          <button onClick={onReset} className="btn-secondary">
            Yeni Degerlendirme
          </button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card text-center">
          <p className="text-3xl font-bold text-primary-600">{avgScore.toFixed(1)}</p>
          <p className="text-sm text-gray-500">Ortalama Puan</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-green-600">{result.successful}</p>
          <p className="text-sm text-gray-500">Basarili</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-red-600">{result.failed}</p>
          <p className="text-sm text-gray-500">Hatali</p>
        </div>
      </div>

      {/* Results list */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-gray-900">Ogrenci Sonuclari</h3>
        {sortedResults.map((student, idx) => (
          <StudentResultCard key={idx} student={student} />
        ))}
      </div>
    </div>
  );
}
