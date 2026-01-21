'use client';

import { getScoreColor, getScoreBgColor } from '@/lib/api';

interface ScoreDisplayProps {
  score: number;
  maxScore: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function ScoreDisplay({
  score,
  maxScore,
  label,
  size = 'md',
}: ScoreDisplayProps) {
  const percentage = (score / maxScore) * 100;
  const colorClass = getScoreColor(score, maxScore);
  const bgColorClass = getScoreBgColor(score, maxScore);

  const sizeClasses = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-4xl',
  };

  return (
    <div className="text-center">
      {label && (
        <p className="text-sm text-gray-600 mb-1">{label}</p>
      )}
      <div className={`font-bold ${sizeClasses[size]} ${colorClass}`}>
        {score.toFixed(1)} / {maxScore}
      </div>
      <div className="mt-2 progress-bar">
        <div
          className={`progress-bar-fill ${bgColorClass.replace('bg-', 'bg-').replace('-100', '-500')}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

interface CircularScoreProps {
  score: number;
  maxScore: number;
  size?: number;
}

export function CircularScore({
  score,
  maxScore,
  size = 120,
}: CircularScoreProps) {
  const percentage = (score / maxScore) * 100;
  const colorClass = getScoreColor(score, maxScore);

  // SVG parameters
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  // Get stroke color based on score
  const getStrokeColor = () => {
    if (percentage >= 80) return '#22c55e';
    if (percentage >= 60) return '#eab308';
    if (percentage >= 40) return '#f97316';
    return '#ef4444';
  };

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getStrokeColor()}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-500 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-bold ${colorClass}`}>
          {score.toFixed(0)}
        </span>
        <span className="text-sm text-gray-500">/ {maxScore}</span>
      </div>
    </div>
  );
}
