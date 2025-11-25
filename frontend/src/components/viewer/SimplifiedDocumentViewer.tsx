import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, Download } from '@mui/icons-material';
import type { Presentation } from '@/types/api';
import { getFileUrl } from '@/utils/fileUrls';
import { cn } from '@/lib/utils';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import './SimplifiedDocumentViewer.css';

// Set up the PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface SimplifiedDocumentViewerProps {
  presentation: Presentation;
  fileType?: 'pptx' | 'pdf';
  currentPage?: number;
  onPageChange?: (page: number) => void;
  className?: string;
}

export const SimplifiedDocumentViewer: React.FC<SimplifiedDocumentViewerProps> = ({
  presentation,
  fileType = 'pdf',
  currentPage = 1,
  onPageChange,
  className
}) => {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(currentPage);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Always get PDF URL for preview (we now generate PDF for both pptx and pdf types)
  const pdfUrl = getFileUrl(presentation, 'pdf');
  // Get PPTX URL for download button (only if original type was pptx)
  const pptxUrl = fileType === 'pptx' ? getFileUrl(presentation, 'pptx') : null;

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('Error loading document:', error);
    setError('Failed to load PDF preview. The file may still be processing.');
    setLoading(false);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= (numPages || 1)) {
      setPageNumber(newPage);
      onPageChange?.(newPage);
    }
  };

  if (!pdfUrl) {
    return (
      <div className={cn('flex items-center justify-center h-full', className)}>
        <p className="text-text-muted">No document available</p>
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col h-full bg-background', className)}>
      {/* Navigation controls at the top */}
      <div className="flex items-center justify-center gap-4 py-2">
        {numPages && numPages > 1 && (
          <>
            <button
              onClick={() => handlePageChange(pageNumber - 1)}
              disabled={pageNumber <= 1}
              className={cn(
                'p-2 rounded-lg transition-colors',
                pageNumber === 1
                  ? 'text-text-muted cursor-not-allowed opacity-50'
                  : 'text-text hover:bg-primary/10'
              )}
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <div className="text-text">
              <span className="font-medium">{pageNumber}</span>
              <span className="text-text-muted mx-2">/</span>
              <span className="text-text-muted">{numPages}</span>
            </div>

            <button
              onClick={() => handlePageChange(pageNumber + 1)}
              disabled={pageNumber >= numPages}
              className={cn(
                'p-2 rounded-lg transition-colors',
                pageNumber === numPages
                  ? 'text-text-muted cursor-not-allowed opacity-50'
                  : 'text-text hover:bg-primary/10'
              )}
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </>
        )}
        
        {/* Download buttons */}
        <div className="flex gap-2 ml-4">
          {pptxUrl && (
            <a
              href={pptxUrl}
              download={`${presentation.main_topic}.pptx`}
              className="px-3 py-1.5 bg-gradient-to-r from-orange-500 to-red-500 text-white text-sm rounded-lg hover:from-orange-600 hover:to-red-600 transition-all flex items-center gap-1 font-medium shadow-sm"
            >
              <Download className="w-4 h-4" />
              PPTX
            </a>
          )}
          <a
            href={pdfUrl}
            download={`${presentation.main_topic}.pdf`}
            className="px-3 py-1.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all flex items-center gap-1 font-medium shadow-sm"
          >
            <Download className="w-4 h-4" />
            PDF
          </a>
        </div>
      </div>

      {/* Document viewer */}
      <div className="flex-1 overflow-auto flex items-start justify-center pt-4">
        {loading && (
          <div className="text-text-muted pt-8">Loading document...</div>
        )}

        {error && (
          <div className="text-red-500 pt-8 text-center px-4">
            {error}
            {pptxUrl && (
              <div className="mt-4">
                <a
                  href={pptxUrl}
                  download={`${presentation.main_topic}.pptx`}
                  className="px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 transition-all inline-flex items-center gap-2 font-medium shadow-md"
                >
                  <Download className="w-5 h-5" />
                  Download PPTX Instead
                </a>
              </div>
            )}
          </div>
        )}

        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={onDocumentLoadError}
          loading=""
          className="flex justify-center"
        >
          <Page
            pageNumber={pageNumber}
            className="shadow-2xl rounded-lg"
            renderTextLayer={true}
            renderAnnotationLayer={true}
            width={Math.min(window.innerWidth - 400, 900)}
          />
        </Document>
      </div>
    </div>
  );
};