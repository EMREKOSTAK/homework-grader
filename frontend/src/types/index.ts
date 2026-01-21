// API Response Types

export interface EvidenceItem {
  slide_no: number;
  quote: string;
  context?: string;
  comment?: string; // AI's evaluation comment about this evidence
}

export interface DeterministicCheckResult {
  check_name: string;
  passed: boolean;
  score: number;
  max_score: number;
  evidence: EvidenceItem[];
  missing_items: string[];
  details?: string;
}

export interface DetectedEthicsPrinciple {
  principle: string;
  correct_definition: boolean;
  scene_match: boolean;
  note?: string;
}

export interface RubricScore {
  category: string;
  score: number;
  max_score: number;
  reason: string;
  evidence: EvidenceItem[];
  sub_scores?: Record<string, number>;
  // Extended evaluation fields
  detected_principles?: DetectedEthicsPrinciple[];
  consistency_analysis?: string;
  found_fields?: string[];
  missing_fields?: string[];
  language_errors?: string[];
}

export interface ImprovementSuggestion {
  category: string;
  suggestion: string;
  priority: 'high' | 'medium' | 'low';
}

export interface GradingResult {
  total_score: number;
  rubric_scores: RubricScore[];
  missing_items: string[];
  improvements: ImprovementSuggestion[];
  deterministic_checks: DeterministicCheckResult[];
  on_time_submitted: boolean;
  grading_notes?: string;
  overall_evaluation?: string;
}

export interface AnalyzeResponse {
  success: boolean;
  result?: GradingResult;
  error?: string;
  parsed_content?: unknown;
}

export interface HealthResponse {
  status: string;
  version: string;
}

// Bulk grading types
export interface StudentResult {
  student_name: string;
  filename: string;
  success: boolean;
  result?: GradingResult;
  error?: string;
}

export interface BulkAnalyzeResponse {
  total_files: number;
  successful: number;
  failed: number;
  results: StudentResult[];
}

// UI State Types
export type UploadStatus = 'idle' | 'uploading' | 'analyzing' | 'complete' | 'error';
export type UploadMode = 'single' | 'bulk';

export interface UploadState {
  status: UploadStatus;
  progress: number;
  file?: File;
  error?: string;
  result?: GradingResult;
}

export interface BulkUploadState {
  status: UploadStatus;
  progress: number;
  files: File[];
  error?: string;
  result?: BulkAnalyzeResponse;
}
