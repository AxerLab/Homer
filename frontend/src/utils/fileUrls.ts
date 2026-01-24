import type { Presentation } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export function getFileUrl(
  presentation: Presentation,
  fileType: 'pdf' | 'pptx' | 'tex',
  options: { forPreview?: boolean } = {}
): string | null {
  if (!presentation.id) {
    return null;
  }

  const format = fileType === 'tex' ? 'pdf' : fileType;
  const baseUrl = `${API_BASE_URL}/api/v1/presentations/${presentation.id}/download?format=${format}`;
  return options.forPreview ? `${baseUrl}&redirect=false` : baseUrl;
}

export function isFileAvailable(
  presentation: Presentation,
  fileType: 'pdf' | 'pptx' | 'tex'
): boolean {
  return getFileUrl(presentation, fileType) !== null;
}

export function getAvailableFileTypes(presentation: Presentation): ('pdf' | 'pptx' | 'tex')[] {
  if (!presentation.id) {
    return [];
  }
  return ['pdf', 'pptx', 'tex'];
}