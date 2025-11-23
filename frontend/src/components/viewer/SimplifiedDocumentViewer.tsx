import React, { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, Download, ExitToApp } from '@mui/icons-material';
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

interface PPTXSlide {
  slide_number: number;
  title: string;
  content?: string[];
  image_base64?: string;
  width?: number;
  height?: number;
  notes?: string;
}

interface PPTXPreviewData {
  success: boolean;
  total_slides: number;
  slides: PPTXSlide[];
  presentation_width?: number;
  presentation_height?: number;
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
  const [pptxPreview, setPptxPreview] = useState<PPTXPreviewData | null>(null);
  const [currentPptxSlide, setCurrentPptxSlide] = useState(0);

  // Get file URL using utility
  const fileUrl = getFileUrl(presentation, fileType);

  // For PPTX files, we don't load slides as images anymore
  useEffect(() => {
    if (fileType === 'pptx') {
      setLoading(false);
    }
  }, [fileType]);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('Error loading document:', error);
    setError('Failed to load document');
    setLoading(false);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= (numPages || 1)) {
      setPageNumber(newPage);
      onPageChange?.(newPage);
    }
  };

  if (!fileUrl) {
    return (
      <div className={cn('flex items-center justify-center h-full', className)}>
        <p className="text-text-muted">No document available</p>
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col h-full bg-background', className)}>
      {/* Navigation controls at the top */}
      {numPages && numPages > 1 && (
        <div className="flex items-center justify-center gap-4">
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
        </div>
      )}

      {/* Document viewer */}
      <div className="flex-1 overflow-auto flex items-start justify-center pt-4">
        {loading && (
          <div className="text-text-muted pt-8">Loading document...</div>
        )}

        {error && (
          <div className="text-red-500 pt-8">{error}</div>
        )}

        {fileType === 'pdf' ? (
          <Document
            file={fileUrl}
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
        ) : (
          // Show PPTX download card
          <div className="flex items-center justify-center h-full p-8">
            <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full">
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 bg-gradient-to-br from-orange-400 to-red-500 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M15,18V16H8V18H15M15,14V12H8V14H15M13,9V3.5L18.5,9H13Z"/>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  {presentation.main_topic}
                </h3>
                <p className="text-gray-600 text-center mb-6">
                  PowerPoint Presentation
                </p>
                <a
                  href={fileUrl}
                  download={`${presentation.main_topic}.pptx`}
                  className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 transition-all transform hover:scale-105 flex items-center gap-2 font-medium shadow-md"
                >
                  <Download className="w-5 h-5" />
                  Download PPTX
                </a>
                <a
                  href={fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 text-blue-600 hover:text-blue-700 text-sm underline"
                >
                  Open in PowerPoint Online
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};