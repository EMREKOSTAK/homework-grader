'use client';

import { useState } from 'react';
import { RubricScore, EvidenceItem, DetectedEthicsPrinciple } from '@/types';
import { getScoreColor, getScoreBgColor } from '@/lib/api';

interface RubricSectionProps {
  rubricScore: RubricScore;
}

export default function RubricSection({ rubricScore }: RubricSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const colorClass = getScoreColor(rubricScore.score, rubricScore.max_score);
  const bgColorClass = getScoreBgColor(rubricScore.score, rubricScore.max_score);
  const percentage = (rubricScore.score / rubricScore.max_score) * 100;

  return (
    <div className="card-hover">
      {/* Header - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-left"
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">
              {rubricScore.category}
            </h3>
            <p className="text-sm text-gray-600 mt-1">{rubricScore.reason}</p>
          </div>
          <div className="flex items-center gap-4 ml-4">
            <div className={`score-badge ${bgColorClass} ${colorClass}`}>
              {rubricScore.score.toFixed(1)} / {rubricScore.max_score}
            </div>
            <svg
              className={`w-5 h-5 text-gray-400 transform transition-transform ${
                isExpanded ? 'rotate-180' : ''
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
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-3 progress-bar">
          <div
            className={`progress-bar-fill ${bgColorClass.replace('-100', '-500')}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </button>

      {/* Expandable content */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
          {/* Sub-scores if available */}
          {rubricScore.sub_scores && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Alt Puanlar</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {Object.entries(rubricScore.sub_scores).map(([key, value]) => (
                  <div
                    key={key}
                    className="bg-gray-50 rounded-lg p-3 text-center"
                  >
                    <p className="text-xs text-gray-500 capitalize">
                      {formatSubScoreKey(key)}
                    </p>
                    <p className="text-lg font-semibold text-gray-900">
                      {typeof value === 'number' ? value.toFixed(1) : value}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detected Ethics Principles */}
          {rubricScore.detected_principles && rubricScore.detected_principles.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Tespit Edilen Etik Ilkeleri</h4>
              <div className="space-y-2">
                {rubricScore.detected_principles.map((principle, idx) => (
                  <PrincipleCard key={idx} principle={principle} />
                ))}
              </div>
            </div>
          )}

          {/* Consistency Analysis */}
          {rubricScore.consistency_analysis && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Tutarlilik Analizi</h4>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-blue-800">{rubricScore.consistency_analysis}</p>
              </div>
            </div>
          )}

          {/* Found/Missing Fields for Template */}
          {(rubricScore.found_fields || rubricScore.missing_fields) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {rubricScore.found_fields && rubricScore.found_fields.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-green-700">Bulunan Alanlar</h4>
                  <ul className="space-y-1">
                    {rubricScore.found_fields.map((field, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-sm text-green-600">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        {field}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {rubricScore.missing_fields && rubricScore.missing_fields.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-red-700">Eksik Alanlar</h4>
                  <ul className="space-y-1">
                    {rubricScore.missing_fields.map((field, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-sm text-red-600">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                        {field}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Language Errors */}
          {rubricScore.language_errors && rubricScore.language_errors.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-orange-700">Dil/Yazim Hatalari</h4>
              <ul className="space-y-1 bg-orange-50 rounded-lg p-3">
                {rubricScore.language_errors.map((error, idx) => (
                  <li key={idx} className="text-sm text-orange-700">
                    • {error}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Evidence quotes */}
          {rubricScore.evidence.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Kanitlar</h4>
              <div className="space-y-2">
                {rubricScore.evidence.map((ev, idx) => (
                  <EvidenceQuote key={idx} evidence={ev} />
                ))}
              </div>
            </div>
          )}

          {rubricScore.evidence.length === 0 && !rubricScore.detected_principles && !rubricScore.consistency_analysis && (
            <p className="text-sm text-gray-500 italic">
              Bu kategori icin detayli bilgi bulunamadi.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

interface PrincipleCardProps {
  principle: DetectedEthicsPrinciple;
}

function PrincipleCard({ principle }: PrincipleCardProps) {
  const isFullyCorrect = principle.correct_definition && principle.scene_match;
  const bgColor = isFullyCorrect ? 'bg-green-50' : principle.correct_definition || principle.scene_match ? 'bg-yellow-50' : 'bg-red-50';
  const borderColor = isFullyCorrect ? 'border-green-200' : principle.correct_definition || principle.scene_match ? 'border-yellow-200' : 'border-red-200';

  return (
    <div className={`${bgColor} border ${borderColor} rounded-lg p-3`}>
      <div className="flex items-start justify-between">
        <h5 className="font-medium text-gray-900">{principle.principle}</h5>
        <div className="flex gap-2">
          <span
            className={`text-xs px-2 py-1 rounded ${
              principle.correct_definition
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            Tanim: {principle.correct_definition ? 'Dogru' : 'Yanlis'}
          </span>
          <span
            className={`text-xs px-2 py-1 rounded ${
              principle.scene_match
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            Sahne Uyumu: {principle.scene_match ? 'Uygun' : 'Uyumsuz'}
          </span>
        </div>
      </div>
      {principle.note && (
        <p className="text-sm text-gray-600 mt-2">{principle.note}</p>
      )}
    </div>
  );
}

interface EvidenceQuoteProps {
  evidence: EvidenceItem;
}

function EvidenceQuote({ evidence }: EvidenceQuoteProps) {
  return (
    <div className="evidence-quote">
      <div className="flex items-start gap-2">
        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-medium flex-shrink-0">
          {evidence.slide_no}
        </span>
        <div className="flex-1">
          <p className="text-sm">&ldquo;{evidence.quote}&rdquo;</p>
          {evidence.context && (
            <p className="text-xs text-gray-500 mt-1">{evidence.context}</p>
          )}
          {evidence.comment && (
            <div className="mt-2 bg-blue-50 rounded p-2">
              <p className="text-xs text-blue-700">
                <span className="font-medium">AI Degerlendirmesi:</span> {evidence.comment}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function formatSubScoreKey(key: string): string {
  const translations: Record<string, string> = {
    ozgulluk: 'Ozgulluk',
    ozgulluk_detay: 'Ozgulluk ve Detay',
    tutarlilik: 'Tutarlilik',
    ic_tutarlilik: 'Ic Tutarlilik',
    etik_baglantisi: 'Etik Baglantisi',
    specificity: 'Ozgulluk',
    coherence: 'Tutarlilik',
    ethical_link: 'Etik Baglantisi',
    ilke_tanimi_dogrulugu: 'Ilke Tanimi Dogrulugu',
    ilke_sahne_uyumu: 'Ilke-Sahne Uyumu',
    aciklama_kalitesi: 'Aciklama Kalitesi',
    gerekli_alanlar: 'Gerekli Alanlar',
    format_duzen: 'Format ve Duzen',
    metin_kalitesi: 'Metin Kalitesi',
    duzen_organizasyon: 'Duzen ve Organizasyon',
  };
  return translations[key] || key.replace(/_/g, ' ');
}
