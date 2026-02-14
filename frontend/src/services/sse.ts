import type { RAGProgressEvent } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export interface ProgressCallbacks {
  onProgress: (event: RAGProgressEvent) => void;
  onComplete: (event: RAGProgressEvent) => void;
  onError: (error: string) => void;
}

export function subscribeToDocumentProgress(
  docId: string,
  callbacks: ProgressCallbacks
): () => void {
  const url = `${API_BASE_URL}/api/v1/rag/document/${docId}/progress`;
  const eventSource = new EventSource(url);
  let isTerminal = false;

  eventSource.onmessage = (event) => {
    try {
      const data: RAGProgressEvent = JSON.parse(event.data);
      callbacks.onProgress(data);

      if (data.stage === 'completed') {
        isTerminal = true;
        callbacks.onComplete(data);
        eventSource.close();
      } else if (data.stage === 'failed') {
        isTerminal = true;
        callbacks.onError(data.error || 'Processing failed');
        eventSource.close();
      }
    } catch (e) {
      console.error('Failed to parse SSE event:', e);
    }
  };

  eventSource.onerror = () => {
    if (isTerminal) {
      return;
    }
    if (eventSource.readyState === EventSource.CLOSED) {
      callbacks.onError('Connection lost');
      eventSource.close();
    }
  };

  return () => {
    eventSource.close();
  };
}
