import React, { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { HugeiconsIcon } from '@hugeicons/react';
import { ArrowLeft01Icon, ArrowRight01Icon, Download01Icon, ArrowLeftDoubleIcon, ArrowRightDoubleIcon } from '@hugeicons/core-free-icons';
import type { Presentation } from '@/types/api';
import { getFileUrl } from '@/utils/fileUrls';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import './SimplifiedDocumentViewer.css';

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
  const [cacheBuster, setCacheBuster] = useState(Date.now());

  useEffect(() => {
    setLoading(true);
    setError(null);
    setCacheBuster(Date.now());
    setPageNumber(1);
  }, [presentation.id, presentation.slides?.length]);

  const basePdfUrl = getFileUrl(presentation, 'pdf', { forPreview: true });
  const pdfUrl = basePdfUrl 
    ? `${basePdfUrl}${basePdfUrl.includes('?') ? '&' : '?'}t=${cacheBuster}` 
    : null;
  const pptxUrl = fileType === 'pptx' ? getFileUrl(presentation, 'pptx') : null;
  const texUrl = fileType !== 'pptx' ? getFileUrl(presentation, 'tex') : null;

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
        <p className="text-muted-foreground">No document available</p>
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col h-full bg-background', className)}>
      <div className="flex items-center justify-center gap-4 py-2">
        {numPages && numPages > 1 && (
          <>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handlePageChange(1)}
              disabled={pageNumber <= 1}
              title="First slide"
            >
              <HugeiconsIcon icon={ArrowLeftDoubleIcon} size={20} />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => handlePageChange(pageNumber - 1)}
              disabled={pageNumber <= 1}
              title="Previous slide"
            >
              <HugeiconsIcon icon={ArrowLeft01Icon} size={20} />
            </Button>

            <div className="text-foreground">
              <span className="font-medium">{pageNumber}</span>
              <span className="text-muted-foreground mx-2">/</span>
              <span className="text-muted-foreground">{numPages}</span>
            </div>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => handlePageChange(pageNumber + 1)}
              disabled={pageNumber >= numPages}
              title="Next slide"
            >
              <HugeiconsIcon icon={ArrowRight01Icon} size={20} />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => handlePageChange(numPages)}
              disabled={pageNumber >= numPages}
              title="Last slide"
            >
              <HugeiconsIcon icon={ArrowRightDoubleIcon} size={20} />
            </Button>
          </>
        )}

        <div className="flex gap-2 ml-4">
          {pptxUrl && (
            <Button
              asChild
              variant="outline"
              size="sm"
              className="border-border text-muted-foreground hover:text-foreground hover:bg-muted gap-1.5"
            >
              <a href={pptxUrl} download={`${presentation.main_topic}.pptx`}>
                <HugeiconsIcon icon={Download01Icon} size={14} />
                PPTX
              </a>
            </Button>
          )}
          <Button
            asChild
            variant="outline"
            size="sm"
            className="border-border text-muted-foreground hover:text-foreground hover:bg-muted gap-1.5"
          >
            <a href={pdfUrl} download={`${presentation.main_topic}.pdf`}>
              <HugeiconsIcon icon={Download01Icon} size={14} />
              PDF
            </a>
          </Button>
          {texUrl && (
            <Button
              asChild
              variant="outline"
              size="sm"
              className="border-border text-muted-foreground hover:text-foreground hover:bg-muted gap-1.5"
            >
              <a href={texUrl} download={`${presentation.main_topic}.tex`}>
                <HugeiconsIcon icon={Download01Icon} size={14} />
                TeX
              </a>
            </Button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-auto flex items-start justify-center pt-4">
        {loading && (
          <div className="text-muted-foreground pt-8">Loading document...</div>
        )}

        {error && (
          <div className="text-destructive pt-8 text-center px-4">
            {error}
            {pptxUrl && (
              <div className="mt-4">
                <Button
                  asChild
                  variant="outline"
                  className="border-border text-muted-foreground hover:text-foreground hover:bg-muted gap-2"
                >
                  <a href={pptxUrl} download={`${presentation.main_topic}.pptx`}>
                    <HugeiconsIcon icon={Download01Icon} size={18} />
                    Download PPTX Instead
                  </a>
                </Button>
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
            className="shadow-2xl rounded-md"
            renderTextLayer={true}
            renderAnnotationLayer={true}
            width={Math.min(window.innerWidth - 400, 900)}
          />
        </Document>
      </div>
    </div>
  );
};
