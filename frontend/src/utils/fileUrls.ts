/**
 * Utility to handle file URLs for both development and production environments
 *
 * In development: Files are served from local /generated_files directory
 * In production: Files are served from CDN/cloud storage with direct URLs
 */

import type { Presentation } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Check if we should use local file serving (development mode)
const USE_LOCAL_FILES = import.meta.env.VITE_USE_LOCAL_FILES !== 'false';

/**
 * Get the URL for a presentation file
 *
 * Priority:
 * 1. Use file_urls from backend if available (production with CDN/storage)
 * 2. Construct local path if in development mode
 * 3. Return null if file not available
 */
export function getFileUrl(
  presentation: Presentation,
  fileType: 'pdf' | 'pptx' | 'tex'
): string | null {
  // First, check if backend provided direct URLs (production scenario)
  if (presentation.file_urls?.[fileType]) {
    return presentation.file_urls[fileType];
  }

  // In development or if backend doesn't provide URLs, construct local path
  if (USE_LOCAL_FILES && presentation.id) {
    // For local development, files are at:
    // - /generated_files/pdf/{uuid}.pdf
    // - /generated_files/pptx/{uuid}.pptx
    // - /generated_files/pdf/{uuid}.tex (tex files are stored in pdf folder)
    const subdir = fileType === 'tex' ? 'pdf' : fileType;
    return `${API_BASE_URL}/generated_files/${subdir}/${presentation.id}.${fileType}`;
  }

  // No file URL available
  return null;
}

/**
 * Check if a file type is available for a presentation
 */
export function isFileAvailable(
  presentation: Presentation,
  fileType: 'pdf' | 'pptx' | 'tex'
): boolean {
  return getFileUrl(presentation, fileType) !== null;
}

/**
 * Get available file types for a presentation
 */
export function getAvailableFileTypes(presentation: Presentation): ('pdf' | 'pptx' | 'tex')[] {
  const types: ('pdf' | 'pptx' | 'tex')[] = [];

  if (isFileAvailable(presentation, 'pdf')) {
    types.push('pdf');
  }

  if (isFileAvailable(presentation, 'pptx')) {
    types.push('pptx');
  }

  if (isFileAvailable(presentation, 'tex')) {
    types.push('tex');
  }

  // If no URLs provided but we have an ID, assume both types are available locally
  if (types.length === 0 && USE_LOCAL_FILES && presentation.id) {
    return ['pdf', 'pptx', 'tex'];
  }

  return types;
}