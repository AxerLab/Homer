// Simple types matching the actual backend API from OpenAPI spec

// Slide data returned from backend
export type SlideData = {
  title: string;
  content: string;
  layout: string;
}

// Backend returns presentation metadata
// In production, it should also return file URLs
export type Presentation = {
  id: string;
  main_topic: string;
  file_type: 'pptx' | 'pdf';  // File type from backend
  slides: SlideData[];  // Slide data from backend
}

// Request/Response types directly from backend spec
export type CreatePresentationRequest = {
  main_topic: string;
  file_type: 'pptx' | 'pdf';
  theme?: string;  // Optional theme selection
  use_rag?: boolean;  // Whether to use RAG context from uploaded documents
}

export type CreatePresentationResponse = {
  id: string;
  // Optional: URLs for newly created files
  file_urls?: {
    pdf?: string;
    pptx?: string;
    tex?: string;
  };
}

export type SlideUpdateRequest = {
  slide_number: number;
  slide_content: string;
}

export type SlideUpdateResponse = {
  id: string;
  // Optional: Updated file URLs after regeneration
  file_urls?: {
    pdf?: string;
    pptx?: string;
    tex?: string;
  };
}

// RAG Types
export type RAGDocumentUploadResponse = {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export type RAGQueryRequest = {
  question: string;
  mode?: 'hybrid' | 'local' | 'global' | 'naive';
  top_k?: number;
}

export type RAGQueryResponse = {
  answer: string;
  question: string;
  mode: string;
}

export type RAGContextRequest = {
  topic: string;
  mode?: 'hybrid' | 'local' | 'global' | 'naive';
}

export type RAGContextResponse = {
  context: string;
  topic: string;
}

export type RAGStatus = {
  working_dir: string;
  parser: string;
  embedding_model: string;
  embedding_dim: number;
  llm_model: string;
  initialized: boolean;
}

export type RAGDocumentStatus = {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  progress_message: string;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
  file_size_bytes: number;
  file_extension: string;
}

export type RAGDocumentListResponse = {
  documents: RAGDocumentStatus[];
  total: number;
}

export type RAGProgressEvent = {
  doc_id: string;
  progress: number;
  stage: 'pending' | 'parsing' | 'embedding' | 'indexing' | 'completed' | 'failed';
  message: string;
  error: string | null;
}

export type RAGDocumentDeleteResponse = {
  id: string;
  deleted: boolean;
  message: string;
}