// API Request Types
export interface PresentationCreate {
  main_topic: string;
  file_type: 'pdf' | 'pptx';
}

export interface SlideUpdate {
  slide_number: number; // 1-based slide number
  slide_content: string;
}

// API Response Types
export interface PresentationCreateResponse {
  id: string; // UUID
}

export interface PresentationGetResponse {
  id: string; // UUID
  main_topic: string;
}

export interface SlideUpdateResponse {
  id: string; // UUID
}

// Extended Types for Frontend Use
export interface Presentation {
  id: string;
  main_topic: string;
  file_type: 'pdf' | 'pptx';
  created_at?: string;
  updated_at?: string;
}

export interface PresentationList {
  presentations: Presentation[];
  total: number;
  skip: number;
  limit: number;
}

// API Error Response
export interface APIError {
  detail: string;
  status?: number;
}

// File Type
export type FileType = 'pdf' | 'pptx';

// Application State Types
export interface AppState {
  presentations: Presentation[];
  currentPresentation: Presentation | null;
  selectedSlide: number;
  isGenerating: boolean;
  isEditing: boolean;
  viewerType: FileType;
}
