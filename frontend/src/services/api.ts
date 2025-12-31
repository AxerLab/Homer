// Enhanced API client with proper error handling and logging
import type { 
  Presentation, 
  CreatePresentationRequest,
  RAGDocumentUploadResponse,
  RAGQueryRequest,
  RAGQueryResponse,
  RAGContextRequest,
  RAGContextResponse,
  RAGStatus
} from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Helper function to handle API responses
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = Array.isArray(errorData.detail)
          ? errorData.detail.map((d: any) => d.msg || d.message).join(', ')
          : errorData.detail;
      } else if (errorData.message) {
        errorMessage = errorData.message;
      } else if (errorData.error) {
        errorMessage = errorData.error;
      }
    } catch (e) {
      // Could not parse error as JSON, try text
      try {
        const text = await response.text();
        if (text) errorMessage = text;
      } catch { }
    }

    console.error(`API Error: ${errorMessage}`);
    throw new Error(errorMessage);
  }

  return response.json();
}

// API client with all endpoints
export const presentationApi = {
  // Health check endpoint
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  },

  // Create a new presentation
  async createPresentation(topic: string, fileType: 'pptx' | 'pdf' = 'pptx', theme?: string): Promise<{ id: string }> {
    console.log('Creating presentation:', { topic, fileType, theme });

    const response = await fetch(`${API_BASE_URL}/api/v1/presentations/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        main_topic: topic,
        file_type: fileType,
        ...(theme && { theme })  // Only include theme if provided
      } as CreatePresentationRequest),
    });

    const data = await handleResponse<{ id: string }>(response);
    console.log('Presentation created:', data);
    return data;
  },

  // Get all presentations
  async getPresentations(skip = 0, limit = 100): Promise<Presentation[]> {
    console.log('Fetching presentations...');

    const response = await fetch(
      `${API_BASE_URL}/api/v1/presentations/?skip=${skip}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      }
    );

    const data = await handleResponse<{ presentations: Presentation[], skip: number, limit: number, total: number }>(response);
    console.log(`Fetched ${data.presentations.length} presentations out of ${data.total} total`);

    // The API returns an object with presentations array
    return data.presentations;
  },

  // Get a specific presentation
  async getPresentation(presentationId: string): Promise<Presentation> {
    console.log('Fetching presentation:', presentationId);

    const response = await fetch(
      `${API_BASE_URL}/api/v1/presentations/${presentationId}`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      }
    );

    const data = await handleResponse<Presentation>(response);
    console.log('Fetched presentation:', data);
    return data;
  },

  // Update a slide
  async updateSlide(
    presentationId: string,
    slideNumber: number,
    slideContent: string
  ): Promise<Presentation> {
    /// Update a specific slide in a presentation. SlideNumber is 1-based.
    console.log('Updating slide:', { presentationId, slideNumber });

    const response = await fetch(
      `${API_BASE_URL}/api/v1/presentations/${presentationId}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          slide_number: slideNumber,
          slide_content: slideContent,
        }),
      }
    );

    const data = await handleResponse<Presentation>(response);
    console.log('Slide updated:', data);
    return data;
  },

  // Delete a presentation
  async deletePresentation(presentationId: string): Promise<void> {
    console.log('Deleting presentation:', presentationId);

    const response = await fetch(
      `${API_BASE_URL}/api/v1/presentations/${presentationId}`,
      {
        method: 'DELETE',
        headers: {
          'Accept': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to delete: ${errorText}`);
    }

    console.log('Presentation deleted successfully');
  },

  // Check if backend is accessible
  async checkBackend(): Promise<{ isHealthy: boolean; error?: string }> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${API_BASE_URL}/health`, {
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        return { isHealthy: true };
      } else {
        return {
          isHealthy: false,
          error: `Backend returned status ${response.status}`
        };
      }
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          return { isHealthy: false, error: 'Backend request timed out' };
        }
        return { isHealthy: false, error: error.message };
      }
      return { isHealthy: false, error: 'Unknown error occurred' };
    }
  },
};

// Export API base URL for use in other components
export { API_BASE_URL };

export const ragApi = {
  async uploadDocument(file: File): Promise<RAGDocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/v1/rag/upload`, {
      method: 'POST',
      body: formData,
    });

    return handleResponse<RAGDocumentUploadResponse>(response);
  },

  async query(request: RAGQueryRequest): Promise<RAGQueryResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/rag/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse<RAGQueryResponse>(response);
  },

  async getContext(request: RAGContextRequest): Promise<RAGContextResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/rag/context`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse<RAGContextResponse>(response);
  },

  async getStatus(): Promise<RAGStatus> {
    const response = await fetch(`${API_BASE_URL}/api/v1/rag/status`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    return handleResponse<RAGStatus>(response);
  },
};