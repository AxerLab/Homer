/**
 * Utility to handle file URLs for both development and production environments
 *
 * In development (local storage): Files are served from /generated_files directory
 * In production (Azure storage): Files are served via /api/v1/presentations/{id}/download endpoint
 */

import type { Presentation } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const USE_AZURE_STORAGE = import.meta.env.VITE_USE_AZURE_STORAGE === 'true';

export function getFileUrl(
  presentation: Presentation,
  fileType: 'pdf' | 'pptx' | 'tex',
  options: { forPreview?: boolean } = {}
): string | null {
  if (!presentation.id) {
    return null;
  }

  if (USE_AZURE_STORAGE) {
    const format = fileType === 'tex' ? 'pdf' : fileType;
    const baseUrl = `${API_BASE_URL}/api/v1/presentations/${presentation.id}/download?format=${format}`;
    return options.forPreview ? `${baseUrl}&redirect=false` : baseUrl;
  }

  const subdir = fileType === 'tex' ? 'pdf' : fileType;
  return `${API_BASE_URL}/generated_files/${subdir}/${presentation.id}.${fileType}`;
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