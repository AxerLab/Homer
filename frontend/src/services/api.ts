import axios, { type AxiosInstance, type AxiosError } from 'axios';
import type {
  PresentationCreate,
  PresentationCreateResponse,
  PresentationGetResponse,
  SlideUpdate,
  SlideUpdateResponse,
  Presentation,
  APIError,
} from '../types';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 60000, // 60 seconds for generation endpoints
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth tokens or custom headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIError>) => {
    const apiError: APIError = {
      detail: error.response?.data?.detail || error.message || 'An unexpected error occurred',
      status: error.response?.status,
    };
    return Promise.reject(apiError);
  }
);

// API Service class
class APIService {
  /**
   * Create a new presentation
   * @param main_topic - The main topic/prompt for the presentation
   * @param file_type - Output format ('pdf' or 'pptx')
   * @returns Promise with presentation ID
   */
  async createPresentation(
    main_topic: string,
    file_type: 'pdf' | 'pptx'
  ): Promise<PresentationCreateResponse> {
    const data: PresentationCreate = { main_topic, file_type };
    const response = await apiClient.post<PresentationCreateResponse>('/presentations/', data);
    return response.data;
  }

  /**
   * Get a presentation by ID
   * @param id - Presentation UUID
   * @returns Promise with presentation data
   */
  async getPresentation(id: string): Promise<PresentationGetResponse> {
    const response = await apiClient.get<PresentationGetResponse>(`/presentations/${id}`);
    return response.data;
  }

  /**
   * Update a specific slide in a presentation
   * @param id - Presentation UUID
   * @param slide_number - 1-based slide number
   * @param slide_content - New content for the slide
   * @returns Promise with updated presentation ID
   */
  async updateSlide(
    id: string,
    slide_number: number,
    slide_content: string
  ): Promise<SlideUpdateResponse> {
    const data: SlideUpdate = { slide_number, slide_content };
    const response = await apiClient.put<SlideUpdateResponse>(`/presentations/${id}`, data);
    return response.data;
  }

  /**
   * Delete a presentation
   * @param id - Presentation UUID
   */
  async deletePresentation(id: string): Promise<void> {
    await apiClient.delete(`/presentations/${id}`);
  }

  /**
   * List all presentations with pagination
   * @param skip - Number of presentations to skip (default: 0)
   * @param limit - Maximum number of presentations to return (default: 100)
   * @returns Promise with array of presentations
   */
  async listPresentations(skip: number = 0, limit: number = 100): Promise<Presentation[]> {
    const response = await apiClient.get<Presentation[]>('/presentations/', {
      params: { skip, limit },
    });
    return response.data;
  }

  /**
   * Get the URL for a generated file
   * @param id - Presentation UUID
   * @param file_type - File type ('pdf' or 'pptx')
   * @returns File URL
   */
  getFileUrl(id: string, file_type: 'pdf' | 'pptx'): string {
    return `/generated_files/${file_type}/${id}.${file_type}`;
  }

  /**
   * Health check endpoint
   * @returns Promise with health status
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await apiClient.get<{ status: string }>('/health');
    return response.data;
  }
}

// Export singleton instance
export const api = new APIService();

// Export class for testing or custom instances
export default APIService;
