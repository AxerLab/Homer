// Simple types matching the actual backend API from OpenAPI spec

// Backend returns presentation metadata
// In production, it should also return file URLs
export type Presentation = {
  id: string;
  main_topic: string;
  file_type: 'pptx' | 'pdf';  // File type from backend
}

// Request/Response types directly from backend spec
export type CreatePresentationRequest = {
  main_topic: string;
  file_type: 'pptx' | 'pdf';
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