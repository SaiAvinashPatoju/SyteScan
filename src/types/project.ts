export interface ProjectCreateRequest {
  name: string;
  requirements: string[];
}

export interface ProjectResponse {
  id: string;
  name: string;
  requirements: string[];
  created_at: string;
}

export interface ApiError {
  detail: string;
  error_code?: string;
}

export interface RequirementMatch {
  requirement: string;
  detected: boolean;
  confidence?: number;
  count: number;
}

export interface DetectionSummary {
  total_objects_detected: number;
  unique_objects: string[];
  average_confidence: number;
}

export interface ProgressResponse {
  project_id: string;
  completion_percentage: number;
  requirement_matches: RequirementMatch[];
  detection_summary: DetectionSummary;
}