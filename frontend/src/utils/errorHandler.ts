/**
 * Centralized error handling utility
 */

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}

/**
 * Extract a user-friendly error message from various error types
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  if (error && typeof error === 'object') {
    if ('message' in error && typeof error.message === 'string') {
      return error.message;
    }

    if ('detail' in error && typeof error.detail === 'string') {
      return error.detail;
    }
  }

  return 'An unexpected error occurred';
}

/**
 * Log error details for debugging
 */
export function logError(context: string, error: unknown): void {
  const timestamp = new Date().toISOString();
  const message = getErrorMessage(error);

  console.error(`[${timestamp}] Error in ${context}:`, {
    message,
    error,
    stack: error instanceof Error ? error.stack : undefined,
  });
}

/**
 * Format API response errors
 */
export async function formatApiError(response: Response): Promise<ApiError> {
  let message = `Request failed with status ${response.status}`;
  let details: unknown = null;

  try {
    const contentType = response.headers.get('content-type');

    if (contentType?.includes('application/json')) {
      details = await response.json();

      // Try to extract a meaningful message from the JSON response
      if (details && typeof details === 'object') {
        if ('message' in details) {
          message = String(details.message);
        } else if ('detail' in details) {
          message = String(details.detail);
        } else if ('error' in details) {
          message = String(details.error);
        }
      }
    } else {
      const text = await response.text();
      if (text) {
        message = text.substring(0, 200); // Limit error message length
      }
    }
  } catch (e) {
    // Failed to parse error response
    console.warn('Failed to parse error response:', e);
  }

  return {
    message,
    status: response.status,
    details,
  };
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof TypeError) {
    const message = error.message.toLowerCase();
    return message.includes('fetch') || message.includes('network') || message.includes('failed');
  }
  return false;
}

/**
 * Check if the backend is accessible
 */
export async function checkBackendHealth(apiBaseUrl: string): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

    const response = await fetch(`${apiBaseUrl}/health`, {
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return response.ok;
  } catch (error) {
    logError('Backend health check', error);
    return false;
  }
}