import { AnalyzeResponse, HealthResponse, BulkAnalyzeResponse } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/health`);
  if (!response.ok) {
    throw new APIError('API health check failed', response.status);
  }
  return response.json();
}

export async function analyzePresentation(
  file: File,
  onTime: boolean
): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('on_time', String(onTime));

  const response = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.detail || 'Analysis failed',
      response.status,
      JSON.stringify(errorData)
    );
  }

  return response.json();
}

export function getScoreColor(score: number, maxScore: number): string {
  const percentage = (score / maxScore) * 100;
  if (percentage >= 80) return 'text-green-600';
  if (percentage >= 60) return 'text-yellow-600';
  if (percentage >= 40) return 'text-orange-500';
  return 'text-red-600';
}

export function getScoreBgColor(score: number, maxScore: number): string {
  const percentage = (score / maxScore) * 100;
  if (percentage >= 80) return 'bg-green-100';
  if (percentage >= 60) return 'bg-yellow-100';
  if (percentage >= 40) return 'bg-orange-100';
  return 'bg-red-100';
}

export function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'low':
      return 'bg-blue-100 text-blue-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

export function formatCheckName(name: string): string {
  const names: Record<string, string> = {
    page_numbers: 'Sayfa Numaraları',
    ethics_principles: 'Etik İlkeleri',
    template_fields: 'Şablon Alanları',
  };
  return names[name] || name;
}

export async function analyzeBulk(
  files: File[],
  onTime: boolean
): Promise<BulkAnalyzeResponse> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  formData.append('on_time', String(onTime));

  const response = await fetch(`${API_URL}/api/analyze-bulk`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.detail || 'Bulk analysis failed',
      response.status,
      JSON.stringify(errorData)
    );
  }

  return response.json();
}

export async function exportExcel(
  files: File[],
  onTime: boolean
): Promise<Blob> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  formData.append('on_time', String(onTime));

  const response = await fetch(`${API_URL}/api/export-excel`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.detail || 'Excel export failed',
      response.status,
      JSON.stringify(errorData)
    );
  }

  return response.blob();
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
