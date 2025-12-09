import { ProjectCreateRequest, ProjectResponse, ApiError, ProgressResponse } from '@/types/project';

export interface DetectedObject {
  name: string;
  confidence: number;
  bbox: number[];
}

export interface DetectionResult {
  image_path: string;
  filename: string;
  detected_objects: DetectedObject[];
  processing_time: number;
  created_at: string;
}

export interface UploadResponse {
  project_id: string;
  uploaded_files: string[];
  detection_results: DetectionResult[];
  total_objects_detected: number;
  processing_summary: {
    total_files_uploaded: number;
    total_files_processed: number;
    total_objects_detected: number;
    average_processing_time: number;
  };
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new Error(errorData.detail || 'An error occurred');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  async createProject(data: ProjectCreateRequest): Promise<ProjectResponse> {
    return this.request<ProjectResponse>('/api/projects/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getProject(projectId: string): Promise<ProjectResponse> {
    return this.request<ProjectResponse>(`/api/projects/${projectId}`);
  }

  async getAllProjects(): Promise<ProjectResponse[]> {
    return this.request<ProjectResponse[]>('/api/projects/');
  }

  async uploadImages(projectId: string, files: File[]): Promise<UploadResponse> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const url = `${API_BASE_URL}/api/projects/${projectId}/upload`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new Error(errorData.detail || 'Upload failed');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred during upload');
    }
  }

  async getProjectImages(projectId: string): Promise<{ project_id: string; images: string[]; count: number }> {
    return this.request<{ project_id: string; images: string[]; count: number }>(`/api/projects/${projectId}/images`);
  }

  async getProjectProgress(projectId: string): Promise<ProgressResponse> {
    return this.request<ProgressResponse>(`/api/projects/${projectId}/progress`);
  }
}

export const apiClient = new ApiClient();