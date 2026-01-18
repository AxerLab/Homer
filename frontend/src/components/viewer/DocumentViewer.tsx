import React, { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import type { Presentation } from '@/types/api';
import { getFileUrl } from '@/utils/fileUrls';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set up the PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

interface DocumentViewerProps {
  presentation: Presentation;
  fileType?: 'pptx' | 'pdf';
  refreshKey?: number;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({ presentation, fileType = 'pdf', refreshKey }) => {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [documentKey, setDocumentKey] = useState(refreshKey || Date.now());

  // Reset state and force remount when refreshKey changes
  useEffect(() => {
    if (refreshKey) {
      setNumPages(null);
      setPageNumber(1);
      setError(null);
      setDocumentKey(refreshKey);
    }
  }, [refreshKey]);

  // Debug logging
  console.log('DocumentViewer rendered with:', {
    presentationId: presentation.id,
    fileType: fileType,
    refreshKey: refreshKey,
    documentKey: documentKey
  });

  // Get file URL using utility (handles both production CDN and local development)
  const baseFileUrl = getFileUrl(presentation, fileType);
  const fileUrl = baseFileUrl ? `${baseFileUrl}?t=${documentKey}` : null;
  console.log('Generated fileUrl:', fileUrl, 'for fileType:', fileType);

  if (!fileUrl) {
    return (
      <div className="document-viewer-container border border-border rounded p-4">
        <h3 className="font-medium mb-2">{presentation.main_topic}</h3>
        <div className="h-[600px] flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <p className="text-gray-500 mb-2">
              {fileType.toUpperCase()} file not available
            </p>
            <p className="text-sm text-gray-400">
              File may still be generating or not yet uploaded
            </p>
          </div>
        </div>
      </div>
    );
  }

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setError(null);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('Error loading document:', error);
    setError('Failed to load document');
  };

  const changePage = (offset: number) => {
    setPageNumber(prevPageNumber => {
      const newPageNumber = prevPageNumber + offset;
      return Math.min(Math.max(1, newPageNumber), numPages || 1);
    });
  };

  return (
    <div className="document-viewer-container border border-border rounded p-4">
      <h3 className="font-medium mb-2">{presentation.main_topic}</h3>

      <div className="h-[600px] w-full overflow-auto">
        {fileType === 'pdf' ? (
          <div className="flex flex-col items-center">
            {error ? (
              <div className="flex flex-col items-center justify-center h-full">
                <p className="text-red-500 mb-4">{error}</p>
                <a
                  href={fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 underline"
                >
                  Download PDF instead
                </a>
              </div>
            ) : (
              <>
                <Document
                  key={documentKey}
                  file={fileUrl}
                  onLoadSuccess={onDocumentLoadSuccess}
                  onLoadError={onDocumentLoadError}
                  loading={
                    <div className="text-gray-500">Loading PDF...</div>
                  }
                >
                  <Page
                    pageNumber={pageNumber}
                    renderTextLayer={true}
                    renderAnnotationLayer={true}
                    className="border border-gray-300"
                    width={Math.min(window.innerWidth - 100, 800)}
                  />
                </Document>

                {numPages && (
                  <div className="mt-4 flex items-center gap-4">
                    <button
                      onClick={() => changePage(-1)}
                      disabled={pageNumber <= 1}
                      className="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <span className="text-sm">
                      Page {pageNumber} of {numPages}
                    </span>
                    <button
                      onClick={() => changePage(1)}
                      disabled={pageNumber >= (numPages || 1)}
                      className="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        ) : (
          // For PPTX files - just show download link as we removed the viewer
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-gray-600">Preview not available for PPTX files.</p>
          </div>
        )}
      </div>

      <div className="mt-2 text-sm text-gray-500 flex justify-between items-center">
        <span>Presentation ID: {presentation.id}</span>
        <div className="flex gap-4 items-center">
          <span>Format: {fileType.toUpperCase()}</span>
          <a
            href={fileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:text-blue-600 underline"
          >
            Download
          </a>
        </div>
      </div>
    </div>
  );
};