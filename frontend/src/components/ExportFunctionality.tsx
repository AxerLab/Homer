import React, { useState } from 'react';
import type { Presentation } from '@/types/api';
import { getFileUrl, getAvailableFileTypes } from '@/utils/fileUrls';

interface ExportFunctionalityProps {
  presentation: Presentation;
}

export const ExportFunctionality: React.FC<ExportFunctionalityProps> = ({ presentation }) => {
  const [exportFormat, setExportFormat] = useState<'pptx' | 'pdf'>('pdf');
  const [loading, setLoading] = useState(false);
  const [exportStatus, setExportStatus] = useState<string | null>(null);

  // Get available file types for this presentation
  const availableTypes = getAvailableFileTypes(presentation);

  const handleExport = async () => {
    const fileUrl = getFileUrl(presentation, exportFormat);

    if (!fileUrl) {
      setExportStatus(`Error: ${exportFormat.toUpperCase()} file not available`);
      return;
    }

    setLoading(true);
    setExportStatus('Starting download...');

    try {
      // Fetch the file from the URL (could be CDN, S3, or local)
      const response = await fetch(fileUrl);

      if (!response.ok) {
        throw new Error(`Download failed: ${response.status}`);
      }

      // Create a blob and trigger download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${presentation.main_topic}.${exportFormat}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setExportStatus('Download completed successfully!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Download failed';
      setExportStatus(`Error: ${errorMessage}`);
      console.error('Download error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (availableTypes.length === 0) {
    return (
      <div className="export-functionality space-y-4">
        <h3 className="font-medium">Download Presentation</h3>
        <div className="text-sm text-gray-500 p-4 bg-gray-50 rounded">
          No files available for download yet. Files may still be generating.
        </div>
      </div>
    );
  }

  return (
    <div className="export-functionality space-y-4">
      <h3 className="font-medium">Download Presentation</h3>

      <div className="flex space-x-4">
        {availableTypes.includes('pptx') && (
          <label className="inline-flex items-center">
            <input
              type="radio"
              name="exportFormat"
              checked={exportFormat === 'pptx'}
              onChange={() => setExportFormat('pptx')}
              className="mr-2"
              disabled={loading}
            />
            PowerPoint (PPTX)
          </label>
        )}
        {availableTypes.includes('pdf') && (
          <label className="inline-flex items-center">
            <input
              type="radio"
              name="exportFormat"
              checked={exportFormat === 'pdf'}
              onChange={() => setExportFormat('pdf')}
              className="mr-2"
              disabled={loading}
            />
            PDF
          </label>
        )}
      </div>

      <button
        onClick={handleExport}
        className="w-full bg-primary text-white p-2 rounded hover:bg-secondary transition-colors disabled:opacity-50"
        disabled={loading || !availableTypes.includes(exportFormat)}
      >
        {loading ? 'Downloading...' : `Download as ${exportFormat.toUpperCase()}`}
      </button>

      {exportStatus && (
        <div className={`text-sm p-2 rounded ${
          exportStatus.startsWith('Error')
            ? 'bg-error/20 text-error'
            : 'bg-primary/10 text-primary'
        }`}>
          {exportStatus}
        </div>
      )}
    </div>
  );
};